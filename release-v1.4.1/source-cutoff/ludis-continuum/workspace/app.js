'use strict';
const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const label = value => String(value || '').replaceAll('_',' ').replace(/\b\w/g,c=>c.toUpperCase());
let state = null, ledger = null, view = 'tray', focusId = null, compareId = null, scope = 'all', example = false, dirty = false, rawDraft = null;
function objects(){ return ledger?.objects || []; }
function byId(id){ return objects().find(o=>o.id===id); }
function pins(){ return ledger?.extensions?.['workspace.tray'] || []; }
function display(o){ return o?.title || o?.id || 'Untitled material'; }
function statusText(){ return example ? 'LABELED EXAMPLE · NOT SAVED' : dirty ? 'Unsaved changes' : ledger ? 'Saved native ledger' : 'No campaign open'; }
function note(message, isError=false){ $('notice').textContent=message; $('notice').classList.toggle('error',isError); }
function markDirty(){ dirty=true; $('save-state').textContent=statusText(); }
async function api(path,data){
  const options = data ? {method:'POST',headers:{'Content-Type':'application/json','X-Desk-Token':state.token},body:JSON.stringify(data)} : {};
  const response=await fetch(path,options);
  const value=await response.json();
  if(!response.ok) throw Error(value.error || response.statusText);
  return value;
}
function statusBadge(o){
  const status = label(o.status);
  return '<span class="status status-'+esc(o.status)+'">'+esc(status)+'</span>';
}
function visibilityBadge(o){
  return '<span class="visibility '+(o.visibility==='gm_only'?'gm':'player')+'">'+(o.visibility==='gm_only'?'GM only':'Player-safe label')+'</span>';
}
async function openObject(id){ if(!byId(id)) return; focusId=id; compareId=null; await setView('materials'); if(view==='materials') $('object-view').scrollIntoView({block:'start',behavior:'instant'}); }
async function setView(next){
  if(view==='ledger' && next!=='ledger' && rawDraft!==null){
    try{
      const candidate=JSON.parse(rawDraft);
      await api('/api/validate',{ledger:candidate});
      ledger=candidate;rawDraft=null;markDirty();note('Valid ledger draft applied locally. Save to retain it.');
    }catch(error){note('Fix the ledger before leaving Ledger tools: '+error.message,true);$('json').focus();return;}
  }
  view=next;
  for(const id of ['tray','materials','capture','ledger']) $(id).hidden=id!==view;
  document.querySelectorAll('[data-tab]').forEach(button=>{button.classList.toggle('active',button.dataset.tab===view);button.setAttribute('aria-current',button.dataset.tab===view?'page':'false');});
  render();
}
function pin(id){
  const current=pins(), next=current.includes(id)?current.filter(x=>x!==id):[...current,id];
  ledger.extensions=ledger.extensions||{}; ledger.extensions['workspace.tray']=next;
  focusId=id; markDirty(); render(); note(current.includes(id)?'Removed from tonight. Save to retain the change.':'Brought into tonight. Save to retain the change.');
}
function movePin(id,direction){
  const next=[...pins()], at=next.indexOf(id), to=at+direction;
  if(at<0||to<0||to>=next.length)return;
  [next[at],next[to]]=[next[to],next[at]];
  ledger.extensions['workspace.tray']=next; markDirty(); render(); note('Tonight’s order changed. Save to retain it.');
}
function parseLinks(value){const links=[...new Set(value.split(',').map(x=>x.trim()).filter(Boolean))];const missing=links.filter(id=>!byId(id));if(missing.length){note('Unknown linked ID: '+missing.join(', ')+'. Choose an existing record.',true);return null;}return links;}
function currentSession(){return ledger.sessions.at(-1);}
function updateSession(field,value){
  if(!ledger.sessions.length) ledger.sessions.push({id:'session-'+crypto.randomUUID(),status:'preparing'});
  currentSession()[field]=value; markDirty();
}
function renderInit(){
  $('init-root').textContent=state?.root || 'your campaign directory';
  $('header-campaign').textContent='A place for the world in motion';
  $('save-state').textContent=statusText();
  $('save').hidden=true; $('player-link').hidden=true;
}
function renderTray(){
  const ordered=pins().map(byId).filter(Boolean);
  const current=ordered.find(o=>o.id===focusId)||ordered[0];
  $('tray-count').textContent=ordered.length?String(ordered.length):'';
  $('pin-count').textContent=ordered.length+' pinned';
  $('tonight-title').textContent=ledger.campaign.title||ledger.campaign.id;
  $('tonight-context').textContent=ledger.campaign.system ? [ledger.campaign.system,ledger.campaign.edition].filter(Boolean).join(' · ') : 'Your private campaign table';
  const session=currentSession();
  $('session-marker').textContent=session?.title||'NEXT SESSION';
  $('horizon').textContent=ledger.campaign.current_horizon||'No horizon recorded yet. Name the next pressure or question in the native ledger.';
  $('premise').textContent=ledger.campaign.premise||'';
  const prep=ledger.next_prep||[];
  $('prep-count').textContent=prep.length+' tasks';
  $('prep-list').innerHTML=prep.length?prep.map(x=>'<li>'+esc(typeof x==='string'?x:JSON.stringify(x))+'</li>').join(''):'<li class="empty-list">No preparation named yet.</li>';
  $('prep').value=prep.map(x=>typeof x==='string'?x:JSON.stringify(x)).join('\n');
  $('session-title').value=session?.title||'';
  $('session-notes').value=session?.notes||'';
  $('tray-cards').innerHTML=ordered.length?ordered.map((o,i)=>'<div class="cue '+(current?.id===o.id?'selected':'')+'"><button class="cue-main" data-focus="'+esc(o.id)+'" aria-current="'+(current?.id===o.id?'true':'false')+'"><span class="cue-number">'+String(i+1).padStart(2,'0')+'</span><span class="cue-text"><small>'+esc(label(o.kind))+' · '+esc(label(o.status))+'</small><strong>'+esc(display(o))+'</strong></span></button><div class="cue-actions"><button data-move="'+esc(o.id)+'" data-direction="-1" aria-label="Move '+esc(display(o))+' earlier" '+(i===0?'disabled':'')+'>↑</button><button data-move="'+esc(o.id)+'" data-direction="1" aria-label="Move '+esc(display(o))+' later" '+(i===ordered.length-1?'disabled':'')+'>↓</button><button data-pin="'+esc(o.id)+'" aria-label="Remove '+esc(display(o))+' from tonight">×</button></div></div>').join(''):'<div class="tray-empty"><span class="empty-glyph">∴</span><p>Nothing is in play yet.</p><span>Open the world and bring a scene, person, or pressure to tonight.</span></div>';
  if(!current){
    $('opening').innerHTML='<div class="opening-empty"><span class="eyebrow">THE OPENING IS YOURS</span><h3>What is in motion?</h3><p>Bring the scene or thread that gives the players something meaningful to meet. The table will keep its links and status beside it.</p><button data-view="materials" class="primary">Explore the world →</button></div>';
  } else {
    const connections=(current.links||[]).map(id=>byId(id)).filter(Boolean);
    $('opening').innerHTML='<div class="opening-head"><span class="eyebrow">IN FOCUS / '+esc(label(current.kind))+'</span><span class="opening-number">'+String(ordered.indexOf(current)+1).padStart(2,'0')+' / '+String(ordered.length).padStart(2,'0')+'</span></div><div class="opening-title"><h3>'+esc(display(current))+'</h3><div class="badges">'+statusBadge(current)+visibilityBadge(current)+'</div></div><p class="opening-content">'+esc(current.content||current.summary||'No description yet. Open this material to inspect its record.')+'</p><div class="opening-bottom"><div class="opening-links"><span class="eyebrow">CONNECTED HERE</span>'+(connections.length?connections.map(o=>'<button data-open="'+esc(o.id)+'">↗ '+esc(display(o))+'</button>').join(''):'<span class="muted">No outgoing links recorded</span>')+'</div><button class="open-world" data-open="'+esc(current.id)+'">Read source & relationships →</button></div>';
  }
}
function filteredObjects(){
  const q=$('filter').value.trim().toLowerCase();
  return objects().filter(o=>{
    const passScope=scope==='all'||(scope==='tonight'&&pins().includes(o.id))||(scope==='unresolved'&&['proposed','disputed'].includes(o.status));
    const passText=!q||[o.title,o.id,o.kind,o.content,o.summary,...(o.tags||[])].join(' ').toLowerCase().includes(q);
    return passScope&&passText;
  });
}
function renderWorld(){
  const all=objects(), filtered=filteredObjects();
  $('world-count').textContent=all.length+' records · '+all.filter(o=>['proposed','disputed'].includes(o.status)).length+' unresolved';
  document.querySelectorAll('[data-scope]').forEach(b=>b.classList.toggle('active',b.dataset.scope===scope));
  const groups=[...new Set(filtered.map(o=>o.kind))];
  $('inventory').innerHTML=groups.length?groups.map(kind=>'<div class="inventory-group"><div class="inventory-heading"><span>'+esc(label(kind))+'</span><small>'+filtered.filter(o=>o.kind===kind).length+'</small></div>'+filtered.filter(o=>o.kind===kind).map(o=>'<button data-open="'+esc(o.id)+'" class="inventory-item" aria-current="'+(focusId===o.id?'true':'false')+'"><span>'+esc(display(o))+'</span><small>'+esc(label(o.status))+' · '+(pins().includes(o.id)?'Tonight':'World')+'</small></button>').join('')+'</div>').join(''):'<p class="inventory-empty">No material matches. Clear search or change scope.</p>';
  const chosen=byId(focusId)||filtered[0]||all[0];
  if(chosen) focusId=chosen.id;
  if(!chosen){
    $('object-view').innerHTML='<div class="world-empty"><span class="eyebrow">NO MATERIAL YET</span><h3>Let the world acquire a memory.</h3><p>Capture an observation, choice, person, or open thread at the table.</p><button data-view="capture" class="primary">Record a moment →</button></div>';
    $('relation-map').innerHTML='<p class="muted">Connections will appear when material has explicit links.</p>';
    $('object-editor').hidden=true; $('compare-panel').hidden=true;
    return;
  }
  const back=all.filter(o=>(o.links||[]).includes(chosen.id));
  const outgoing=(chosen.links||[]).map(byId).filter(Boolean);
  const contradictions=(chosen.contradicts||[]).map(byId).filter(Boolean);
  $('object-view').innerHTML='<div class="reading-top"><span class="eyebrow">'+esc(label(chosen.kind))+' / '+esc(chosen.id)+'</span><button data-pin="'+esc(chosen.id)+'" class="pin-action">'+(pins().includes(chosen.id)?'− Remove from tonight':'+ Bring to tonight')+'</button></div><h3>'+esc(display(chosen))+'</h3><div class="badges">'+statusBadge(chosen)+visibilityBadge(chosen)+'</div><div class="reading-content">'+esc(chosen.content||chosen.summary||'No content recorded.')+'</div><div class="reading-facts"><div><small>CONFIDENCE</small><span>'+esc(label(chosen.confidence||'unknown'))+'</span></div><div><small>HORIZON</small><span>'+esc(chosen.tenure||'Unspecified')+'</span></div><div><small>EXPORT</small><span>'+esc(label(chosen.export_eligibility||'unknown'))+'</span></div></div><details class="provenance"><summary>Authority & provenance</summary><p><strong>Authority:</strong> '+esc(chosen.authority||'Unspecified')+'</p><ul>'+(chosen.provenance||[]).map(p=>'<li>'+esc(p)+'</li>').join('')+'</ul></details>';
  const group=(title,items)=>'<div class="relation-group"><small>'+title+' <b>'+items.length+'</b></small>'+(items.length?items.map(o=>'<div class="relation-row"><button data-open="'+esc(o.id)+'">'+esc(display(o))+' <span>'+esc(label(o.kind))+'</span></button><button data-compare="'+esc(o.id)+'" aria-label="Compare with '+esc(display(o))+'">≍</button></div>').join(''):'<p>None recorded</p>')+'</div>';
  $('relation-map').innerHTML='<div class="relation-center"><small>CURRENT MATERIAL</small><strong>'+esc(display(chosen))+'</strong></div>'+group('LINKS TO',outgoing)+group('LINKED FROM',back)+group('CONTRADICTS',contradictions);
  $('object-editor').hidden=false;
  $('object-title').value=chosen.title||''; $('object-content').value=chosen.content||''; $('object-links').value=(chosen.links||[]).join(', '); $('object-visibility').value=chosen.visibility;
  const locked=chosen.status!=='proposed';
  for(const id of ['object-title','object-content','object-links','object-visibility','apply-object']) $(id).disabled=locked;
  $('object-editor').querySelector('summary').textContent=locked?'Only proposals can be edited here':'Edit proposed material';
  const compare=byId(compareId);
  $('compare-panel').hidden=!compare||compare.id===chosen.id;
  if(compare&&compare.id!==chosen.id) $('compare-panel').innerHTML='<div class="compare-head"><span class="eyebrow">SIDE BY SIDE</span><button id="close-compare">Close comparison ×</button></div><div class="compare-grid">'+[chosen,compare].map(o=>'<div><small>'+esc(label(o.kind))+' · '+esc(label(o.status))+'</small><h4>'+esc(display(o))+'</h4><p>'+esc(o.content||o.summary||'No content recorded.')+'</p><span>'+esc(o.provenance?.join(' · ')||'No provenance recorded')+'</span></div>').join('')+'</div>';
}
function renderCapture(){
  const recent=objects().filter(o=>o.authority==='local_operator_proposal').slice(-6).reverse();
  $('recent-captures').innerHTML=recent.length?recent.map(o=>'<button data-open="'+esc(o.id)+'"><small>'+esc(label(o.kind))+' · '+esc(label(o.status))+'</small><strong>'+esc(display(o))+'</strong><span>'+esc((o.content||'').slice(0,150))+'</span></button>').join(''):'<p class="capture-empty">The session has no captured moments yet. Start with what actually occurred.</p>';
}
function renderLedger(){
  $('root').textContent=state.root;
  if(document.activeElement!==$('json')) $('json').value=rawDraft!==null?rawDraft:JSON.stringify(ledger,null,2);
}
function bindDynamic(){
  document.querySelectorAll('[data-open]').forEach(b=>b.onclick=()=>openObject(b.dataset.open));
  document.querySelectorAll('[data-focus]').forEach(b=>b.onclick=()=>{focusId=b.dataset.focus;renderTray();bindDynamic();});
  document.querySelectorAll('[data-pin]').forEach(b=>b.onclick=()=>pin(b.dataset.pin));
  document.querySelectorAll('[data-move]').forEach(b=>b.onclick=()=>movePin(b.dataset.move,Number(b.dataset.direction)));
  document.querySelectorAll('[data-view]').forEach(b=>b.onclick=()=>setView(b.dataset.view));
  document.querySelectorAll('[data-compare]').forEach(b=>b.onclick=()=>{compareId=b.dataset.compare;renderWorld();bindDynamic();$('compare-panel').scrollIntoView({block:'nearest'});});
  if($('close-compare')) $('close-compare').onclick=()=>{compareId=null;renderWorld();bindDynamic();};
}
function render(){
  $('init').hidden=!!ledger; $('work').hidden=!ledger; $('load-error').hidden=true;
  $('player-link').hidden=!ledger||example;
  if(!ledger){renderInit();return;}
  $('header-campaign').textContent=(example?'EXAMPLE / ':'')+(ledger.campaign.title||ledger.campaign.id);
  $('save').hidden=false; $('save').disabled=example;
  $('save-state').textContent=statusText();
  renderTray();renderWorld();renderCapture();renderLedger();bindDynamic();
}
async function refresh(){
  state=await api('/api/state');ledger=state.ledger;example=false;dirty=false;rawDraft=null;focusId=pins()[0]||objects()[0]?.id||null;render();
}
document.querySelectorAll('[data-tab]').forEach(b=>b.onclick=()=>setView(b.dataset.tab));
document.querySelectorAll('[data-scope]').forEach(b=>b.onclick=()=>{scope=b.dataset.scope;renderWorld();bindDynamic();});
$('browse-material').onclick=()=>setView('materials');
$('filter').oninput=()=>{renderWorld();bindDynamic();};
$('skin').value=['night','patchwork'].includes(localStorage.getItem('ludis-skin'))?localStorage.getItem('ludis-skin'):'night';
document.body.dataset.skin=$('skin').value;
$('skin').onchange=()=>{document.body.dataset.skin=$('skin').value;localStorage.setItem('ludis-skin',$('skin').value);};
$('prep').oninput=()=>{ledger.next_prep=$('prep').value.split('\n').map(x=>x.trim()).filter(Boolean);markDirty();$('prep-list').innerHTML=ledger.next_prep.map(x=>'<li>'+esc(x)+'</li>').join('')||'<li class="empty-list">No preparation named yet.</li>';$('prep-count').textContent=ledger.next_prep.length+' tasks';};
$('session-title').oninput=()=>updateSession('title',$('session-title').value);
$('session-notes').oninput=()=>updateSession('notes',$('session-notes').value);
$('init-form').onsubmit=async e=>{e.preventDefault();try{state=await api('/api/init',{...Object.fromEntries(new FormData(e.target)),etag:null});ledger=state.ledger;dirty=false;focusId=null;render();setView('tray');note('Native campaign created. Start with a scene, person, or pressure.');}catch(error){note(error.message,true);}};
$('apply-object').onclick=async()=>{const selected=byId(focusId);if(!selected||selected.status!=='proposed')return;const links=parseLinks($('object-links').value);if(!links)return;const candidate=structuredClone(ledger),target=candidate.objects.find(o=>o.id===selected.id);target.title=$('object-title').value;target.content=$('object-content').value;target.links=links;target.visibility=$('object-visibility').value;try{await api('/api/validate',{ledger:candidate});ledger=candidate;markDirty();render();note('Proposal changed. Save to retain it.');}catch(error){note(error.message,true);}};
$('capture-form').onsubmit=e=>{e.preventDefault();if(!ledger){note('Create a campaign first.',true);return;}const form=Object.fromEntries(new FormData(e.target));const links=parseLinks(form.links);if(!links)return;const kind=form.kind==='player-choice'?'observation':form.kind;ledger.objects.push({id:'capture-'+crypto.randomUUID(),kind,status:'proposed',visibility:'gm_only',authority:'local_operator_proposal',provenance:['Campaign Table capture at '+new Date().toISOString()],confidence:'unknown',tenure:'current session horizon',title:form.title,content:form.content,links,asset_ids:[],export_eligibility:'eligible'});e.target.reset();markDirty();render();note('Captured as a GM-only proposal. Save to retain it.');};
$('save').onclick=async()=>{try{const candidate=rawDraft!==null?JSON.parse(rawDraft):ledger;state=await api('/api/save',{ledger:candidate,etag:state.etag});ledger=state.ledger;rawDraft=null;dirty=false;render();note('Saved canonical campaign-ledger.json.');}catch(error){note(error.message,true);}};
$('json').oninput=()=>{rawDraft=$('json').value;markDirty();};
$('export').onclick=()=>{if(!ledger)return;const a=document.createElement('a');const content=rawDraft!==null?rawDraft:JSON.stringify(ledger,null,2);a.href=URL.createObjectURL(new Blob([content],{type:'application/json'}));a.download=rawDraft!==null?'campaign-ledger.draft.json':example?'campaign-ledger.example.json':'campaign-ledger.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),1000);};
async function importLedger(event){try{const file=event.target.files[0];if(!file)return;const content=await file.text();const original=await new Promise((resolve,reject)=>{const reader=new FileReader();reader.onload=()=>resolve(reader.result.split(',')[1]);reader.onerror=reject;reader.readAsDataURL(file);});state=await api('/api/save',{ledger:JSON.parse(content),etag:state.etag,import:true,original});ledger=state.ledger;example=false;dirty=false;rawDraft=null;focusId=pins()[0]||objects()[0]?.id||null;render();setView('tray');note('Native v2 ledger imported. Original bytes preserved.');}catch(error){note(error.message,true);}event.target.value='';}
$('import').onchange=importLedger;$('import-work').onchange=importLedger;
$('example').onclick=()=>{
  const object=(id,kind,title,content,visibility='gm_only',links=[],status='active_canon')=>({id,kind,title,content,visibility,links,status,authority:status==='active_canon'?'gm_approved':'local_operator_proposal',provenance:['Labeled illustrative example'],confidence:status==='active_canon'?'high':'unknown',tenure:'tonight',asset_ids:[],export_eligibility:'eligible'});
  ledger={format:'cd-ludis-campaign-ledger/v2',campaign:{id:'example',title:'The Last Lantern',premise:'One ferry. Three claimants. A promise that cannot survive the crossing.',system:'fictional tabletop example',current_horizon:'The last ferry leaves at midnight.'},table_contract:{player_preferences:[],lines:[],veils:[],other_boundaries:[]},objects:[object('ferry','scene','The lantern ferry','The last ferry waits at a black quay. A bell is sealed beneath the seat; three passengers have come with three different claims to the crossing.','player_safe',['bell','keeper']),object('keeper','npc','Keeper of the bell','Wants the bell delivered unopened. She has promised two rival houses the same crossing.','gm_only',['ferry','crossing']),object('crossing','thread','Who gets the crossing?','Three passengers. Two places aboard. One debt comes due when the bell rings.','gm_only',['keeper','ferry']),object('bell','rumor','The bell remembers debts','Travelers say the bell rings for promises broken on the river. Nobody agrees whose voice it uses.','player_safe',['ferry']),object('choice','observation','A passenger offers to stay behind','The group has heard the offer. What they choose to do with it is still open.','gm_only',['crossing'],'proposed')],assets:[],sessions:[{id:'session-example',status:'preparing',title:'The last crossing',notes:''}],approvals:[],publication:{status:'private_draft'},next_prep:['Decide what the ferryman will reveal if questioned.','Keep three viable approaches to the crossing.'],extensions:{'workspace.tray':['ferry','crossing','keeper']}};
  example=true;dirty=false;rawDraft=null;focusId='ferry';render();setView('tray');note('Labeled unsaved example. Your native campaign is unchanged.');
};
$('notice').innerHTML='<span>Opening the native campaign…</span>';
$('retry').onclick=()=>refresh().then(()=>note('')).catch(error=>{ $('load-error-message').textContent=error.message;note('Could not open the native ledger.',true); });
refresh().then(()=>note('')).catch(error=>{state={root:'your campaign directory',token:null,etag:null};renderInit();$('init').hidden=true;$('load-error').hidden=false;$('load-error-message').textContent=error.message;note('Could not open the native ledger.',true);});
