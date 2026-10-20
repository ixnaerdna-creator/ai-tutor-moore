"""Klikateľná čítačka textov s jediným posuvným panelom.

Komponent Streamlit v2: HTML/CSS/JS sa vykonávajú na strane prehliadača.
Do Pythonu odosiela iba ID kliknutého odseku a identifikátor kliknutia.
"""
import streamlit as st

READER_HTML = """
<div class="moo-shell" lang="sk">
  <div class="moo-tools">
    <input type="search" id="moo-search" placeholder="Hľadať v texte…" aria-label="Vyhľadávanie v štúdii" autocomplete="off" />
    <button type="button" id="moo-prev" aria-label="Predchádzajúci nález" title="Predchádzajúci nález">↑</button>
    <button type="button" id="moo-next" aria-label="Nasledujúci nález" title="Nasledujúci nález">↓</button>
    <select id="moo-chapters" aria-label="Prejsť na kapitolu alebo oddiel"></select>
    <select id="moo-paragraphs" aria-label="Prejsť na paragraf" hidden></select>
    <button type="button" id="moo-start">Na začiatok</button>
    <button type="button" id="moo-end-btn">Na koniec</button>
  </div>
  <div class="moo-context" aria-live="polite">
    <span id="moo-current"></span>
    <span id="moo-found"></span>
  </div>
  <div class="moo-scroll" id="moo-scroll" tabindex="0" aria-label="Posuvný text vybranej štúdie">
    <div id="moo-text"></div>
    <div id="moo-bottom">Koniec vybraného textu</div>
  </div>
</div>
"""

READER_CSS = r"""
:host { display:block; width:100%; height:780px; }
*, *::before, *::after { box-sizing:border-box; }
.moo-shell { height:780px; max-height:780px; min-height:780px; width:100%; overflow:hidden;
  display:flex; flex-direction:column; color:var(--st-text-color,#222);
  font-family:Georgia,'Times New Roman',serif; }
.moo-tools { display:flex; flex:0 0 auto; flex-wrap:wrap; align-items:center;
  gap:6px; padding:5px 0 9px; font:12px system-ui,sans-serif; }
.moo-tools input, .moo-tools select { border:1px solid #9daab5; border-radius:5px;
  color:var(--st-text-color,#222); background:var(--st-background-color,#fff);
  padding:7px 8px; font:13px system-ui,sans-serif; min-height:35px; }
.moo-tools input {flex:2 1 170px; min-width:130px;}
.moo-tools select {flex:1 1 130px; min-width:120px; max-width:260px;}
.moo-tools button {border:1px solid #aab4bf; color:var(--st-text-color,#222);
  background:var(--st-background-color,#fff); border-radius:5px; cursor:pointer;
  padding:7px 9px; min-height:35px; font:12px system-ui,sans-serif; white-space:nowrap;}
.moo-tools button:hover {background:#e7edf3; color:#222;}
.moo-tools button:focus-visible, .moo-tools select:focus-visible, .moo-tools input:focus-visible {
  outline:2px solid #3779b6; outline-offset:1px;}
.moo-context {flex:0 0 auto; display:flex; justify-content:space-between; gap:8px; min-height:26px;
  color:var(--st-text-color,#555); opacity:.8; font:12px/1.3 system-ui,sans-serif;
  padding:0 4px 7px;}
#moo-current {max-width:70%; overflow:hidden; white-space:nowrap; text-overflow:ellipsis;}
#moo-found {flex:0 0 auto; white-space:nowrap;}
.moo-scroll { flex:1 1 0; min-height:0; overflow-y:auto; overflow-x:hidden;
  scrollbar-width:auto; scrollbar-color:#59636e #e7eaef; scrollbar-gutter:stable;
  overscroll-behavior:contain; border-top:1px solid #d9dfe4;
  scroll-behavior:auto; }
.moo-scroll::-webkit-scrollbar {width:16px;}
.moo-scroll::-webkit-scrollbar-track {background:#e7eaef;}
.moo-scroll::-webkit-scrollbar-thumb {background:#59636e; border:3px solid #e7eaef; border-radius:9px;}
#moo-text {padding:12px 12px 4px 0;}
.moo-heading {font:700 21px/1.4 Georgia,serif; margin:22px 0 14px;
  padding:0 0 9px; border-bottom:1px solid #bdc7d0; color:var(--st-text-color,#222);}
.moo-heading:first-child {margin-top:0;}
.moo-section-number {font-size:17px; margin:17px 0 7px; padding-bottom:3px; border-bottom:0;}
.moo-continuation-heading,.moo-notes-heading {font-size:15px; opacity:.75;}
.moo-paragraph {display:block; width:100%; white-space:normal; text-align:left;
  background:transparent; color:var(--st-text-color,#222); border:0;
  border-left:3px solid transparent; padding:7px 9px 12px 10px; margin:0 0 7px;
  cursor:pointer; overflow-wrap:break-word;
  font:18px/1.55 Georgia,'Times New Roman',serif; border-radius:2px;}
.moo-paragraph:hover {background:#edf4f9;}
.moo-paragraph:focus-visible {outline:2px solid #3876ab; outline-offset:-2px;}
.moo-paragraph.moo-selected {border-left-color:#4a82ae; background:#edf5fc;}
.moo-paragraph.moo-hit {border-left-color:#ae7700; background:#ffecac; color:#272019;}
.moo-location {display:block; color:#6b7480; margin-bottom:3px; font:11px/1.35 system-ui,sans-serif;}
.moo-paragraph.moo-hit .moo-location {color:#735000;}
.moo-picture {margin:10px 8px 20px; padding:10px; border:1px solid #aab7c2; border-radius:6px; max-width:100%;}
.moo-picture img {display:block; max-width:100%; height:auto; margin:0 auto;}
.moo-picture figcaption {font:12px/1.45 system-ui,sans-serif; color:var(--st-text-color,#444); padding:9px 2px 0;}
.moo-formula {font-family:'Cambria Math',Georgia,serif; background:rgba(125,125,125,.04);}
.moo-tablebutton {overflow-x:auto;}
.moo-real-table {border-collapse:collapse; font:14px/1.4 Georgia,serif; width:100%; min-width:450px;}
.moo-real-table th,.moo-real-table td {border:1px solid #aab7c2; padding:7px; text-align:left; vertical-align:top; white-space:pre-wrap;}
.moo-real-table th {font-weight:bold; background:rgba(125,125,125,.13);}
.moo-note {font:14px/1.45 Georgia,serif; padding:4px 10px; margin:8px 0;
  border-left:2px solid #aeb7c2; opacity:.78;}
#moo-bottom {padding:18px 8px 30px; margin:22px 0 0;
  border-top:1px solid #b9c1cb; color:var(--st-text-color,#555);
  font:13px system-ui,sans-serif;}
@media(max-width:700px){.moo-paragraph{font-size:16px;} .moo-tools button{padding:6px 7px;}}
"""

READER_JS = r"""
export default function({parentElement, data, setTriggerValue}) {
  const root=parentElement.querySelector('.moo-shell');
  const scroll=root.querySelector('#moo-scroll');
  const content=root.querySelector('#moo-text');
  const searchInput=root.querySelector('#moo-search');
  const chapterList=root.querySelector('#moo-chapters');
  const paragraphList=root.querySelector('#moo-paragraphs');
  const prev=root.querySelector('#moo-prev');
  const next=root.querySelector('#moo-next');
  const first=root.querySelector('#moo-start');
  const last=root.querySelector('#moo-end-btn');
  const found=root.querySelector('#moo-found');
  const current=root.querySelector('#moo-current');
  const rows=Array.isArray(data?.paragraphs)?data.paragraphs:[];
  const storageKey='moo.reader.v1.'+(data?.bookKey||'default');
  const normalized=s=>String(s??'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const entries=[], sections=[], paragraphSections=[];
  const fragment=document.createDocumentFragment();
  let hits=[], hitIndex=0, initialized=false, clickNumber=0;
  let rememberedScroll=0, rememberedSearch='';
  try {
    rememberedScroll=Number(sessionStorage.getItem(storageKey+'.scroll'))||0;
    rememberedSearch=sessionStorage.getItem(storageKey+'.search')||'';
  } catch(_) {}

  for (const row of rows) {
    if (row.type==='heading') {
      const h=document.createElement('h3');
      h.className='moo-heading'; h.textContent=row.text;
      fragment.appendChild(h);
      if(row.heading_role==='paragraph_number') {
        paragraphSections.push({number:row.paragraph_number,el:h});
        h.classList.add('moo-section-number');
      } else if(row.heading_role==='chapter'||row.heading_role==='part') {
        sections.push({label:row.text,el:h});
      } else if (row.heading_role==='notes') {
        h.classList.add('moo-notes-heading');
      } else if (row.heading_role==='continuation') {
        h.classList.add('moo-continuation-heading');
      }
      continue;
    }
    if (row.type==='note') {
      const note=document.createElement('div');
      note.className='moo-note';
      const kind=row.note_origin==='author'?'Autorova poznámka':
        row.note_origin==='editor'?'Redakčná poznámka':'Poznámka / bibliografický údaj';
      note.textContent=kind+' — '+row.text;
      fragment.appendChild(note);
      continue;
    }
    if (row.type==='image') {
      const visual=(data?.visuals||[]).find(v=>v.id===row.visual_id);
      const box=document.createElement('figure'); box.className='moo-picture';
      if (visual && visual.image_base64) {
        const img=document.createElement('img');
        img.src='data:image/png;base64,'+visual.image_base64;
        img.alt=visual.description_sk||row.text;
        img.loading='lazy'; box.appendChild(img);
      }
      const caption=document.createElement('figcaption');
      caption.textContent='Obrazová príloha – '+(visual?.description_sk||row.text);
      box.appendChild(caption); fragment.appendChild(box);
      continue;
    }
    if (!['paragraph','formula','table'].includes(row.type)) continue;
    const p=document.createElement('button');
    p.type='button';
    p.className='moo-paragraph'+(row.id===data?.selected?' moo-selected':'')+(row.type==='formula'?' moo-formula':'')+(row.type==='table'?' moo-tablebutton':'');
    p.setAttribute('aria-label','Otvoriť výklad '+row.id);
    const place=document.createElement('span'); place.className='moo-location';
    const placeParts=[];
    if (row.page!=null) placeParts.push('strana '+row.page);
    if (row.chapter) placeParts.push(row.chapter);
    if (row.subchapter && String(row.subchapter).startsWith('§')) placeParts.push(row.subchapter);
    place.textContent=placeParts.join(' · ');
    const body=document.createElement('span');
    if (row.type==='table' && Array.isArray(row.table_rows)) {
       const table=document.createElement('table'); table.className='moo-real-table';
       for (const [n, cells] of row.table_rows.entries()) {
         const tr=document.createElement('tr');
         for (const cell of cells) {
           const item=document.createElement(n===0?'th':'td');
           item.textContent=String(cell); tr.appendChild(item);
         }
         table.appendChild(tr);
       }
       body.appendChild(table);
    } else { body.textContent=row.text; }
    p.append(place,body);
    p.addEventListener('click',()=>{
      for(const n of entries) n.el.classList.toggle('moo-selected',n.id===row.id);
      remember(); setTriggerValue('selected', {id:row.id, nonce:Date.now()+'-'+(++clickNumber)});
    });
    fragment.appendChild(p);
    entries.push({id:row.id,el:p,searchable:normalized(
      [row.id,row.text].join(' '))});
  }
  content.replaceChildren(fragment);

  const topMax=()=>Math.max(0,scroll.scrollHeight-scroll.clientHeight);
  function remember() {
    if (!initialized) return;
    try {sessionStorage.setItem(storageKey+'.scroll',String(scroll.scrollTop));}catch(_){}
  }
  function jump(position) {
    scroll.scrollTop=Math.max(0,Math.min(topMax(),position));
    remember(); updateCurrent();
  }
  function reveal(node) {
    const diff=node.getBoundingClientRect().top-scroll.getBoundingClientRect().top;
    jump(scroll.scrollTop+diff-14);
  }
  function updateCurrent() {
    let label=sections.length?sections[0].label:'';
    const threshold=scroll.getBoundingClientRect().top+32;
    for(const section of sections) {
      if(section.el.getBoundingClientRect().top<=threshold) label=section.label;
      else break;
    }
    const firstVisible=entries.find(e=>e.el.getBoundingClientRect().bottom>scroll.getBoundingClientRect().top+12);
    if (firstVisible) { const foundPage=firstVisible.el.querySelector('.moo-location')?.textContent||'';
      current.textContent=[label,foundPage].filter(Boolean).join(' · ');
    } else current.textContent=label;
  }
  function highlight() {
    for(const entry of entries) entry.el.classList.remove('moo-hit');
    if(!hits.length) {found.textContent=searchInput.value.trim()?'Bez nálezov':'';return;}
    const chosen=entries[hits[hitIndex]];
    chosen.el.classList.add('moo-hit');
    found.textContent=`Nález ${hitIndex+1} z ${hits.length} · ${chosen.id}`;
  }
  function runSearch(jumpToFirst=false) {
    const q=normalized(searchInput.value.trim());
    hits=[];
    if(q) entries.forEach((n,i)=>{if(n.searchable.includes(q))hits.push(i)});
    hitIndex=0;
    highlight();
    try {sessionStorage.setItem(storageKey+'.search',searchInput.value)}catch(_){}
    if(jumpToFirst&&hits.length)reveal(entries[hits[0]].el);
  }
  function nextHit(delta) {
    if(!hits.length)return;
    hitIndex=(hitIndex+delta+hits.length)%hits.length;
    highlight(); reveal(entries[hits[hitIndex]].el);
  }
  chapterList.replaceChildren();
  const beginning=document.createElement('option');
  beginning.value='top'; beginning.textContent='Začiatok textu'; chapterList.appendChild(beginning);
  sections.forEach((section,i)=>{
    const option=document.createElement('option');
    option.value=String(i); option.textContent=section.label;
    chapterList.appendChild(option);
  });

  chapterList.disabled=sections.length===0;
  paragraphList.hidden=paragraphSections.length===0;
  paragraphList.replaceChildren();
  if (paragraphSections.length) {
    const initial=document.createElement('option'); initial.value='';
    initial.textContent='Prejsť na § 1–135'; paragraphList.appendChild(initial);
    paragraphSections.forEach((item,i)=>{
      const option=document.createElement('option'); option.value=String(i);
      option.textContent='§ '+item.number; paragraphList.appendChild(option);
    });
  }
  const onChapter=()=>{
    const value=chapterList.value;
    if(value==='top')jump(0);
    else if(sections[Number(value)])reveal(sections[Number(value)].el);
  };
  const onParagraph=()=>{
    const value=paragraphList.value;
    if(value!==''&&paragraphSections[Number(value)])reveal(paragraphSections[Number(value)].el);
  };
  const onInput=()=>runSearch(true);
  const onSearchKey=e=>{
    if(e.key==='ArrowDown'||e.key==='Enter'){e.preventDefault();nextHit(1);}
    if(e.key==='ArrowUp'){e.preventDefault();nextHit(-1);}
  };
  const onPrev=()=>nextHit(-1), onNext=()=>nextHit(1);
  const onFirst=()=>jump(0), onLast=()=>jump(scroll.scrollHeight);
  const onScroll=()=>{remember(); updateCurrent();};
  searchInput.value=rememberedSearch;
  runSearch(false);
  chapterList.addEventListener('change',onChapter);
  paragraphList.addEventListener('change',onParagraph);
  searchInput.addEventListener('input',onInput);
  searchInput.addEventListener('keydown',onSearchKey);
  prev.addEventListener('click',onPrev);
  next.addEventListener('click',onNext);
  first.addEventListener('click',onFirst);
  last.addEventListener('click',onLast);
  scroll.addEventListener('scroll',onScroll,{passive:true});
  jump(rememberedScroll);
  initialized=true;
  updateCurrent();
  return ()=>{
    chapterList.removeEventListener('change',onChapter);
    paragraphList.removeEventListener('change',onParagraph);
    searchInput.removeEventListener('input',onInput);
    searchInput.removeEventListener('keydown',onSearchKey);
    prev.removeEventListener('click',onPrev);
    next.removeEventListener('click',onNext);
    first.removeEventListener('click',onFirst);
    last.removeEventListener('click',onLast);
    scroll.removeEventListener('scroll',onScroll);
  };
}
"""

book_reader = st.components.v2.component(
    name="moore_text_reader_v1", html=READER_HTML,
    css=READER_CSS, js=READER_JS, isolate_styles=True,
)
