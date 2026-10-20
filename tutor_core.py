"""G. E. Moore: validácia zdrojov, lokálne vyhľadávanie a export.

Práca s korpusom nevyžaduje volanie externých API.
"""
from __future__ import annotations
import json
import math
import re
import unicodedata
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

MAX_TURNS = 20
RECORD_TYPES = {"paragraph", "heading", "note"}
RECORD_RE = re.compile(r"MOO-\d{2}-\d{4}")
TOKEN_RE = re.compile(r"[^\W_]+", re.UNICODE)
STOP = set("ako čo co alebo lebo teda kde kedy kto ktorý ktoré ktorá tento toto jeho jej som sme ste sú su bol bola byť byt mám mať mat vtedy preto medzi pred po pre pri do od z na si sa je ze že nie ani ale aby by iba možno možné má majú ak v tom to tak že i a o za či s vo na k ktorý ten nej zo ktorý že".split())

class CorpusError(ValueError):
    pass


def load_corpus(path: str | Path) -> dict:
    path = Path(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8-sig"))
    except FileNotFoundError as exc:
        raise CorpusError(f"Chýba súbor {path.name}.") from exc
    except json.JSONDecodeError as exc:
        raise CorpusError(f"Poškodený JSON: riadok {exc.lineno}, stĺpec {exc.colno}.") from exc
    if not isinstance(data, dict) or not isinstance(data.get("works"), list) or not isinstance(data.get("records"), list):
        raise CorpusError("Neočakávaný formát: očakáva sa objekt s works a records.")
    works = data["works"]
    rows = data["records"]
    if len(works) != 8:
        raise CorpusError(f"Očakáva sa 8 textov, nájdených {len(works)}.")
    work_ids = set()
    for w in works:
        if not isinstance(w, dict) or not isinstance(w.get("id"), str) or w["id"] in work_ids:
            raise CorpusError("Neplatné alebo duplicitné označenie štúdie.")
        if not isinstance(w.get("authors"), list) or not w["authors"] or not all(isinstance(a,str) and a.strip() for a in w["authors"]):
            raise CorpusError(f"Štúdia {w['id']} nemá uvedených autorov.")
        if not isinstance(w.get("title"), str) or not w["title"].strip():
            raise CorpusError(f"Štúdia {w['id']} nemá názov.")
        work_ids.add(w["id"])
    seen = set()
    for i, r in enumerate(rows, 1):
        rid = r.get("id") if isinstance(r,dict) else None
        if not isinstance(rid,str) or not RECORD_RE.fullmatch(rid) or rid in seen:
            raise CorpusError(f"Záznam {i} má neplatné/duplicitné ID: {rid}.")
        seen.add(rid)
        if r.get("work_id") not in work_ids or r.get("type") not in RECORD_TYPES:
            raise CorpusError(f"Záznam {rid} má neplatný typ alebo dielo.")
        if not isinstance(r.get("text"),str) or not r["text"].strip():
            raise CorpusError(f"Záznam {rid} nemá text.")
    # Všetky hlavné texty musia byť zastúpené.
    with_paragraphs = {r["work_id"] for r in rows if r["type"] == "paragraph"}
    if with_paragraphs != work_ids:
        raise CorpusError(f"Chýbajú odseky v dielach: {sorted(work_ids-with_paragraphs)}")
    # Originálne číslovanie paragrafov diela Principia Ethica (§ 1–135).
    nums = [r.get("paragraph_number") for r in rows
            if r.get("work_id") == "MOO-06" and r.get("type") == "heading"
            and r.get("heading_role") == "paragraph_number"]
    if nums != list(range(1,136)):
        raise CorpusError("Principia Ethica nemá úplnú postupnosť § 1–135.")
    expected_titles = ["Čo je filozofia?", "Dôkaz vonkajšieho sveta", "Istota",
                       "Obrana zdravého rozumu", "Povaha súdu", "Principia Ethica",
                       "Štyri podoby skepticizmu", "Vyvrátenie idealizmu"]
    if [w["title"] for w in works] != expected_titles:
        raise CorpusError("Texty sú neúplné alebo v nesprávnom poradí.")
    return data


def all_authors(data: dict) -> list[str]:
    return list(dict.fromkeys(author for w in data["works"] for author in w["authors"]))


def filtered_works(data: dict, author: str | None = None) -> list[dict]:
    return [w for w in data["works"] if author is None or author in w["authors"]]


def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", str(text).casefold())
    return "".join(c for c in text if not unicodedata.combining(c))


def terms(text: str) -> list[str]:
    return [x for x in TOKEN_RE.findall(normalize(text)) if len(x) > 2 and x not in STOP]


def source_label(record: dict) -> str:
    bits = [record["author"], f"„{record['work_title']}“"]
    if record.get("chapter"):
        bits.append("kapitola/časť " + str(record["chapter"]))
    if record.get("subchapter") and str(record["subchapter"]).startswith("§"):
        bits.append(str(record["subchapter"]))
    if record.get("page") is not None:
        bits.append("strana " + str(record["page"]))
    bits.append("interné ID " + record["id"])
    return " · ".join(bits)


class PassageIndex:
    """Lokálne BM25-podobné vyhľadávanie; nepoužíva web ani API."""
    def __init__(self, data: dict):
        self.rows = [r for r in data["records"] if r["type"] == "paragraph"]
        self.by_id = {r["id"]: i for i,r in enumerate(self.rows)}
        self.docs = [Counter(terms(" ".join([r["text"], r["work_title"],
                                              str(r.get("chapter") or ""), str(r.get("subchapter") or ""), r["author"]]))) for r in self.rows]
        self.df = Counter(t for doc in self.docs for t in doc)
        self.length = [sum(doc.values()) for doc in self.docs]
        self.avglen = sum(self.length) / max(1,len(self.length))

    def find(self, query: str, *, work_ids: set[str] | None = None, focus_id: str | None = None,
             limit: int = 10) -> list[dict]:
        q = set(terms(query))
        n = len(self.rows)
        scored = []
        for i, r in enumerate(self.rows):
            if work_ids is not None and r["work_id"] not in work_ids:
                continue
            doc = self.docs[i]
            score = 0.0
            for t in q:
                if t in doc:
                    tf = doc[t]
                    idf = math.log(1+(n-self.df[t]+.5)/(self.df[t]+.5))
                    score += idf * (tf*2.2)/(tf + 1.2*(.25+.75*self.length[i]/max(1,self.avglen)))
            if focus_id == r["id"]:
                score += 1000
            if r["id"].casefold() in query.casefold():
                score += 100
            if score > 0:
                scored.append((score,i))
        matches = [i for _,i in sorted(scored,key=lambda x:(-x[0],x[1]))[:limit]]
        if focus_id in self.by_id:
            pos = self.by_id[focus_id]
            row = self.rows[pos]
            if work_ids is None or row["work_id"] in work_ids:
                near = [j for j in (pos,pos-1,pos+1) if 0 <= j < n and self.rows[j]["work_id"] == row["work_id"]]
                matches = list(dict.fromkeys(near+matches))[:limit]
        return [self.rows[i] for i in matches]


def evidence(index: PassageIndex, query: str, *, work_ids: set[str] | None = None,
             focus_id: str | None = None, limit: int = 9, char_budget: int = 12500) -> str:
    rows = index.find(query,work_ids=work_ids,focus_id=focus_id,limit=limit)
    if not rows:
        return "Žiadny spoľahlivo relevantný úryvok sa nenašiel. Neodvodzuj odpoveď z pamäti."
    chunks = []
    free = char_budget
    for r in rows:
        header = "[ZDROJ: " + source_label(r) + "; typ=" + r["type"] + "]\n"
        cap = 3500 if r["id"] == focus_id else 1500
        budget = min(cap,free-len(header)-50)
        if budget < 100: break
        excerpt = r["text"]
        if len(excerpt) > budget:
            excerpt = excerpt[:budget].rsplit(" ",1)[0] + " […] [skrátené]"
        chunk = header + excerpt
        chunks.append(chunk)
        free -= len(chunk)+2
    return "\n\n".join(chunks) + "\n\nPozor: ID MOO-xx-yyyy je technické; predložené slovenské preklady neboli overené podľa anglického originálu."


def api_error(exc: Exception, model: str) -> str:
    msg = str(exc).lower()
    code = getattr(exc,'code',None)
    if code == 429 or "429" in msg or "resource_exhausted" in msg:
        return f"Pre model {model} nie je dostupná kvóta Gemini (429). Skontrolujte Google AI Studio; skúste neskôr."
    if code == 503 or "503" in msg or "service_unavailable" in msg:
        return "Gemini je dočasne nedostupné (503). Skúste zopakovať otázku neskôr."
    if code == 404 or "404" in msg or "not_found" in msg:
        return f"Model {model} nie je prístupný (404). Skontrolujte nastavenie GEMINI_MODEL."
    if code in (401,403) or "401" in msg or "403" in msg:
        return "Gemini odmietlo prístup (401/403). Skontrolujte API kľúč a oprávnenia projektu."
    if "timeout" in msg or "timed out" in msg:
        return "Odpoveď Gemini sa nestihla načítať (ReadTimeout). Skúste znova; otázka sa nezapočítala."
    return f"Požiadavku sa nepodarilo dokončiť ({type(exc).__name__}). Podrobnosti sú v serverových logoch."


def transcript(messages: list[dict], name: str, scope: str, model: str, session_id: str,
               when: datetime | None = None) -> str:
    when = when or datetime.now(ZoneInfo('Europe/Bratislava'))
    result = ["G. E. MOORE – 20-KROKOVÝ FILOZOFICKÝ DIALÓG", "="*54,
              "Študent/ka: "+(name.strip() or '(neuvedené)'),
              "Dátum: "+when.strftime('%d. %m. %Y %H:%M %Z'),
              "Rozsah: "+scope, "Model: "+model, "Relácia: "+session_id,
              f"Počet vstupov: {sum(m['role']=='user' for m in messages)}/{MAX_TURNS}","", "PREPIS", "="*54, ""]
    for m in messages:
        result.extend(["ŠTUDENT:" if m["role"]=="user" else "AI TÚTOR:",m["content"],""])
    return "\n".join(result)
