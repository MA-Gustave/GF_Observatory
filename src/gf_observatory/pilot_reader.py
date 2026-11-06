"""Strict, read-only importer for *actual* Defluens practical WordBench pilot ZIPs.

A pilot ZIP is NOT a canonical GF WordBench artifact manifest. It is technical
candidate evidence, with producer-claimed counts and locally recalculated bytes.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
from pathlib import Path, PurePosixPath
import re
import stat
import zipfile
from .errors import ObservatoryError, require
from .jsonsafe import loads, sha256, parse_time, utcnow
from .policy import CORE_14, SCENARIOS_15, STATUS_KEYS, scope

MAX_MEMBERS = 2500
MAX_EXPANDED = 200_000_000
MAX_MEMBER = 10_000_000
MAX_JSON = 8_000_000
MAX_ARCHIVE = 250_000_000
HEX = re.compile(r"^[0-9a-f]{64}$")
CODE = re.compile(r"^[A-Z][a-z]{2}$")


def _check_member(info: zipfile.ZipInfo):
    name = info.filename
    require(isinstance(name, str) and 0 < len(name) < 400, "OBS_ZIP_PATH", "Bad ZIP member length")
    require("\\" not in name and "\x00" not in name and not name.startswith("/") and
            not re.match(r"^[A-Za-z]:", name), "OBS_ZIP_PATH", "Absolute/Windows ZIP member path")
    parts = name.rstrip("/").split("/")
    require(all(seg not in ("", ".", "..") and not seg.endswith((".", " ")) for seg in parts),
            "OBS_ZIP_PATH", "ZIP path traversal or noncanonical member")
    require(len(parts) <= 9, "OBS_ZIP_PATH", "ZIP path too deep")
    require(not any(re.search(r"[\x00-\x1f:*?\"<>|]", seg) for seg in parts),
            "OBS_ZIP_PATH", "Unsafe ZIP member name")
    if info.create_system == 3:
        mode = info.external_attr >> 16
        require(not stat.S_ISLNK(mode), "OBS_ZIP_LINK", "ZIP symlink refused")
    require(info.file_size <= MAX_MEMBER, "OBS_ZIP_BOMB", "ZIP member too large")
    # Refuse implausible expansion before attempting to read.
    require(info.file_size == 0 or info.compress_size > 0, "OBS_ZIP_BOMB", "Invalid compressed size")
    if info.compress_size:
        require(info.file_size / info.compress_size <= 2000, "OBS_ZIP_BOMB", "Compression ratio exceeds limit")


@dataclass(frozen=True)
class PilotImport:
    batch_id: str
    archive_sha256: str
    archive_bytes: int
    member_count: int
    recalculated_members_sha256: str
    started_at: str
    finished_at: str
    source_status: str
    source_languages: tuple[str,...]
    selected: tuple[str,...]
    totals: dict
    languages: list[dict]
    scenarios: list[dict]
    warnings: list[dict]
    imported_at: str


def inspect_archive(path: Path, languages=None) -> PilotImport:
    selected = scope(languages)
    f = Path(path).expanduser().absolute()
    require(f.is_file(), "OBS_SOURCE_UNREACHABLE", "ZIP not found", 404)
    require(not f.is_symlink(), "OBS_SOURCE_LINK", "Symlink source archive refused")
    require(f.stat().st_size <= MAX_ARCHIVE, "OBS_ZIP_BOMB", "ZIP source too large")
    before = f.stat()
    h = hashlib.sha256()
    with f.open("rb") as stream:
        for block in iter(lambda:stream.read(1024*1024),b""):h.update(block)
    digest = h.hexdigest()
    try:
        with zipfile.ZipFile(f, "r") as z:
            infos=z.infolist()
            require(len(infos) <= MAX_MEMBERS, "OBS_ZIP_BOMB", "Too many ZIP members")
            require(sum(x.file_size for x in infos) <= MAX_EXPANDED,
                    "OBS_ZIP_BOMB", "ZIP uncompressed size limit exceeded")
            by_name={}
            for info in infos:
                _check_member(info)
                norm=info.filename.rstrip("/").casefold()
                require(norm not in by_name, "OBS_ZIP_COLLISION", "Duplicate/ambiguous ZIP member")
                by_name[norm]=info
            hashes={}
            for info in infos:
                if info.is_dir(): continue
                hh=hashlib.sha256();size=0
                try:
                    with z.open(info, "r") as reader:
                        for block in iter(lambda:reader.read(1024*1024),b""):
                            size+=len(block)
                            require(size<=MAX_MEMBER,"OBS_ZIP_BOMB","Member exceeds read budget")
                            hh.update(block)
                except (OSError, zipfile.BadZipFile, RuntimeError) as exc:
                    raise ObservatoryError("OBS_ZIP_INTEGRITY",f"Cannot validate ZIP member: {info.filename}") from exc
                require(size==info.file_size,"OBS_ZIP_INTEGRITY","Declared ZIP member size mismatch")
                hashes[info.filename]=(hh.hexdigest(),size)
            names=list(hashes)
            sum_names=[n for n in names if n.endswith("/batch_summary.json") and n.count("/")==1]
            require(len(sum_names)==1,"OBS_PILOT_SCHEMA","Expected one root batch_summary.json")
            prefix=sum_names[0].rsplit("/",1)[0]+"/"
            require(all(n.startswith(prefix) for n in names),"OBS_ZIP_PATH","Unexpected second ZIP root")
            summary=loads(z.read(sum_names[0]),MAX_JSON)
            require(isinstance(summary,dict) and summary.get("schema_id")=="defluens.pilot-batch" and summary.get("schema_version")=="1.0",
                    "OBS_PILOT_SCHEMA","Unsupported batch summary schema")
            require(summary.get("mode")=="full" and summary.get("status")=="completed_unverified",
                    "OBS_PILOT_INCOMPLETE","Only completed_unverified full pilot archives supported")
            bid=summary.get("batch_id")
            require(isinstance(bid,str) and re.fullmatch(r"[0-9]{8}T[0-9]{6}Z-[0-9A-Za-z_-]{1,24}",bid),
                    "OBS_PILOT_ID","Invalid pilot batch ID")
            require(prefix==f"defluens-batch-full-{bid}/","OBS_PILOT_ID","ZIP root and batch identity differ")
            parse_time(summary.get("started_at"));parse_time(summary.get("finished_at"))
            requested=summary.get("languages_requested")
            require(isinstance(requested,list) and requested and len(set(requested))==len(requested) and
                    all(isinstance(c,str) and CODE.fullmatch(c) for c in requested),
                    "OBS_PILOT_SCHEMA","Invalid requested languages")
            require(set(selected).issubset(set(requested)),"OBS_SCOPE_MISSING","Requested 14-language scope absent in archive")
            entries=summary.get("entries")
            require(isinstance(entries,list) and len(entries)==len(requested) and
                    [e.get("language") for e in entries]==requested,
                    "OBS_PILOT_INCONSISTENT","Batch entry ordering/languages differ")
            for ent in entries:
                require(ent.get("status") in ("candidate_for_review","probe_failed","partial","timeout","unverified"),
                        "OBS_PILOT_SCHEMA","Invalid language status")
                require(isinstance(ent.get("totals"),dict),"OBS_PILOT_SCHEMA","Missing language totals")
            totals={x:0 for x in STATUS_KEYS}
            langrows=[];scenrows=[];warnings=[]
            all_lang_counts={}
            for ent in entries:
                lang=ent["language"]
                targets=[n for n in names if re.fullmatch(
                    re.escape(prefix)+r"languages/defluens-pilot-"+re.escape(lang)+r"-[^/]+/pilot_run\.json",n)]
                require(len(targets)==1,"OBS_PILOT_INCONSISTENT",f"Pilot report absent or duplicated for {lang}")
                report_path=targets[0]
                report=loads(z.read(report_path),MAX_JSON)
                require(isinstance(report,dict) and report.get("schema_id")=="defluens.pilot-run" and
                        report.get("schema_version")=="1.0" and report.get("language")==lang,
                        "OBS_PILOT_SCHEMA",f"Bad pilot report identity {lang}")
                require(report.get("semantic_coverage_verified") is False,
                        "OBS_PILOT_INCONSISTENT","Pilot report unexpectedly claims semantic certification")
                scenarios=report.get("scenarios")
                require(isinstance(scenarios,list) and [s.get("id") for s in scenarios]==list(SCENARIOS_15),
                        "OBS_PILOT_SCOPE",f"Unexpected practical scenario set for {lang}")
                counts={x:0 for x in STATUS_KEYS}
                for item in scenarios:
                    sid=item["id"];st=item.get("status")
                    require(st in STATUS_KEYS,"OBS_PILOT_SCHEMA",f"Bad scenario state {lang}/{sid}")
                    require(type(item.get("timed_out")) is bool,"OBS_PILOT_SCHEMA","Missing timed_out")
                    require(item.get("review_approved") is False and item.get("gold_match") is None,
                            "OBS_PILOT_REVIEW_UNTRUSTED","Pilot archive contains unsupported approved review claim")
                    candidate=item.get("candidate")
                    if st=="candidate_for_review":
                        require(isinstance(candidate,str) and bool(candidate.strip()) and item.get("exit_code")==0 and
                                item.get("timed_out") is False,
                                "OBS_PILOT_INCONSISTENT",f"Candidate result inconsistent: {lang}/{sid}")
                        candidate_member=report_path.rsplit("/",1)[0]+f"/scenarios/{sid}.candidate.txt"
                        require(candidate_member in hashes,"OBS_PILOT_INCONSISTENT",f"Candidate text missing: {lang}/{sid}")
                        b=z.read(candidate_member)
                        try: sidecar=b.decode("utf-8").strip()
                        except UnicodeDecodeError as e: raise ObservatoryError("OBS_PILOT_INCONSISTENT","Invalid candidate UTF-8") from e
                        require(sidecar==candidate.strip(),"OBS_PILOT_INCONSISTENT",f"Candidate mismatch: {lang}/{sid}")
                    else:
                        require(st!="probe_failed" or item.get("exit_code")!=0 or item.get("timed_out") or not candidate,
                                "OBS_PILOT_INCONSISTENT",f"Failed probe contradicts exit status: {lang}/{sid}")
                    counts[st]+=1;totals[st]+=1
                    if lang in selected:
                        item_warnings=[]
                        if isinstance(candidate,str) and "&+" in candidate:
                            item_warnings.append("GF_UNRESOLVED_GLUE_MARKER")
                            warnings.append({"language":lang,"scenario_id":sid,"code":"GF_UNRESOLVED_GLUE_MARKER",
                                             "interpretation":"Surface anomaly heuristic, not linguistic review"})
                        scenrows.append({"language":lang,"scenario_id":sid,"status":st,
                            "semantic_intent":str(item.get("semantic_intent", ""))[:220],
                            "meaning_en":str(item.get("meaning_en", ""))[:300],
                            "candidate":candidate if isinstance(candidate,str) else None,
                            "exit_code":item.get("exit_code") if type(item.get("exit_code")) is int else None,
                            "timed_out":item["timed_out"],"reason":str(item.get("reason", ""))[:240],
                            "gold_match":None,"review_approved":False,
                            "evidence_member":report_path,"evidence_sha256":hashes[report_path][0],
                            "surface_warnings":item_warnings})
                require(all(type(ent["totals"].get(k)) is int and ent["totals"][k]==v for k,v in counts.items()),
                        "OBS_PILOT_INCONSISTENT",f"Batch and pilot counters differ for {lang}")
                require(ent.get("scenarios_attempted")==15,"OBS_PILOT_INCOMPLETE",f"Missing scenarios for {lang}")
                all_lang_counts[lang]=counts
                if lang in selected:
                    langrows.append({"language":lang,"candidate_count":counts["candidate_for_review"],
                        "failed_count":counts["probe_failed"],"timeout_count":counts["timeout"],
                        "unverified_count":counts["unverified"],"scenario_count":15,
                        "technical_status":ent["status"],"human_review_status":"NOT_REVIEWED",
                        "practical_generation_status":"unverified","canonical_readiness":"R0",
                        "source_report_sha256":hashes[report_path][0]})
            published_totals=summary.get("totals",{})
            require(all(type(published_totals.get(k)) is int and published_totals[k]==v for k,v in totals.items()),
                    "OBS_PILOT_INCONSISTENT","Aggregate pilot counters differ")
            require(published_totals.get("languages_unattempted")==0 and
                    published_totals.get("languages_attempted")==len(requested),
                    "OBS_PILOT_INCOMPLETE","Full pilot was not completed for all source languages")
            require(len(scenrows)==15*len(selected),"OBS_PILOT_INCOMPLETE","Selected scenario count mismatch")
            # Independent file digests, not source-authenticated manifest signatures.
            treehash=hashlib.sha256()
            for name,(fh,bytes_) in sorted(hashes.items()):
                treehash.update((name+"\0"+fh+"\0"+str(bytes_)+"\n").encode("utf-8"))
            result=PilotImport(batch_id=bid,archive_sha256=digest,archive_bytes=before.st_size,
                member_count=len(hashes),recalculated_members_sha256=treehash.hexdigest(),
                started_at=summary["started_at"],finished_at=summary["finished_at"],
                source_status="completed_unverified",source_languages=tuple(requested),
                selected=selected,totals=totals,languages=langrows,scenarios=scenrows,
                warnings=warnings,imported_at=utcnow())
    except (zipfile.BadZipFile, OSError, EOFError, RuntimeError) as exc:
        raise ObservatoryError("OBS_ZIP_INTEGRITY",f"Invalid or unreadable ZIP: {type(exc).__name__}") from exc
    after=f.stat()
    require((before.st_ino,before.st_size,before.st_mtime_ns)==(after.st_ino,after.st_size,after.st_mtime_ns),
            "OBS_SOURCE_CHANGED","ZIP changed during import")
    return result
