"""Synthetic, clearly labelled test archives. Not real GF evidence."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import json
from gf_observatory.policy import CORE_14,SCENARIOS_15
from gf_observatory.jsonsafe import dumps

BATCH_ID="20261105T233034Z-TEST001"
ROOT=f"defluens-batch-full-{BATCH_ID}/"

def fake_archive(path, languages=CORE_14, *, fail_language=None, malicious=None,
                 tamper_candidate=False, tamper_counters=False, reviewed=False):
    path=Path(path)
    entries=[];files={};global_counts={x:0 for x in ("candidate_for_review","probe_failed","timeout","unverified")}
    for code in languages:
        counts={x:0 for x in global_counts}
        scenarios=[];dirname=f"{ROOT}languages/defluens-pilot-{code}-synthetic/"
        for sid in SCENARIOS_15:
            status="probe_failed" if code==fail_language else "candidate_for_review"
            candidate=f"{code} synthetic {sid}" if status=="candidate_for_review" else None
            counts[status]+=1;global_counts[status]+=1
            scenarios.append({"id":sid,"status":status,"candidate":candidate,
                "exit_code":0 if candidate else 1,"timed_out":False,
                "gold_match":None,"review_approved":reviewed,
                "semantic_intent":sid,"meaning_en":"Fictional example.","reason":"gold_and_linguistic_review_missing"})
            if candidate:
                files[dirname+f"scenarios/{sid}.candidate.txt"]=(candidate if not tamper_candidate else "tampered text").encode()+b"\n"
            files[dirname+f"scenarios/{sid}.stdout.txt"]=b"synthetic output\n"
            files[dirname+f"scenarios/{sid}.stderr.txt"]=b""
        report={"schema_id":"defluens.pilot-run","schema_version":"1.0","language":code,
                "run_id":"synthetic","status":"unverified","semantic_coverage_verified":False,
                "scenarios":scenarios}
        files[dirname+"pilot_run.json"]=dumps(report)
        entries.append({"language":code,"status":"probe_failed" if fail_language==code else "candidate_for_review",
                        "scenarios_attempted":15,"totals":counts})
    overall={"schema_id":"defluens.pilot-batch","schema_version":"1.0","batch_id":BATCH_ID,
             "mode":"full","languages_requested":list(languages),
             "started_at":"2026-11-05T23:30:34Z","finished_at":"2026-11-05T23:35:34Z",
             "status":"completed_unverified","semantic_coverage_verified":False,
             "totals":{**global_counts,"languages_attempted":len(languages),"languages_unattempted":0},
             "entries":entries}
    if tamper_counters:overall["totals"]["candidate_for_review"]+=1
    files[ROOT+"batch_summary.json"]=dumps(overall)
    if malicious:files[malicious]=b"malicious"
    with ZipFile(path,"w",compression=ZIP_DEFLATED) as z:
        for key,value in files.items():z.writestr(key,value)
    return path
