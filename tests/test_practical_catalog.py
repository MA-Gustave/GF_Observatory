from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
import sys


BASE = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('practical_catalog', BASE / 'tools/practical_catalog.py')
module = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = module
spec.loader.exec_module(module)


def dump(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj) + '\n', encoding='utf-8')


def test_missing_source_is_not_ready(tmp_path):
    inv = tmp_path/'inventory.json'
    prof=tmp_path/'profile.json'
    dump(inv,{'schema_id':'gf-practical.rgl-inventory','schema_version':'1.0','languages':[{'code':'Eng','structural_status':'candidate','structural_gaps':[],'source_dirs':['src/english']}]})
    dump(prof,{'schema_id':'gf-practical.profile','schema_version':'1.0','profile_id':'p','profile_version':'1.0','capabilities':[{'id':'factual-present','required':True,'scenario_ids':['factual-present'],'domains':['encyclopedic']}]})
    result=module.aggregate(inv,prof,tmp_path)
    assert result['counts'] == {'ready':0,'needs_work':0,'unverified':1}
    assert 'factual-present' in result['languages'][0]['unverified']


def test_verified_gold_can_be_ready_but_tampered_manifest_cannot(tmp_path):
    inv=tmp_path/'inventory.json';prof=tmp_path/'profile.json';run=tmp_path/'runs/run_01'
    dump(inv,{'schema_id':'gf-practical.rgl-inventory','schema_version':'1.0','languages':[{'code':'Eng','structural_status':'candidate','structural_gaps':[],'source_dirs':['src/english']}]})
    dump(prof,{'schema_id':'gf-practical.profile','schema_version':'1.0','profile_id':'p','profile_version':'1.0','domains':['encyclopedic'],'capabilities':[{'id':'factual-present','required':True,'scenario_ids':['factual-present'],'domains':['encyclopedic']}]})
    summary={'schema_id':'gf-wordbench.run-summary','schema_version':'1.0', 'metadata':{'project_id':'Eng','run_id':'01','no_compile':False},'totals':{'overall_status':'OK'},'scenario_results':[{'scenario_id':'factual-present','status':'OK','exit_code':0,'gold_match':True,'gold_path':'gold','normalized_output_path':'raw/out'}]}
    dump(run/'summary.json', summary)
    b=(run/'summary.json').read_bytes()
    dump(run/'manifest.json',{'schema_id':'gf-wordbench.artifact-manifest','schema_version':'1.0','artifacts':[{'path':'summary.json','role':'machine_summary','size_bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}]})
    report={'schema_id':'gf-practical.coverage-result','schema_version':'1.0','profile_id':'p','profile_version':'1.0','profile_sha256':hashlib.sha256(prof.read_bytes()).hexdigest(),'language_key':'Eng','wordbench_run_id':'01','wordbench_run_status':'OK','status':'ready','capabilities':[{'id':'factual-present','status':'passed','required':True,'domains':['encyclopedic']}], 'domains':[{'domain':'encyclopedic','status':'ready'}]}
    dump(run/'practical_coverage.json',report)
    assert module.aggregate(inv,prof,tmp_path/'runs')['counts']['ready']==1
    # Even a legitimate report must be downgraded when the raw Wordbench
    # summary has been modified after manifest production.
    summary['metadata']['project_id']='Fra'
    dump(run/'summary.json',summary)
    result=module.aggregate(inv,prof,tmp_path/'runs')
    assert result['counts']['ready']==0
    assert result['languages'][0]['status']=='unverified'
    assert result['languages'][0]['evidence_status']=='manifest_hash_mismatch'
