# AI tútor: George Edward Moore

Samostatná aplikácia Streamlit pre osem slovenských textov G. E. Moora. Je nezávislá od predchádzajúcich projektov `ai-tutor-tractatus`, `ai-tutor-frege` a ďalších.

## Obsah korpusu

V hlavnom rozbaľovacom menu je presne osem položiek v poradí dodaných príloh:

1. **Čo je filozofia?** (prvá kapitola *Some Main Problems of Philosophy*, nie celé dielo)
2. **Dôkaz vonkajšieho sveta**
3. **Istota**
4. **Obrana zdravého rozumu** (pôvodné oddiely I–V)
5. **Povaha súdu**
6. **Principia Ethica** (predhovor, kapitoly I–VI, všetky pôvodné paragrafy § 1–135)
7. **Štyri podoby skepticizmu**
8. **Vyvrátenie idealizmu**

Použitý súbor `moore_texty.json` má 940 záznamov: 766 textových odsekov, 153 štruktúrnych nadpisov a 21 poznámok. Poznámky sú v čítačke vizuálne oddelené; nie sú pokladané za autorovo primárne tvrdenie pri vyhľadávaní podkladov pre AI.

## Funkcie

- Výber jedného z ôsmich textov.
- Vlastná čítačka s nezávislým posuvníkom; tlačidlá **Na začiatok** a **Na koniec**.
- Navigácia po kapitolách a častiach; pri *Principia Ethica* aj osobitný rozbaľovací výber § 1–135.
- Vyhľadávanie bez ohľadu na slovenskú diakritiku; šípky označujú vždy **jeden aktuálny nález**.
- Kliknutím na každý textový odsek sa pripraví samostatný analytický výklad (nezapočítava sa do 20 diskusných krokov).
- Sokratovský dialóg na najviac **20 študentských vstupov**. Rozsah sa uzamkne pri prvej úspešnej otázke: buď jeden text, alebo celý korpus.
- Kritické zhodnotenie 20. vstupu a úplný export konverzácie do TXT.
- Pri chybe 429/503/ReadTimeout sa otázka automaticky nezapočíta, zostáva pripravená na ručné opakovanie. Nespoliehajte sa na automatické opakované volania API.

## Súbory projektu

```
app.py                  # Streamlit aplikácia
book_reader.py          # HTML/CSS/JS čítačka cez Streamlit custom component v2
tutor_core.py           # Kontroly korpusu, lokálne vyhľadávanie a export
moore_texty.json        # Textový korpus ôsmich diel
requirements.txt        # Knižnice aplikácie
.streamlit/secrets.toml.example  # Vzor nastavenia (bez skutočného hesla)
.gitignore
POZNAMKY_K_TEXTOM.md
README.md
tests/test_core.py
tests/test_reader_browser.py
```

## Nasadenie cez GitHub a Streamlit Community Cloud

1. Vytvorte nový repozitár **`ai-tutor-moore`**. Súbory musia byť priamo v koreni repozitára (nie vo vnorenom priečinku).
2. Na [share.streamlit.io](https://share.streamlit.io/) zvoľte **Create app**, GitHub repozitár a ako **Main file path** určite `app.py`.
3. Otvorte správu aplikácie a v **Settings → Secrets** doplňte:

```toml
GEMINI_API_KEY = "SEM_DOSADTE_SVOJ_API_KLUC"
GEMINI_MODEL = "gemini-3.5-flash-lite"
GEMINI_TIMEOUT_MS = 120000
```

Skutočný kľúč nevkladajte do GitHubu ani do chatu. Model je možné zmeniť na ktorýkoľvek podporovaný model dostupný pre váš Google projekt; vyššie uvedený je predvolený. Kvóty RPM/TPM/RPD sa pri viacerých tútoroch pod jedným Google projektom zdieľajú. Ak ste pri inej aplikácii nastavili Secrets, treba ich nastaviť samostatne aj tu.

4. Po uložení Secrets obnovte alebo reštartujte aplikáciu. Navrhovaný názov URL: `ai-tutor-moore.streamlit.app` (podľa dostupnosti).
5. Najprv skontrolujte zobrazenie ôsmich diel a navigáciu *Principia Ethica*; potom skúste krátky výklad odseku a jednu otázku do dialógu.

## Lokálne spustenie

Potrebný je Python 3.11 alebo novší.

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Pri lokálnom používaní doplňte súkromný `.streamlit/secrets.toml` (ignorovaný Gitom) alebo premennú prostredia `GEMINI_API_KEY`.

## Automatizované testy

```bash
python -m unittest discover -s tests -p 'test_core.py' -v
```

Pre samostatný test čítačky treba dodatočne nainštalovať Playwright a mať dostupný Chromium:

```bash
python -m pip install playwright
python -m playwright install chromium
python tests/test_reader_browser.py
```

Posledný test štandardne používa lokálne Chromium na ceste `/usr/bin/chromium`; ak sa nachádza inde, upravte `executable_path` v teste (alebo vynechajte tento argument). Playwright nie je závislosťou Streamlit nasadenia a nepatrí do `requirements.txt`.

## Metodologické a právne obmedzenia

- Korpus vznikol z ôsmich **poskytnutých slovenských dokumentov Word**. Pravdivosť prekladu sa neoverovala podľa anglických originálov.
- Nie každé dielo v korpuse je samostatná kniha; *Čo je filozofia?* je iba prvou kapitolou väčšej publikácie.
- Pri *Principia Ethica* sú pôvodné čísla paragrafov 1–135. Označenia `MOO-06-....` sú iba **technické identifikátory záznamov**.
- V zdrojovom JSON nie sú dôveryhodné tlačené čísla strán; AI ich nesmie vymýšľať.
- AI odpovedá na základe lokálne vyhľadaných textových podkladov. Je inštruovaná nepoužívať iné zdroje, no jazykový model môže urobiť chybu. Jeho interpretácie a citácie treba kontrolovať.
- **Úplné preklady nesprístupňujte cez verejný GitHub ani verejne nasadenú aplikáciu bez vyjasnených autorských práv a príslušného oprávnenia.** Ak také oprávnenie nie je zabezpečené, použite súkromné nasadenie s vhodnými prístupovými obmedzeniami.
