"""Manual redacted static status export. Never git-pushes or activates runtime sets."""
from pathlib import Path
import json
import shutil
import tempfile
from .errors import ObservatoryError, require
from .jsonsafe import dumps, sha256, utcnow
from .policy import LANG_NAMES

HTML='''<!doctype html><html lang="fr"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>GF Observatory · état public candidat</title><link rel="stylesheet" href="style.css"></head><body><header><h1>GF Observatory</h1><p>Projection de preuves techniques — non certifiées</p></header><main><p class="notice">Les candidats GF et les statistiques ne prouvent aucune correction linguistique. Aucun RuntimeSet publié ou activé.</p><p id="info">Chargement du statut…</p><section id="langs" class="grid"></section></main><script src="app.js"></script></body></html>'''
CSS='''*{box-sizing:border-box}body{margin:0;font:16px system-ui,sans-serif;background:#f1f4f5;color:#213344}header{background:#162d45;color:white;padding:30px max(20px,calc((100vw - 1100px)/2))}header h1{margin:0}header p{opacity:.8}main{max-width:1100px;margin:auto;padding:22px}.notice{background:#fff3d7;border:1px solid #ddc692;padding:16px;border-radius:9px}.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(210px,1fr));gap:14px}article{border:1px solid #d2dfe7;border-radius:11px;background:white;padding:17px}h2{margin-top:0;font-size:1.1rem}strong{font-size:1.5rem;color:#23726a}small{display:block;color:#647884}'''
JS='''"use strict";(async()=>{try{const r=await fetch("./status.json",{cache:"no-store"});if(!r.ok)throw Error("HTTP " + r.status);const d=await r.json();document.getElementById("info").textContent=`${d.languages.length} langues observées · ${d.scope} · Revue humaine non effectuée`;for(const l of d.languages){const a=document.createElement("article"),h=document.createElement("h2"),b=document.createElement("strong"),s=document.createElement("small");h.textContent=l.name;b.textContent=`${l.candidate_count}/15`;s.textContent=`Candidats techniques · ${l.surface_warning_count} alertes · R0 non qualifié`;a.append(h,b,s);document.getElementById("langs").append(a);}}catch(e){document.getElementById("info").textContent="Statut indisponible (ouvrir par un serveur HTTP statique)";}})();'''

def export_static(app, output:Path, import_id=None, acknowledged=False):
    require(acknowledged,"OBS_APPROVAL_REQUIRED", "Explicit operator acknowledgment required for public projection",400)
    batch=app.batch(import_id)
    langs=app.store.languages(batch["import_id"])
    scenarios=app.store.scenarios(batch["import_id"])
    warningcount={r["code"]:0 for r in langs}
    for s in scenarios:
        warningcount[s["code"]]+=len(s["surface_warnings"])
    data={"schema_id":"gf-observatory.public-pilot-status","schema_version":"1.0",
          "generated_at":utcnow(),"scope":"14 languages · 15 useful intents",
          "verification":"LOCAL_PILOT_ARCHIVE_ONLY","review_status":"NOT_REVIEWED",
          "linguistically_certified":False,"canonical_readiness":"R0","released":False,
          "activated":False,"languages":[{"code":r["code"],"name":LANG_NAMES[r["code"]],
          "candidate_count":r["candidate_count"],"failed_count":r["failed_count"],
          "surface_warning_count":warningcount[r["code"]]} for r in langs]}
    contents={"index.html":HTML.encode("utf8"),"app.js":JS.encode("utf8"),
              "style.css":CSS.encode("utf8"),"status.json":dumps(data)+b"\n"}
    target=Path(output).expanduser().absolute()
    # Never write into an existing data store, evidence source directory, or source tree.
    require(target.name not in ("", ".", "..") and target != Path(target.anchor) and
            not target.is_symlink(),"OBS_PUBLIC_OUTPUT","Unsafe output directory")
    dbdir=app.config.database.parent.resolve(strict=False)
    require(not target.resolve(strict=False).is_relative_to(dbdir) and not dbdir.is_relative_to(target.resolve(strict=False)),
            "OBS_PUBLIC_OUTPUT","Public output overlaps private DB state")
    if target.exists():
        require(target.is_dir() and all(p.is_file() and not p.is_symlink() and p.name in contents for p in target.iterdir()),
                "OBS_PUBLIC_OUTPUT","Existing folder contains unrelated/private files")
    target.parent.mkdir(parents=True,exist_ok=True)
    stage=Path(tempfile.mkdtemp(prefix=".gf-obs-stage-",dir=target.parent));backup=None
    try:
        for name,raw in contents.items():(stage/name).write_bytes(raw)
        if target.exists():
            backup=Path(tempfile.mkdtemp(prefix=".gf-obs-old-",dir=target.parent))
            backup.rmdir();target.rename(backup)
        try:stage.rename(target)
        except OSError:
            if backup and backup.exists():backup.rename(target)
            raise
        if backup and backup.exists():shutil.rmtree(backup)
    finally:
        if stage.exists():shutil.rmtree(stage)
    return {"local_export":str(target),"files":list(contents),"status_sha256":sha256(contents["status.json"]),
            "external_publication_performed":False,"linguistically_certified":False}
