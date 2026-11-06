"""Deterministically assemble the entire source repository ZIP (no private evidence)."""
from pathlib import Path
import hashlib
import json
import zipfile
import argparse

ROOT=Path(__file__).resolve().parents[1]
SKIP={'__pycache__','.pytest_cache','.gf-observatory','.venv','.git','dist','build','.mypy_cache'}

def sha(data):return hashlib.sha256(data).hexdigest()

def collect():
    return sorted((p for p in ROOT.rglob('*') if p.is_file() and p.name!='BUILD_MANIFEST_SHA256.json'
            and not any(part in SKIP or part.endswith('.egg-info') for part in p.relative_to(ROOT).parts)
            and p.suffix not in ('.pyc','.pyo')),key=lambda p:p.relative_to(ROOT).as_posix())

def build(path):
    files=collect()
    manifest={'schema_id':'gf-observatory.source-release-manifest','schema_version':'1.0',
        'release':'1.0.0rc1','archive_scope':'entire repository source and documentation',
        'excludes':['private databases','source ZIP evidence','generated reports','Python caches'],
        'files':[{'path':p.relative_to(ROOT).as_posix(),'size_bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in files]}
    (ROOT/'BUILD_MANIFEST_SHA256.json').write_bytes(json.dumps(manifest,sort_keys=True,indent=2,ensure_ascii=False).encode()+b'\n')
    files=sorted([*files,ROOT/'BUILD_MANIFEST_SHA256.json'],key=lambda p:p.relative_to(ROOT).as_posix())
    output=Path(path).absolute();output.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for p in files:
            entry=zipfile.ZipInfo('GF_Observatory/'+p.relative_to(ROOT).as_posix(),date_time=(2026,11,5,18,0,0))
            entry.compress_type=zipfile.ZIP_DEFLATED
            entry.external_attr=(0o644<<16)
            z.writestr(entry,p.read_bytes(),compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
    with zipfile.ZipFile(output) as z:
        assert z.testzip() is None
        assert len(set(z.namelist()))==len(files)
    print(json.dumps({'path':str(output),'sha256':sha(output.read_bytes()),'bytes':output.stat().st_size,'files':len(files)},indent=2))

if __name__=='__main__':
    ap=argparse.ArgumentParser()
    ap.add_argument('output',type=Path)
    build(ap.parse_args().output)
