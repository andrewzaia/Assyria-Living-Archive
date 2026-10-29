(() => {
  'use strict';
  const $ = (s, root=document) => root.querySelector(s);
  const $$ = (s, root=document) => [...root.querySelectorAll(s)];
  const BASE = $('meta[name="site-base-path"]')?.content || '';
  const KEY = 'assyria-reading-v1' + BASE;
  let saved=[];
  try { const value=JSON.parse(localStorage.getItem(KEY)||'[]'); if(Array.isArray(value)) saved=value.filter(x=>typeof x==='string'); } catch {}
  let catalogue;
  const getData = () => catalogue ||= fetch(BASE + '/catalogue.json').then(r=>{if(!r.ok)throw Error('Catalogue unavailable');return r.json();});
  const esc = s => String(s).replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const notify = text => { const el=$('#toast');el.textContent=text;el.classList.add('visible');clearTimeout(el.timer);el.timer=setTimeout(()=>el.classList.remove('visible'),2400); };
  const syncSaved = () => {
    $$('[data-save]').forEach(b=>{const active=saved.includes(b.dataset.save);b.setAttribute('aria-pressed',String(active));const t=$('span',b);if(t)t.textContent=active?'Saved article':'Save article';if(b.classList.contains('small-save'))b.setAttribute('aria-label',(active?'Unsave ':'Save ')+b.closest('.article-card').querySelector('h3').textContent);});
    $$('.saved-count').forEach(el=>{el.textContent=saved.length;el.hidden=!saved.length;});
  };
  const storeSaved = () => {try{localStorage.setItem(KEY,JSON.stringify(saved));return true;}catch{notify('Browser storage is unavailable. Saved for this visit only.');return false;}};
  const saveIcon='<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M6 3h12v18l-6-4-6 4Z"/></svg>';
  const arrow='<svg class="icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M4 12h15m-6-6 6 6-6 6"/></svg>';
  const makeCard = a => `<article class="article-card"><a class="card-main" href="${BASE}/articles/${esc(a.slug)}/"><span class="eyebrow">${esc(a.category)}</span><h3>${esc(a.title)}</h3><p>${esc(a.summary)}</p><span class="card-meta">${a.kind === 'preserved_reference' ? 'Preserved reference' : 'Editorial guide'} ${arrow}</span></a><button class="save small-save" data-save="${esc(a.slug)}" aria-label="Unsave ${esc(a.title)}" aria-pressed="true">${saveIcon}</button></article>`;
  const renderReading = async () => {
    if(!$('#reading-grid'))return;
    try{const {articles}=await getData();const list=articles.filter(a=>saved.includes(a.slug));$('#reading-grid').innerHTML=list.map(makeCard).join('');$('#reading-empty').hidden=!!list.length;$('#reading-count').textContent=`${list.length} saved article${list.length===1?'':'s'}`;$('#clear-saved').hidden=!list.length;syncSaved();}
    catch{$('#reading-count').textContent='The catalogue could not load. Refresh to try again.';}
  };
  document.addEventListener('click',e=>{
    const b=e.target.closest('[data-save]');if(!b)return;
    const id=b.dataset.save;const active=saved.includes(id);saved=active?saved.filter(x=>x!==id):[...saved,id];
    const persisted=storeSaved();syncSaved();renderReading();if(persisted)notify(active?'Removed from your reading list':'Saved to your reading list');
  });
  $('#clear-saved')?.addEventListener('click',()=>{saved=[];storeSaved();syncSaved();renderReading();notify('Reading list cleared');});
  syncSaved();renderReading();
  window.addEventListener('storage',e=>{if(e.key===KEY){try{const v=JSON.parse(e.newValue||'[]');saved=Array.isArray(v)?v.filter(x=>typeof x==='string'):[];syncSaved();renderReading();}catch{}}});
  const menu=$('.menu-toggle');menu?.addEventListener('click',()=>{const nav=$('.mobile-nav');nav.hidden=!nav.hidden;menu.setAttribute('aria-expanded',String(!nav.hidden));menu.setAttribute('aria-label',nav.hidden?'Open navigation':'Close navigation');});

  const dialog=$('#search-dialog');let searchVersion=0;
  const searchGlobal=async()=>{
    const version=++searchVersion;const q=$('#global-search').value.trim().toLocaleLowerCase();
    $('#search-results').innerHTML='';
    if(!q){$('#search-status').textContent='Search titles, topics and article text.';return;}
    $('#search-status').textContent='Searching the archive...';
    try{const {articles}=await getData();if(version!==searchVersion)return;
      const words=q.split(/\s+/);const found=articles.filter(a=>{const t=[a.title,a.summary,a.category,...a.sections.map(s=>s.title+' '+s.text)].join(' ').toLocaleLowerCase();return words.every(w=>t.includes(w));}).sort((a,b)=>Number(b.title.toLowerCase().includes(q))-Number(a.title.toLowerCase().includes(q)));
      $('#search-status').textContent=found.length?`${found.length} matching article${found.length===1?'':'s'}`:'No matches yet. Try a broader term, a place or a language.';
      $('#search-results').innerHTML=found.map(a=>`<a href="${BASE}/articles/${esc(a.slug)}/"><span class="eyebrow">${esc(a.category)}</span><h3>${esc(a.title)}</h3><p>${esc(a.summary)}</p></a>`).join('');
    }catch{if(version===searchVersion)$('#search-status').textContent='The search catalogue could not load. Please try again.';}
  };
  $$('.search-open').forEach(b=>b.addEventListener('click',()=>{dialog.showModal();$('#global-search').focus();}));
  $('.search-close')?.addEventListener('click',()=>dialog.close());
  dialog?.addEventListener('click',e=>{if(e.target===dialog){const r=dialog.getBoundingClientRect();if(e.clientX<r.left||e.clientX>r.right||e.clientY<r.top||e.clientY>r.bottom)dialog.close();}});
  $('#global-search')?.addEventListener('input',searchGlobal);
  document.addEventListener('keydown',e=>{if((e.metaKey||e.ctrlKey)&&e.key.toLowerCase()==='k'){e.preventDefault();if(!dialog.open)dialog.showModal();$('#global-search').focus();}});

  if($('#article-grid')){
    const cards=$$('.article-card',$('#article-grid'));let topic='all';let cats=[];
    const params=new URLSearchParams(location.search);const requested=params.get('topic');
    const apply=()=>{
      const q=$('#article-search').value.trim().toLowerCase();let count=0;
      cards.forEach(c=>{c.hidden=!(topic==='all'||c.dataset.category===cats[Number(topic)])||!q.split(/\s+/).every(w=>c.dataset.search.includes(w));if(!c.hidden)count++;});
      $('#result-count').textContent=`${count} introduction${count===1?'':'s'}`;$('#no-results').hidden=!!count;
      $$('.chip[data-topic]').forEach(b=>{const active=b.dataset.topic===topic;b.classList.toggle('active',active);b.setAttribute('aria-pressed',String(active));});
    };
    // Category labels are rendered in the same order as the catalogue.
    cats=$$('.chip[data-topic]').slice(1).map(b=>b.textContent);
    if(requested!==null&&/^\d+$/.test(requested)&&Number(requested)<cats.length)topic=requested;
    $$('.chip[data-topic]').forEach(b=>b.addEventListener('click',()=>{topic=b.dataset.topic;const u=new URL(location);if(topic==='all')u.searchParams.delete('topic');else u.searchParams.set('topic',topic);history.replaceState(null,'',u);apply();}));
    $('#article-search').addEventListener('input',apply);
    $('#sort').addEventListener('change',()=>{const ordered=$('#sort').value==='az'?[...cards].sort((a,b)=>$('h3',a).textContent.localeCompare($('h3',b).textContent)):cards;ordered.forEach(c=>$('#article-grid').appendChild(c));});
    $('#clear-filters').addEventListener('click',()=>{topic='all';$('#article-search').value='';const u=new URL(location);u.searchParams.delete('topic');history.replaceState(null,'',u);apply();});
    apply();
  }
  const sourceSearch=$('#source-search');sourceSearch?.addEventListener('input',()=>{const words=sourceSearch.value.trim().toLowerCase().split(/\s+/);let n=0;$$('[data-source-search]').forEach(s=>{s.hidden=!words.every(w=>s.dataset.sourceSearch.includes(w));if(!s.hidden)n++;});$('#source-count').textContent=`Showing ${n} source record${n===1?'':'s'}`;$('#source-empty').hidden=!!n;});
  $$('[data-era-filter]').forEach(b=>b.addEventListener('click',()=>{let n=0;$$('[data-era]').forEach(el=>{el.hidden=b.dataset.eraFilter!=='all'&&el.dataset.era!==b.dataset.eraFilter;if(!el.hidden)n++;});$$('[data-era-filter]').forEach(el=>{const active=el===b;el.classList.toggle('active',active);el.setAttribute('aria-pressed',String(active));});$('#timeline-count').textContent=`${n} selected moment${n===1?'':'s'}`;}));
  $('.copy-link')?.addEventListener('click',async()=>{try{await navigator.clipboard.writeText(location.href);notify('Article link copied');}catch{notify('Copy the article URL from your address bar');}});
  const form=$('#contribution-form');if(form){
    const subject=$('#contribution-subject');
    const status=$('#draft-status');
    const submit=$('#submit-contribution');
    const api='https://assyria-archive-contributions.andrew-zaia.workers.dev/submit';
    const makeDraft=()=>{
      const fd=new FormData(form);
      return ['# Assyria | The Living Archive','','Contribution draft - not submitted','','## Contributor','',
        'Name: '+(fd.get('name')||'Not supplied'),'Contact email: '+(fd.get('email')||'Not supplied'),
        '','## Submission','','Type: '+fd.get('type'),'Subject: '+fd.get('subject'),
        '','### Contribution','',fd.get('body'),'','### Sources or supporting records','',
        fd.get('sources')||'Not supplied','','### Attribution and permissions','',
        fd.get('permissions')||'To be discussed',''].join('\n');
    };
    const setStatus=(message,state='')=>{status.textContent=message;status.dataset.state=state;};
    const slug=new URLSearchParams(location.search).get('article');
    if(slug)getData().then(({articles})=>{const article=articles.find(x=>x.slug===slug);if(article)subject.value=article.title;}).catch(()=>{});
    $('#download-draft')?.addEventListener('click',()=>{
      const draft=makeDraft();
      const url=URL.createObjectURL(new Blob([draft],{type:'text/markdown;charset=utf-8'}));
      const a=document.createElement('a');
      a.href=url;a.download='assyria-contribution-draft.md';document.body.append(a);a.click();a.remove();
      setTimeout(()=>URL.revokeObjectURL(url),1000);
      setStatus('Your Markdown draft was downloaded to this device. It has not been submitted.','success');
      notify('Contribution draft downloaded');
    });
    form.addEventListener('submit',async e=>{
      e.preventDefault();
      if(!form.reportValidity())return;
      const fd=new FormData(form);
      const token=String(fd.get('cf-turnstile-response')||'');
      if(!token){setStatus('Please complete the security check before submitting. You can still download your draft.','error');return;}
      const data={};
      for(const key of ['type','subject','name','email','body','sources','permissions','website'])data[key]=String(fd.get(key)||'');
      data.turnstileToken=token;
      submit.disabled=true;
      setStatus('Sending your contribution securely for editorial review...');
      try{
        const response=await fetch(api,{method:'POST',mode:'cors',credentials:'omit',headers:{'Content-Type':'application/json'},body:JSON.stringify(data)});
        const result=await response.json().catch(()=>({}));
        if(!response.ok||result.ok!==true)throw new Error(result.error||'The submission service could not confirm delivery.');
        form.reset();
        window.turnstile?.reset?.();
        setStatus('Contribution received for editorial review. Thank you. Nothing has been published automatically.','success');
        notify('Contribution submitted');
      }catch(error){
        setStatus((error?.message||'Unable to send contribution.')+' Your draft remains on this page. You can download it for safekeeping.','error');
        window.turnstile?.reset?.();
      }finally{submit.disabled=false;}
    });
  }
})();
