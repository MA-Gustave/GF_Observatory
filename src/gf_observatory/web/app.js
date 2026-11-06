"use strict";
const $ = id => document.getElementById(id);
const state = {batch:null, languages:[], scenarios:[], active:null, summary:null};
function el(tag, cls, text){ const n=document.createElement(tag);if(cls)n.className=cls;if(text!==undefined)n.textContent=String(text);return n; }
async function api(endpoint){ const r=await fetch(endpoint,{cache:"no-store"});const obj=await r.json();if(!r.ok)throw Error(obj.error?.code||"HTTP_"+r.status);return obj.data; }
const query=(name,val)=>encodeURIComponent(name)+"="+encodeURIComponent(val);
function metric(v,label){ const n=el("article","metric"),b=el("strong",null,v),a=el("span",null,label);n.append(b,a);return n; }
function renderSummary(){const d=state.summary,box=$("metrics");box.replaceChildren();if(!d || d.status==="NO_EVIDENCE"){box.append(metric("0","Lots importés"));return;}
box.append(metric(d.languages_in_scope,"Langues dans le périmètre"),metric(d.scenarios_in_scope,"Intentions observées"),metric(d.candidate_for_review,"Candidats GF"),metric(d.human_reviews_completed,"Revues humaines confirmées"));
const meta=$("source");meta.replaceChildren();const lines=[["Lot source",d.source_batch_id],["SHA-256 source",d.source_archive_sha256],["État producteur",d.producer_status],["Sources dans le ZIP",d.source_languages_total+" langues (dont "+d.languages_in_scope+" observées)"],["Readiness canonique",d.canonical_readiness+" — non qualifiée"],["Certification", "Non effectuée"],["Alertes heuristiques",JSON.stringify(d.surface_warnings||{})]];
for(const [k,v] of lines){const row=el("div");row.append(el("strong",null,k+" : "),el("span",null,v));meta.append(row);} }
function renderLanguages(){const box=$("langs");box.replaceChildren();for(const r of state.languages){const b=el("button","langbtn"),label=el("span","lname");label.append(el("span",null,r.code),el("span","lcode",r.technical_status));b.append(label,el("span","completion",r.candidate_count+" / 15"));b.setAttribute("aria-pressed",String(state.active===r.code));b.onclick=()=>{state.active=r.code;renderLanguages();renderScenarios();};box.append(b);} }
function renderScenarios(){const box=$("scenarios");box.replaceChildren();const code=state.active;$("detailtitle").textContent=code?"Détails — "+code:"Détails des intentions";
const all=state.scenarios.filter(x=>x.code===code),f=$("statusfilter").value;$("detailmeta").textContent=all.length+" scénarios — revue humaine non effectuée";
const selected=all.filter(x=>f==="all"|| (f==="warning"?x.surface_warnings.length>0:x.status===f));
for(const r of selected){const card=el("article","scenario"),head=el("div","scenario-top"),tag=el("span","tag"+(r.status!=="candidate_for_review"?" bad":""),r.status==="candidate_for_review"?"Candidat":r.status);head.append(el("span","scenario-id",r.scenario_id),tag);card.append(head,el("p","candidate",r.candidate||"Aucun candidat généré"),el("p","meaning",r.meaning_en));if(r.surface_warnings.length)card.append(el("p","warn","Alerte de surface : "+r.surface_warnings.join(", ")));box.append(card);}
if(!selected.length)box.append(el("p","muted","Aucun scénario correspondant au filtre.")); }
async function refresh(){try{$("message").textContent="Lecture des analyses persistées…";
const batches=await api("/api/v1/batches");const select=$("batch");select.replaceChildren();if(!batches.length){state.summary={status:"NO_EVIDENCE"};renderSummary();$("langs").textContent="Aucun lot. Utilise l'application de bureau ou import-pilot.";$("message").textContent="En attente de preuves";return;}
for(const b of batches){const o=el("option",null,b.source_batch_id);o.value=b.import_id;select.append(o);}if(state.batch && batches.some(b=>b.import_id===state.batch))select.value=state.batch;else state.batch=select.value;
await loadBatch();}catch(err){$("message").textContent="Erreur : "+err.message;} }
async function loadBatch(){state.batch=$("batch").value;const q="?"+query("batch_id",state.batch);const [s,l,r]=await Promise.all([api("/api/v1/status"+q),api("/api/v1/languages"+q),api("/api/v1/scenarios"+q)]);state.summary=s;state.languages=l;state.scenarios=r;state.active=l.some(x=>x.code===state.active)?state.active:(l[0]?.code||null);renderSummary();renderLanguages();renderScenarios();$("message").textContent="Lecture seule · preuves techniques non certifiées";}
$("reload").addEventListener("click",refresh);$("batch").addEventListener("change",()=>loadBatch().catch(e=>$("message").textContent=e.message));$("statusfilter").addEventListener("change",renderScenarios);refresh();
