"""Read-only Observatory consumer for versioned Wordbench practical reports.

This prototype does NOT change Observatory R0-R7 maturity/readiness. It reports
application suitability as a separate dimension. It never compiles GF.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path, PurePosixPath


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def verified_source(report_path: Path, profile: dict, report: dict) -> tuple[bool, str]:
    """Verify source run, its manifest, and all required scenario gold evidence."""
    summary_file, manifest_file = report_path.parent / "summary.json", report_path.parent / "manifest.json"
    if not summary_file.is_file() or not manifest_file.is_file():
        return False, "source_summary_or_manifest_missing"
    try:
        manifest = _json(manifest_file)
        summary = _json(summary_file)
        if manifest.get("schema_id") != "gf-wordbench.artifact-manifest" or manifest.get("schema_version") != "1.0":
            return False, "unsupported_manifest_schema"
        if summary.get("schema_id") != "gf-wordbench.run-summary" or summary.get("schema_version") != "1.0":
            return False, "unsupported_summary_schema"
        entries = manifest.get("artifacts")
        if not isinstance(entries, list):
            return False, "invalid_manifest_artifacts"
        verified = False
        for entry in entries:
            if not isinstance(entry, dict):
                return False, "invalid_manifest_entry"
            path = entry.get("path")
            if not isinstance(path, str) or path.startswith("/") or "\\" in path or ".." in PurePosixPath(path).parts:
                return False, "unsafe_manifest_path"
            file = (report_path.parent / path).resolve()
            if not file.is_relative_to(report_path.parent.resolve()) or not file.is_file():
                return False, "missing_manifest_artifact"
            if file.stat().st_size != entry.get("size_bytes") or _sha256(file) != entry.get("sha256"):
                return False, "manifest_hash_mismatch"
            if path == "summary.json" and entry.get("role") == "machine_summary":
                verified = True
        if not verified:
            return False, "summary_not_declared_in_manifest"
        if report.get("wordbench_run_id") != summary.get("metadata", {}).get("run_id") or report.get("language_key") != summary.get("metadata", {}).get("project_id"):
            return False, "source_identity_mismatch"
        if report.get("wordbench_run_status") != summary.get("totals", {}).get("overall_status"):
            return False, "source_status_mismatch"
        if summary.get("totals", {}).get("overall_status") not in ("OK", "FAIL", "ERROR"):
            return False, "invalid_source_run_status"
        items = summary.get("scenario_results", [])
        if not isinstance(items, list):
            return False, "invalid_scenario_results"
        scenarios = {item.get("scenario_id"): item for item in items if isinstance(item, dict)}
        if len(scenarios) != len(items):
            return False, "duplicate_scenario_ids"
        # Independently confirm all required claims. Unknown/failed capabilities
        # are still visible in the report, but cannot confer readiness.
        caps = report.get("capabilities")
        if not isinstance(caps, list) or len(caps) != len(profile["capabilities"]):
            return False, "capability_count_mismatch"
        actual = {cap.get("id"): cap for cap in caps if isinstance(cap, dict)}
        if len(actual) != len(caps):
            return False, "duplicate_capability_claim"
        run_ok = summary["totals"]["overall_status"] == "OK" and summary["metadata"].get("no_compile") is not True
        for cap in profile["capabilities"]:
            claimed = actual.get(cap["id"])
            if not isinstance(claimed, dict) or claimed.get("required") is not cap["required"] or claimed.get("domains") != cap["domains"]:
                return False, "capability_claim_mismatch"
            statuses = []
            for sid in cap["scenario_ids"]:
                item = scenarios.get(sid)
                if not item or item.get("status") not in ("OK", "FAIL", "ERROR", "SKIPPED"):
                    statuses.append("unverified")
                elif item["status"] in ("FAIL", "ERROR") or item.get("timed_out") is True or (item["status"] == "OK" and item.get("exit_code") != 0):
                    statuses.append("failed")
                elif (item["status"] == "OK" and item.get("gold_match") is True
                      and item.get("gold_path") and item.get("normalized_output_path")
                      and all(sec.get("completed", False) for sec in item.get("sections", []) if isinstance(sec, dict))):
                    statuses.append("passed")
                else:
                    statuses.append("unverified")
            expected = "failed" if "failed" in statuses else ("passed" if set(statuses) == {"passed"} and run_ok else "unverified")
            if claimed.get("status") != expected:
                return False, "capability_claim_unsubstantiated"
        expected_domains = []
        for domain in profile["domains"]:
            values = [actual[c["id"]]["status"] for c in profile["capabilities"] if c["required"] and domain in c["domains"]]
            expected_domains.append("ready" if values and set(values) == {"passed"} and run_ok else ("needs_work" if "failed" in values else "unverified"))
        expected_overall = "ready" if set(expected_domains) == {"ready"} else ("needs_work" if "needs_work" in expected_domains else "unverified")
        if report.get("status") != expected_overall:
            return False, "overall_claim_unsubstantiated"
        return True, "verified_wordbench_manifest"
    except (OSError, ValueError, TypeError, AttributeError, KeyError):
        return False, "evidence_verification_error"


def aggregate(inventory_path: Path, profile_path: Path, reports_root: Path, identity_map: dict[str, str] | None = None) -> dict:
    inv, profile = _json(inventory_path), _json(profile_path)
    if inv.get("schema_id") != "gf-practical.rgl-inventory" or inv.get("schema_version") != "1.0":
        raise ValueError("unsupported inventory schema")
    if profile.get("schema_id") != "gf-practical.profile" or profile.get("schema_version") != "1.0":
        raise ValueError("unsupported practical profile schema")
    profile_digest = _sha256(profile_path)
    aliases = identity_map or {}
    if len(set(aliases.values())) != len(aliases):
        raise ValueError("identity map must not map two RGL languages to the same project")
    reports: dict[str, tuple[Path, dict]] = {}
    for file in sorted(reports_root.rglob("practical_coverage.json")):
        if file.is_symlink() or not file.is_file():
            continue
        doc = _json(file)
        if doc.get("schema_id") != "gf-practical.coverage-result" or doc.get("schema_version") != "1.0":
            continue
        key = doc.get("language_key")
        if not isinstance(key, str) or not key or key in reports:
            raise ValueError(f"duplicate or invalid practical report language: {key!r}")
        reports[key] = (file, doc)
    outputs = []
    for lang in inv["languages"]:
        code = lang["code"]
        key = aliases.get(code, code)
        found = reports.get(key)
        base = {"code": code, "project_id": key, "source_dirs": lang.get("source_dirs", []),
                "structural_status": lang.get("structural_status"), "structural_gaps": lang.get("structural_gaps", [])}
        if found is None:
            base.update(status="unverified", evidence_status="missing", domains=[], missing=[], unverified=[x["id"] for x in profile["capabilities"] if x["required"]])
        else:
            path, doc = found
            consistent = doc.get("profile_id") == profile.get("profile_id") and doc.get("profile_version") == profile.get("profile_version") and doc.get("profile_sha256") == profile_digest
            proven, why = verified_source(path, profile, doc) if consistent else (False, "profile_mismatch")
            # Fail closed: a readiness claim requires intact Wordbench evidence.
            status = doc.get("status") if proven and doc.get("status") in ("ready", "needs_work", "unverified") else "unverified"
            base.update(status=status, evidence_status=why, report_path=str(path),
                        domains=doc.get("domains", []) if proven else [],
                        missing=[x["id"] for x in doc.get("capabilities", []) if x.get("required") and x.get("status") == "failed"] if proven else [],
                        unverified=[x["id"] for x in doc.get("capabilities", []) if x.get("required") and x.get("status") == "unverified"] if proven else [x["id"] for x in profile["capabilities"] if x["required"]])
        outputs.append(base)
    counts = {state: sum(x["status"] == state for x in outputs) for state in ("ready", "needs_work", "unverified")}
    return {"schema_id": "gf-practical.observatory-catalog", "schema_version": "1.0",
            "profile_id": profile["profile_id"], "profile_sha256": profile_digest,
            "counts": counts, "languages": outputs,
            "note": "Application readiness is distinct from R0-R7. Unverified is not failure or missing linguistic capability."}


def write_catalog(result: dict, json_out: Path, csv_out: Path | None = None) -> None:
    json_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    if csv_out:
        csv_out.parent.mkdir(parents=True, exist_ok=True)
        with csv_out.open("w", encoding="utf-8", newline="") as handle:
            w = csv.writer(handle)
            w.writerow(["code", "project_id", "status", "evidence_status", "missing", "unverified", "structural_gaps"])
            for item in result["languages"]:
                w.writerow([item["code"], item["project_id"], item["status"], item["evidence_status"], ";".join(item["missing"]), ";".join(item["unverified"]), ";".join(item["structural_gaps"])])


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inventory", type=Path, required=True)
    p.add_argument("--practical-profile", type=Path, required=True)
    p.add_argument("--reports-root", type=Path, required=True)
    p.add_argument("--identity-map", type=Path)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--csv", type=Path)
    args = p.parse_args(argv)
    aliases = _json(args.identity_map) if args.identity_map else None
    catalog = aggregate(args.inventory, args.practical_profile, args.reports_root, aliases)
    write_catalog(catalog, args.output, args.csv)
    print(f"Observatory: {catalog['counts']} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
