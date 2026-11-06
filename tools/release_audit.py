"""Optional local acceptance of a *real* practical pilot ZIP, without DB mutation."""
import argparse
import json
from pathlib import Path
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from gf_observatory.pilot_reader import inspect_archive
from gf_observatory.errors import ObservatoryError

def main(argv=None):
    p=argparse.ArgumentParser(description='Read-only WordBench pilot archive acceptance audit')
    p.add_argument('zip',type=Path)
    p.add_argument('--report',type=Path)
    a=p.parse_args(argv)
    try:r=inspect_archive(a.zip)
    except ObservatoryError as e:
        print(json.dumps({'status':'REJECTED','code':e.code,'message':str(e)}),file=sys.stderr)
        return 4
    doc={'schema_id':'gf-observatory.real-pilot-audit','schema_version':'1.0',
         'archive_sha256':r.archive_sha256,'archive_bytes':r.archive_bytes,
         'member_count':r.member_count,'member_tree_sha256':r.recalculated_members_sha256,
         'source_batch_id':r.batch_id,'source_status':r.source_status,
         'languages_requested_in_source':len(r.source_languages),
         'selected_language_codes':list(r.selected),
         'selected_scenario_count':len(r.scenarios),
         'selected_candidate_count':sum(x['candidate_count'] for x in r.languages),
         'producer_totals':r.totals,'surface_warnings':r.warnings,
         'canonical_manifest_verified':False,'human_review_completed':False,
         'linguistic_certification':False,'readiness':'R0',
         'description':'Pilot ZIP consistency and bytes verified locally; not canonical release proof.'}
    serialized=json.dumps(doc,ensure_ascii=False,indent=2)+'\n'
    if a.report:
        if a.report.exists():raise SystemExit('Refusing to overwrite an existing audit report')
        a.report.parent.mkdir(parents=True,exist_ok=True)
        a.report.write_text(serialized,encoding='utf8')
    print(serialized)
    return 0
if __name__=='__main__':raise SystemExit(main())
