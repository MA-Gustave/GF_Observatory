"""Read model: do not turn pilot candidates into canonical readiness or review."""
from collections import defaultdict
from .jsonsafe import utcnow
from .policy import CORE_14,SCENARIOS_15,LANG_NAMES

ZONES = {"A":("IDNT","CONF","SCHE","MANI"),
         "B":("SUMM","RAWE","HASH","FRESH"),
         "C":("COMP","SCEN","ARTF"),
         "D":("GOLD","REGR","GATE")}

def matrix(batch, language):
    """A canonical *evidence* matrix, not a GF candidate-success score."""
    observed={"IDNT", "SUMM", "RAWE", "SCEN"}
    # This pilot has parsed source structures but NO canonical source manifest.
    # SHA over ZIP bytes is local evidence integrity, NOT canonical HASH.
    found=[]; zones={}
    for zone, ids in ZONES.items():
        cells=[]
        for sid in ids:
            st="OBSERVED" if sid in observed else ("INCOMPATIBLE" if sid in {"SCHE","MANI","HASH"} else "MISSING")
            cell={"signal_id":sid,"status":st,"score":None,"confidence":None,
                  "evidence_refs":["archive-sha256:"+batch["archive_sha256"]] if sid in observed else [],
                  "reason_codes":[] if sid in observed else ["CANONICAL_PRODUCER_EVIDENCE_REQUIRED"]}
            cells.append(cell);found.append(cell)
        zones[zone]={"signal_ids":list(ids),"cells":cells}
    return {"schema_id":"gf-observatory.evidence-matrix","schema_version":"1.0",
            "profile_id":"defluens-practical-15/core-14/1","observation_id":batch["import_id"]+":"+language,
            "language":language,"zones":zones,"signals":found,"maturity":None,
            "readiness":"R0","health":"UNKNOWN","strategy":"SAFE_MODE",
            "reason_codes":["PILOT_NOT_CANONICAL_WORDBENCH_RUN","LINGUISTIC_REVIEW_MISSING"],
            "practical_generation_status":"unverified"}

def overview(batch,langrows,scenarios):
    warnings=defaultdict(int)
    for x in scenarios:
        for w in x["surface_warnings"]:warnings[w]+=1
    cand=sum(r["candidate_count"] for r in langrows)
    failed=sum(r["failed_count"] for r in langrows)
    timed=sum(r["timeout_count"] for r in langrows)
    technical_complete=sum(r["candidate_count"]==15 for r in langrows)
    return {"schema_id":"gf-observatory.practical-status","schema_version":"1.0",
        "status":"PILOT_EVIDENCE_ONLY","scope":"CORE_14_USEFUL_CAPABILITIES",
        "batch_id":batch["import_id"],"source_batch_id":batch["source_batch_id"],
        "producer_status":batch["source_status"],"source_archive_sha256":batch["archive_sha256"],
        "source_languages_total":len(batch["source_languages"]),"languages_in_scope":len(langrows),
        "required_capabilities_per_language":15,
        "scenarios_in_scope":len(scenarios),"candidate_for_review":cand,"probe_failed":failed,
        "timeout":timed,"technical_15_of_15_languages":technical_complete,
        "source_full_batch_totals":batch["source_totals"],
        "human_reviews_completed":0,"linguistically_certified":False,
        "canonical_readiness":"R0","canonical_maturity":None,
        "practical_generation_status":"unverified","published":False,"activated":False,
        "surface_warnings":dict(sorted(warnings.items())),
        "generated_at":utcnow()}

def trend(batch_list,language,lang_lookup):
    """Only a technical candidate-count trend across distinct source batch hashes."""
    records=[];seen=set()
    for b in sorted(batch_list,key=lambda x:(x["finished_at"],x["import_id"])):
        if b["archive_sha256"] in seen:continue
        seen.add(b["archive_sha256"])
        rows={x["code"]:x for x in lang_lookup(b["import_id"])}
        if language not in rows:continue
        r=rows[language]
        records.append({"batch_id":b["import_id"],"source_batch_id":b["source_batch_id"],
                        "finished_at":b["finished_at"],"candidate_count":r["candidate_count"],
                        "failed_count":r["failed_count"],"technical_status":r["technical_status"]})
    changes=[]
    for left,right in zip(records,records[1:]):
        diff=right["candidate_count"]-left["candidate_count"]
        changes.append({"from":left["batch_id"],"to":right["batch_id"],"delta_candidates":diff,
            "classification":"TECHNICAL_IMPROVEMENT" if diff>0 else "TECHNICAL_REGRESSION" if diff<0 else "UNCHANGED"})
    return {"language":language,"trend_type":"TECHNICAL_CANDIDATE_ONLY",
            "linguistic_regression_assessed":False,"records":records,"changes":changes,
            "status":changes[-1]["classification"] if changes else "NO_COMPARABLE_BASELINE"}
