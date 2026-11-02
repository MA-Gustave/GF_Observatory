# -*- coding: utf-8 -*-
"""GF Observatory — diagnostic graphique autonome pour Windows / Python 3.10+.

Inventaire RGL et agrégation des preuves WordBench; sources en lecture seule.
La validation WordBench est une action explicite, bornée et annulable entre langues.
"""
from __future__ import annotations

# --- Embedded inventory parser from tools/rgl_inventory.py ---
"""Discover language candidates in an actual GF RGL checkout (read-only)."""

import argparse
import csv
from datetime import datetime, timezone
import json
from pathlib import Path
import re

# Module names such as ResSqi.gf, CatSqi.gf and Morphologysomething
# may be the only source evidence for a still incomplete language.
# Recognise general module suffixes, but only the four public core names
# contribute to the structural checklist.  No semantic capability is inferred.
MODULE = re.compile(r"^([A-Z][A-Za-z0-9_]*?)([A-Z][a-z]{2})\.gf$")


def inventory(rgl_root: Path) -> dict:
    root = Path(rgl_root).resolve(strict=True)
    src = root / "src" if (root / "src").is_dir() else root
    if not src.is_dir():
        raise ValueError(f"RGL source directory not found: {src}")
    found: dict[str, dict] = {}
    # Include auxiliary resources too: they identify incomplete languages.
    for path in sorted(src.rglob("*.gf")):
        if path.is_symlink() or not path.is_file():
            continue
        match = MODULE.fullmatch(path.name)
        if match is None:
            continue
        role, code = match.groups()
        if len(path.relative_to(src).parts) > 5:
            continue
        info = found.setdefault(code, {"code": code, "modules": {}, "source_dirs": set()})
        info["modules"].setdefault(role, []).append(path.relative_to(root).as_posix())
        info["source_dirs"].add(path.parent.relative_to(root).as_posix())
    # Exclude RGL support-module pseudo-codes, even in the standalone .pyw.
    # Partial Cat/Res modules remain eligible (e.g. Sqi).
    eligible_roles = {"Grammar", "Syntax", "Paradigms", "Lang", "All", "Cat", "Res",
                      "Noun", "Verb", "Adjective", "Phrase", "Sentence", "Question"}
    technical_dirs = {"TEMPLATE", "prelude", "abstract_ext", "abstract_to_api"}
    filtered = {}
    for code, info in found.items():
        if code in {"Abs", "Cnc", "Ext", "TMP"}:
            continue
        has_language_module = any(
            role in eligible_roles and any(
                not set(Path(relative).parts).intersection(technical_dirs)
                for relative in paths
            ) for role, paths in info["modules"].items()
        )
        if has_language_module:
            filtered[code] = info
    found = filtered
    # The CSV is advisory: do not invent implementation status or treat a listed
    # language as implemented when there are no source files.
    csv_path = root / "languages.csv"
    if csv_path.exists():
        with csv_path.open(encoding="utf-8-sig", newline="") as f:
            for row in csv.reader(f):
                cells = [v.strip() for v in row]
                for i, item in enumerate(cells):
                    if item in found and i + 1 < len(cells) and len(cells[i+1]) > 3:
                        found[item].setdefault("name_hint", cells[i+1])
    languages = []
    for code, info in sorted(found.items()):
        roles = {key: sorted(paths) for key, paths in sorted(info["modules"].items())}
        missing = sorted({"Grammar", "Syntax", "Paradigms", "Lang"} - set(roles))
        languages.append({"code": code, "name_hint": info.get("name_hint"),
                          "modules": roles, "module_count": sum(len(paths) for paths in roles.values()),
                          "source_dirs": sorted(info["source_dirs"]),
                          "structural_gaps": missing, "structural_status": "candidate" if "Syntax" in roles else "partial_candidate"})
    return {"schema_id": "gf-practical.rgl-inventory", "schema_version": "1.0",
            "source_root": str(root), "generated_at": datetime.now(timezone.utc).isoformat(),
            "languages": languages, "language_count": len(languages),
            "note": "RGL filename discovery only (including partial/auxiliary modules); never proof of grammatical or practical readiness."}



# --- Embedded read-only consumer from tools/practical_catalog.py ---
"""Read-only Observatory consumer for versioned Wordbench practical reports.

This prototype does NOT change Observatory R0-R7 maturity/readiness. It reports
application suitability as a separate dimension. It never compiles GF.
"""

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



DEFAULT_PROFILE_JSON = '{\n  "schema_id": "gf-practical.profile",\n  "schema_version": "1.0",\n  "profile_id": "encyclopedic-procedural",\n  "profile_version": "1.0",\n  "description": "Functional semantic coverage; morphology and tense selection are language-specific.",\n  "domains": [\n    "encyclopedic",\n    "procedural"\n  ],\n  "capabilities": [\n    {\n      "id": "factual-present",\n      "domains": [\n        "encyclopedic",\n        "procedural"\n      ],\n      "required": true,\n      "description": "Énoncer un fait ou un état actuel",\n      "scenario_ids": [\n        "factual-present"\n      ]\n    },\n    {\n      "id": "past-event",\n      "domains": [\n        "encyclopedic"\n      ],\n      "required": true,\n      "description": "Décrire un événement révolu",\n      "scenario_ids": [\n        "past-event"\n      ]\n    },\n    {\n      "id": "past-state",\n      "domains": [\n        "encyclopedic"\n      ],\n      "required": true,\n      "description": "Décrire un état ou une habitude passée",\n      "scenario_ids": [\n        "past-state"\n      ]\n    },\n    {\n      "id": "future-reference",\n      "domains": [\n        "encyclopedic",\n        "procedural"\n      ],\n      "required": true,\n      "description": "Exprimer une référence future",\n      "scenario_ids": [\n        "future-reference"\n      ]\n    },\n    {\n      "id": "factual-negation",\n      "domains": [\n        "encyclopedic",\n        "procedural"\n      ],\n      "required": true,\n      "description": "Nier une proposition",\n      "scenario_ids": [\n        "factual-negation"\n      ]\n    },\n    {\n      "id": "temporal-order",\n      "domains": [\n        "encyclopedic",\n        "procedural"\n      ],\n      "required": true,\n      "description": "Exprimer une séquence temporelle",\n      "scenario_ids": [\n        "temporal-order"\n      ]\n    },\n    {\n      "id": "condition-real",\n      "domains": [\n        "encyclopedic",\n        "procedural"\n      ],\n      "required": true,\n      "description": "Exprimer une condition réaliste",\n      "scenario_ids": [\n        "condition-real"\n      ]\n    },\n    {\n      "id": "possibility",\n      "domains": [\n        "encyclopedic"\n      ],\n      "required": true,\n      "description": "Exprimer une possibilité sans la convertir en fait",\n      "scenario_ids": [\n        "possibility"\n      ]\n    },\n    {\n      "id": "source-attribution",\n      "domains": [\n        "encyclopedic"\n      ],\n      "required": true,\n      "description": "Attribuer une affirmation à une source",\n      "scenario_ids": [\n        "source-attribution"\n      ]\n    },\n    {\n      "id": "quantity",\n      "domains": [\n        "encyclopedic",\n        "procedural"\n      ],\n      "required": true,\n      "description": "Exprimer des nombres et des mesures",\n      "scenario_ids": [\n        "quantity"\n      ]\n    },\n    {\n      "id": "location",\n      "domains": [\n        "encyclopedic",\n        "procedural"\n      ],\n      "required": true,\n      "description": "Exprimer des lieux et des relations spatiales",\n      "scenario_ids": [\n        "location"\n      ]\n    },\n    {\n      "id": "instruction",\n      "domains": [\n        "procedural"\n      ],\n      "required": true,\n      "description": "Exprimer une directive",\n      "scenario_ids": [\n        "instruction"\n      ]\n    },\n    {\n      "id": "prohibition",\n      "domains": [\n        "procedural"\n      ],\n      "required": true,\n      "description": "Exprimer une interdiction",\n      "scenario_ids": [\n        "prohibition"\n      ]\n    },\n    {\n      "id": "obligation",\n      "domains": [\n        "procedural"\n      ],\n      "required": true,\n      "description": "Exprimer une obligation",\n      "scenario_ids": [\n        "obligation"\n      ]\n    },\n    {\n      "id": "conditional-instruction",\n      "domains": [\n        "procedural"\n      ],\n      "required": true,\n      "description": "Donner une instruction conditionnelle",\n      "scenario_ids": [\n        "conditional-instruction"\n      ]\n    },\n    {\n      "id": "anteriority",\n      "domains": [\n        "encyclopedic",\n        "procedural"\n      ],\n      "required": false,\n      "description": "Expliciter l’antériorité",\n      "scenario_ids": [\n        "anteriority"\n      ]\n    },\n    {\n      "id": "process-ongoing",\n      "domains": [\n        "encyclopedic"\n      ],\n      "required": false,\n      "description": "Décrire un processus en cours",\n      "scenario_ids": [\n        "process-ongoing"\n      ]\n    },\n    {\n      "id": "passive-or-rephrase",\n      "domains": [\n        "encyclopedic",\n        "procedural"\n      ],\n      "required": false,\n      "description": "Exprimer une relation patient-agent",\n      "scenario_ids": [\n        "passive-or-rephrase"\n      ]\n    },\n    {\n      "id": "counterfactual",\n      "domains": [\n        "encyclopedic"\n      ],\n      "required": false,\n      "description": "Exprimer une hypothèse contraire aux faits",\n      "scenario_ids": [\n        "counterfactual"\n      ]\n    },\n    {\n      "id": "habitual",\n      "domains": [\n        "encyclopedic"\n      ],\n      "required": false,\n      "description": "Exprimer une habitude ou récurrence",\n      "scenario_ids": [\n        "habitual"\n      ]\n    }\n  ]\n}\n'
# --- Standalone WordBench bounded runner (mirrors tools/wordbench_runner.py) ---


import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import threading
from typing import Callable


PUBLIC_ROLES = ("Syntax", "Grammar", "Lang", "Cat", "Res")


def resolve_wordbench_root(preferred: Path, workspace: Path | None = None) -> Path | None:
    """Locate the real WordBench package, even under an extra ZIP/repository folder.

    Search is deliberately bounded: no full-workspace recursive walk and no
    environment modification until the caller launches WordBench explicitly.
    """
    roots = [Path(preferred).expanduser()]
    if workspace is not None:
        roots.append(Path(workspace).expanduser())
    seen: set[Path] = set()

    def candidates(base: Path):
        yield base
        if base.name.casefold() == 'src':
            yield base.parent
        for name in ('GF_Wordbench', 'GF_WordBench', 'gf-wordbench', 'wordbench'):
            yield base / name
        # Common extraction layout: GF_Wordbench/GF_Wordbench/src/...
        # Only inspect immediate, WordBench-named directories.
        if base.is_dir():
            try:
                for child in sorted(base.iterdir()):
                    if child.is_dir() and 'wordbench' in child.name.casefold().replace('-', '').replace('_', ''):
                        yield child
                        for name in ('GF_Wordbench', 'GF_WordBench', 'gf-wordbench', 'wordbench'):
                            yield child / name
            except OSError:
                pass

    for base in roots:
        for candidate in candidates(base):
            candidate = candidate.resolve()
            if candidate in seen:
                continue
            seen.add(candidate)
            if (candidate / 'src' / 'gf_wordbench' / '__init__.py').is_file():
                return candidate
    return None


def wordbench_missing_message(path: Path) -> str:
    return ("Dépôt WordBench introuvable.\n\n"
            f"Chemin indiqué : {path}\n\n"
            "Choisis le dossier qui contient directement :\n"
            "  src\\gf_wordbench\\__init__.py\n\n"
            "Si tu as extrait le ZIP d'origine, vérifie aussi le dossier imbriqué :\n"
            "  GF_Wordbench\\GF_Wordbench\n\n"
            "Clique sur « Détecter WordBench » ou « Parcourir… ».")



def language_source(rgl_root: Path, language: dict) -> tuple[Path | None, str]:
    """Choose one real source module from the inventory, never an inferred filename."""
    root = rgl_root.resolve()
    modules = language.get("modules", {})
    for role in PUBLIC_ROLES:
        for relative in modules.get(role, []):
            # Inventory paths are untrusted; refuse escaping RGL or symlinks.
            path = (root / relative).resolve()
            if not path.is_relative_to(root) or not path.is_file() or path.is_symlink():
                continue
            # Prefer modules in language directories over shared API/prelude.
            if any(part in {"api", "prelude", "TEMPLATE", "abstract_ext"} for part in path.relative_to(root).parts):
                continue
            return path, role
    return None, "no_public_module"


def python_console() -> Path:
    exe = Path(sys.executable)
    if os.name == "nt" and exe.name.lower() == "pythonw.exe":
        candidate = exe.with_name("python.exe")
        if candidate.is_file():
            return candidate
    return exe


def wordbench_environment(wordbench_root: Path) -> dict[str, str]:
    src = (wordbench_root / "src").resolve()
    if not (src / "gf_wordbench" / "__init__.py").is_file():
        raise ValueError(wordbench_missing_message(wordbench_root))
    env = dict(os.environ)
    env["PYTHONPATH"] = str(src) + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    return env


def wordbench_language_key(source: Path, rgl_root: Path) -> str:
    src = rgl_root / "src" if (rgl_root / "src").is_dir() else rgl_root
    try:
        return source.parent.relative_to(src).as_posix()
    except ValueError:
        return source.parent.name


def make_command(
    *, code: str, source: Path, wordbench_root: Path, rgl_root: Path,
    output_dir: Path, mode: str, practical_profile: Path | None = None,
    validation_profiles_root: Path | None = None, gf_executable: Path | None = None,
    python_executable: Path | None = None,
) -> list[str]:
    exe = str(python_executable or python_console())
    common = ["--language-path", str(source.parent), "--rgl-root", str(rgl_root), "--output-root", str(output_dir / "wb_artifacts")]
    if gf_executable is not None:
        common.extend(["--gf-executable", str(gf_executable)])
    if mode == "quick":
        # Canonical WB CLI uses --gf-exe and --out-root, not practical CLI spellings.
        cmd = [exe, "-m", "gf_wordbench", "validate", "--mode", "quick",
               "--language-path", str(source.parent), "--target", str(source),
               "--rgl-root", str(rgl_root), "--out-root", str(output_dir / "wb_artifacts"),
               "--compile-timeout", "70", "--no-compare-previous"]
        if gf_executable is not None:
            cmd.extend(["--gf-exe", str(gf_executable)])
        return cmd
    if mode == "practical":
        if practical_profile is None or not practical_profile.is_file():
            raise ValueError("Profil sémantique pratique manquant")
        if validation_profiles_root is None:
            raise ValueError("Dossier des profils WordBench par langue manquant")
        toml = validation_profiles_root / code / "project.toml"
        if not toml.is_file():
            raise ValueError(f"Scénarios GF et profil WordBench non configurés pour {code}: {toml}")
        cmd = [exe, "-m", "gf_wordbench.practical.cli", "run", *common,
               "--validation-profile", str(toml), "--practical-profile", str(practical_profile),
               "--language-key", wordbench_language_key(source, rgl_root)]
        if gf_executable is not None:
            cmd.extend(["--gf-executable", str(gf_executable)])
        return cmd
    raise ValueError("Mode WordBench invalide (quick ou practical)")


def _stop_process(proc: subprocess.Popen) -> None:
    if proc.poll() is not None:
        return
    if os.name == "nt":
        try:
            subprocess.run(["taskkill", "/PID", str(proc.pid), "/T", "/F"],
                           capture_output=True, timeout=8, check=False)
        except (OSError, subprocess.TimeoutExpired):
            proc.kill()
    else:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except OSError:
            proc.kill()


def _execute(cmd: list[str], env: dict[str, str], timeout: int, stop: threading.Event) -> tuple[str, int | None, str]:
    if stop.is_set():
        return "cancelled", None, "Annulation demandée"
    kwargs = {"stdout": subprocess.PIPE, "stderr": subprocess.STDOUT, "text": True,
              "encoding": "utf-8", "errors": "replace", "env": env}
    if os.name == "nt":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    proc = subprocess.Popen(cmd, **kwargs)
    # communicate(timeout) is bounded; caller is responsible for log truncation.
    # Cancellation between individual runs is supported; current run finishes or times out.
    try:
        stdout, _ = proc.communicate(timeout=timeout)
        return ("ok" if proc.returncode == 0 else "error"), proc.returncode, stdout or ""
    except subprocess.TimeoutExpired:
        _stop_process(proc)
        try:
            stdout, _ = proc.communicate(timeout=4)
        except subprocess.TimeoutExpired:
            proc.kill()
            stdout, _ = proc.communicate()
        return "timeout", None, (stdout or "") + "\n[Observatory] Délai WordBench dépassé."


def run_batch(
    *, inventory: dict, rgl_root: Path, wordbench_root: Path, output_dir: Path,
    codes: list[str], mode: str = "quick", timeout: int = 90,
    practical_profile: Path | None = None, validation_profiles_root: Path | None = None,
    gf_executable: Path | None = None, stop: threading.Event | None = None,
    on_progress: Callable[[int, int, str, str], None] | None = None,
    python_executable: Path | None = None,
) -> dict:
    """Execute only the explicit set, sequentially; never guess missing golden fixtures."""
    if not 5 <= timeout <= 3600:
        raise ValueError("Le délai doit être entre 5 et 3600 secondes")
    if mode not in {"quick", "practical"}:
        raise ValueError("Mode invalide")
    rgl_root, wordbench_root, output_dir = (Path(x).resolve() for x in (rgl_root, wordbench_root, output_dir))
    resolved_wb = resolve_wordbench_root(wordbench_root)
    if resolved_wb is None:
        raise ValueError(wordbench_missing_message(wordbench_root))
    wordbench_root = resolved_wb
    if output_dir == rgl_root or output_dir.is_relative_to(rgl_root) or output_dir == wordbench_root or output_dir.is_relative_to(wordbench_root):
        raise ValueError("Dossier de sortie interdit dans la RGL ou WordBench")
    env = wordbench_environment(wordbench_root)
    if mode == "practical" and not (wordbench_root / "src/gf_wordbench/practical/cli.py").is_file():
        raise ValueError("Extension gf_wordbench.practical absente du WordBench installé")
    if not isinstance(inventory.get("languages"), list):
        raise ValueError("Inventaire incorrect")
    by_code = {x["code"]: x for x in inventory["languages"]}
    wanted = list(dict.fromkeys(codes))
    if not wanted or any(code not in by_code for code in wanted):
        raise ValueError("Sélection de langues vide ou inconnue")
    stop = stop or threading.Event()
    log_dir = output_dir / "wordbench_logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    records = []
    for index, code in enumerate(wanted, 1):
        if stop.is_set():
            break
        lang = by_code[code]
        source, role = language_source(rgl_root, lang)
        record: dict = {"code": code, "mode": mode, "source_module": str(source) if source else None,
                        "status": "not_tested", "exit_code": None, "reason": None, "log_path": None,
                        "wordbench_language_key": wordbench_language_key(source, rgl_root) if source else None}
        if source is None:
            record["reason"] = role
        else:
            try:
                cmd = make_command(code=code, source=source, wordbench_root=wordbench_root,
                                   rgl_root=rgl_root, output_dir=output_dir, mode=mode,
                                   practical_profile=practical_profile,
                                   validation_profiles_root=validation_profiles_root,
                                   gf_executable=gf_executable, python_executable=python_executable)
                status, exit_code, captured = _execute(cmd, env, timeout, stop)
                record["status"] = status
                record["exit_code"] = exit_code
                if status == "error":
                    if "The validation application requires a resolved RunConfig" in captured:
                        record["reason"] = "wordbench_runconfig_unresolved"
                    else:
                        record["reason"] = "wordbench_exit_nonzero"
                elif status == "timeout":
                    record["reason"] = "wordbench_timeout"
                else:
                    record["reason"] = None
                log_file = log_dir / f"{code}_{mode}.log"
                # Keep capped logs, and do not persist executable command or environment secrets.
                log_file.write_text(captured[-600_000:], encoding="utf-8")
                record["log_path"] = str(log_file)
            except (OSError, ValueError) as exc:
                record["status"] = "not_tested"
                record["reason"] = f"{type(exc).__name__}: {exc}"
        records.append(record)
        if on_progress:
            on_progress(index, len(wanted), code, record["status"])
    # Merge aliases: separate UI runs must not erase prior project identities.
    alias_path = output_dir / "wordbench_identity_map.json"
    try:
        aliases = json.loads(alias_path.read_text(encoding="utf-8")) if alias_path.is_file() else {}
        if not isinstance(aliases, dict):
            aliases = {}
    except (OSError, ValueError):
        aliases = {}
    aliases.update({r['code']: r['wordbench_language_key'] for r in records if r.get('wordbench_language_key')})
    if len(set(aliases.values())) == len(aliases):
        alias_path.write_text(json.dumps(aliases, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result = {"schema_id": "gf-observatory.wordbench-execution", "schema_version": "1.0",
              "mode": mode, "generated_at": datetime.now(timezone.utc).isoformat(),
              "rgl_root": str(rgl_root), "wordbench_root": str(wordbench_root),
              "requested": wanted, "completed": len(records), "cancelled": stop.is_set(),
              "results": records,
              "note": "quick = module compile/check only, never evidence of semantic readiness; practical requires verified WordBench gold scenarios"}
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / ("wordbench_quick_results.json" if mode == "quick" else "wordbench_practical_executions.json")
    if mode == "quick" and path.is_file():
        try:
            previous = json.loads(path.read_text(encoding="utf-8"))
            if (previous.get("schema_id") == result["schema_id"] and previous.get("rgl_root") == str(rgl_root)):
                merged = {r["code"]: r for r in previous.get("results", []) if isinstance(r, dict) and "code" in r}
                merged.update({r["code"]: r for r in records})
                result["results"] = [merged[key] for key in sorted(merged)]
        except (OSError, ValueError, TypeError):
            pass
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temp.replace(path)
    return result


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inventory", type=Path, required=True)
    p.add_argument("--rgl-root", type=Path, required=True)
    p.add_argument("--wordbench-root", type=Path, required=True)
    p.add_argument("--output-dir", type=Path, required=True)
    p.add_argument("--mode", choices=("quick", "practical"), default="quick")
    p.add_argument("--codes", nargs="+", required=True)
    p.add_argument("--timeout", type=int, default=90)
    p.add_argument("--practical-profile", type=Path)
    p.add_argument("--validation-profiles-root", type=Path)
    p.add_argument("--gf-executable", type=Path)
    args = p.parse_args(argv)
    data = json.loads(args.inventory.read_text(encoding="utf-8"))
    results = run_batch(inventory=data, rgl_root=args.rgl_root, wordbench_root=args.wordbench_root,
                        output_dir=args.output_dir, codes=args.codes, mode=args.mode, timeout=args.timeout,
                        practical_profile=args.practical_profile,
                        validation_profiles_root=args.validation_profiles_root, gf_executable=args.gf_executable,
                        on_progress=lambda i,n,c,s: print(f"{i}/{n} {c}: {s}",flush=True))
    print(f"{results['completed']} langues traitées ; {results['mode']}")
    return 0



# ---------------------------------------------------------------------------
# Standalone UI and diagnostic workflow.  No third-party dependencies.
# ---------------------------------------------------------------------------
import os
import platform
import queue
import shutil
import sys
import threading
import traceback
from tkinter import Tk, StringVar, Text, END, filedialog, messagebox, ttk
from typing import Any

APP_VERSION = "0.3.3-wordbench-diagnostics"
REPOSITORIES = ("GF_Observatory", "GF_Wordbench", "ars-magna-lulli", "GF_RGL_AI_Compendium")


def find_rgl_root(workspace: Path) -> Path | None:
    """Suggest a small known set of root paths; never traverse the whole disk."""
    roots = [
        workspace / "gf" / "lib", workspace / "GF" / "lib",
        workspace / "gf-rgl", workspace / "GF-RGL", workspace / "RGL",
        workspace / "rgl", workspace / "gf", workspace / "GF",
        workspace / "gf" / "lib" / "src",
        workspace / "GF" / "lib" / "src", workspace,
    ]
    for root in roots:
        for src in (root / "src", root):
            if src.is_dir() and any((src / d).is_dir() for d in ("english", "french", "albanian", "api", "german")):
                return root
    return None


def collect_environment(workspace: Path, root: Path) -> dict[str, Any]:
    tools = {}
    for name in ("gf", "python", "py", "pwsh", "git"):
        tool_path = shutil.which(name)
        tools[name] = {"found": tool_path is not None, "path": tool_path,
                       "version": None, "version_note": "Non exécuté (diagnostic sans processus externe)"}
    repos = {}
    for name in REPOSITORIES:
        folder = workspace / name
        repos[name] = {"exists": folder.is_dir(), "path": str(folder)}
    return {"schema_id": "gf-practical.environment-diagnostic", "schema_version": "1.0",
            "app_version": APP_VERSION,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "platform": platform.platform(), "python_version": platform.python_version(),
            "workspace_root": str(workspace), "workspace_found": workspace.is_dir(),
            "rgl_root": str(root), "rgl_found": root.is_dir(),
            "tools": tools, "repositories": repos,
            "note": "Sans compilation GF, sans WordBench, sans version -- exécutée; aucune modification des sources."}


def _load_identity_map(path: Path | None) -> dict[str, str]:
    if path is None:
        return {}
    value = _json(path)
    if not all(isinstance(k, str) and isinstance(v, str) and k and v for k, v in value.items()):
        raise ValueError("La carte d'identité doit être un objet JSON code -> project_id.")
    return value


def _ensure_output_safe(out_dir: Path, inputs: list[Path]) -> None:
    dest = out_dir.resolve()
    for source in inputs:
        base = source.resolve()
        if dest == base or dest.is_relative_to(base):
            raise ValueError(f"Le dossier de sortie est situé dans une source scannée : {base}. "
                             "Choisis un répertoire extérieur aux sources.")


def run_diagnostic(
    *, workspace: Path, rgl_root: Path, reports_root: Path | None,
    profile_path: Path, identity_map_path: Path | None, output_dir: Path
) -> dict:
    """Read-only scan plus evidence aggregation; write only in output_dir."""
    workspace = Path(workspace).expanduser()
    rgl_root = Path(rgl_root).expanduser()
    output_dir = Path(output_dir).expanduser()
    if not rgl_root.is_dir():
        raise ValueError(f"La RGL est introuvable : {rgl_root}")
    if not profile_path.is_file():
        raise ValueError(f"Profil introuvable : {profile_path}")
    if reports_root is not None and not reports_root.is_dir():
        raise ValueError(f"Dossier de rapports introuvable : {reports_root}")
    _ensure_output_safe(output_dir, [rgl_root] + ([reports_root] if reports_root is not None else []))
    profile = _json(profile_path)
    if profile.get('schema_id') != 'gf-practical.profile' or profile.get('schema_version') != '1.0':
        raise ValueError("Le profil pratique doit être gf-practical.profile v1.0")
    # Never claim readiness just because the GF module exists.
    inv = inventory(rgl_root)
    auto_aliases = output_dir / 'wordbench_identity_map.json'
    aliases = _load_identity_map(identity_map_path if identity_map_path is not None else (auto_aliases if auto_aliases.is_file() else None))
    diag = collect_environment(workspace, rgl_root)
    diag["language_candidates"] = inv["language_count"]
    generated_reports = output_dir / "wb_artifacts"
    effective_reports = reports_root if reports_root is not None else (generated_reports if generated_reports.is_dir() else None)
    diag["reports_root"] = str(effective_reports) if effective_reports is not None else None
    diag["wordbench_reports_imported"] = effective_reports is not None
    # The versioned profile is copied into the output to freeze a reproducible
    # profile digest without touching WordBench, Observatory or the RGL source.
    output_dir.mkdir(parents=True, exist_ok=True)
    prof_out = output_dir / 'practical_generation_profile.json'
    prof_out.write_bytes(profile_path.read_bytes())
    reports = effective_reports if effective_reports is not None else output_dir / '__aucun_rapport__'
    # Atomic-ish writing: inventory must be on disk before catalog aggregation.
    inv_file = output_dir / 'rgl_inventory.json'
    inv_file.write_text(json.dumps(inv, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    cat = aggregate(inv_file, prof_out, reports, aliases)
    # Explicitly separate the light WordBench module compilation probe from
    # verified semantic practical readiness; never upgrade readiness from quick.
    quick_file = output_dir / 'wordbench_quick_results.json'
    if quick_file.is_file():
        try:
            quick = _json(quick_file)
            if (quick.get('schema_id') == 'gf-observatory.wordbench-execution'
                    and quick.get('mode') == 'quick'
                    and Path(quick.get('rgl_root', '')).resolve() == rgl_root.resolve()):
                by_code = {r['code']: r for r in quick.get('results', []) if isinstance(r, dict) and 'code' in r}
                for row in cat['languages']:
                    record = by_code.get(row['code'])
                    row['wordbench_quick'] = record.get('status', 'not_tested') if record else 'not_tested'
                    row['wordbench_quick_log'] = record.get('log_path') if record else None
                    row['wordbench_quick_reason'] = record.get('reason') if record else None
                    row['wordbench_quick_exit_code'] = record.get('exit_code') if record else None
        except (OSError, ValueError, TypeError):
            pass
    write_catalog(cat, output_dir / 'practical_catalog.json', output_dir / 'practical_catalog.csv')
    (output_dir / 'diagnostic.json').write_text(json.dumps(diag, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')
    summary = ["GF Observatory — Diagnostic des langues (usage pratique)",
               "==============================================", "",
               "Candidats RGL détectés : " + str(inv['language_count']),
               "Langues prêtes (avec preuves WordBench vérifiées) : " + str(cat['counts']['ready']),
               "Langues avec échecs confirmés : " + str(cat['counts']['needs_work']),
               "Langues non vérifiées : " + str(cat['counts']['unverified']), "",
               "RGL : " + str(rgl_root),
               "Rapports WordBench : " + (str(effective_reports) if effective_reports else "non fournis"), "",
               "ATTENTION : un module GF présent n'est pas une preuve de réussite.",
               "'Non vérifiée' signifie absence ou insuffisance de preuve, et non échec.",
               "Le profil pratique ne modifie pas les niveaux R0–R7 d'Observatory.",
               "Cet inventaire ne compile pas GF ; les tests WB sont distincts.", "",
               "Fichiers produits : diagnostic.json, rgl_inventory.json,",
               "practical_catalog.json, practical_catalog.csv, practical_generation_profile.json", ""]
    (output_dir / 'LISEZ_MOI.txt').write_text('\n'.join(summary), encoding='utf-8')
    return {"inventory": inv, "catalog": cat, "diagnostic": diag,
            "output_dir": str(output_dir.resolve())}


class DiagnosticWindow(Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("GF Observatory — Inventaire et diagnostic pratique")
        self.geometry("1250x830")
        self.minsize(950, 600)
        self._events: queue.Queue = queue.Queue()
        self._running = False
        self._rows: dict[str, dict] = {}
        self._result: dict | None = None
        self._last_error: str = ""
        default_ws = Path(r"C:\mycode\Grammatical-Framework") if os.name == 'nt' else Path.home()
        self.workspace = StringVar(value=str(default_ws))
        suggestion = find_rgl_root(default_ws)
        self.rgl_root = StringVar(value=str(suggestion) if suggestion else "")
        self.reports_root = StringVar(value="")
        self.wordbench_root = StringVar(value=str(resolve_wordbench_root(default_ws / 'GF_Wordbench', default_ws) or (default_ws / 'GF_Wordbench')))
        self.validation_profiles_root = StringVar(value="")
        self.wb_mode = StringVar(value="quick")
        self._cancel_wordbench = threading.Event()
        self.profile_path = StringVar(value="")
        self.identity_path = StringVar(value="")
        self.output_dir = StringVar(value=str(Path.home() / "GF_Observatory_Diagnostic"))
        self.filter_text = StringVar(value="")
        self.state_text = StringVar(value="Prêt à inventorier, aucune compilation lancée.")
        self.count_text = StringVar(value="Aucun résultat")
        self._make_ui()
        self.after(120, self._poll)

    def _make_ui(self) -> None:
        outer = ttk.Frame(self, padding=12)
        outer.pack(fill="both", expand=True)
        ttk.Label(outer, text="GF Observatory — Diagnostic RGL / ChatSystem", font=("Segoe UI", 17, "bold")).pack(anchor="w")
        ttk.Label(outer, text="Lecture seule des sources. Inventaire rapide des modules, puis résultats WordBench si disponibles.").pack(anchor="w", pady=(0, 10))
        params = ttk.LabelFrame(outer, text="Sources et sortie", padding=8)
        params.pack(fill="x")
        self._path_row(params, 0, "Workspace", self.workspace, True)
        self._path_row(params, 1, "RGL / GF lib", self.rgl_root, True)
        self._path_row(params, 2, "Rapports WordBench (facultatif)", self.reports_root, True)
        self._path_row(params, 3, "Profil pratique JSON (facultatif)", self.profile_path, False)
        self._path_row(params, 4, "Correspondance des codes JSON (facultatif)", self.identity_path, False)
        self._path_row(params, 5, "Dossier de sortie", self.output_dir, True)
        self._path_row(params, 6, "Dépôt GF WordBench", self.wordbench_root, True)
        self._path_row(params, 7, "Profils WordBench par langue (si tests pratiques)", self.validation_profiles_root, True)
        params.columnconfigure(1, weight=1)
        buttons = ttk.Frame(outer)
        buttons.pack(fill="x", pady=(9, 0))
        self.run_button = ttk.Button(buttons, text="Scanner les langues", command=self._start)
        self.run_button.pack(side="left")
        ttk.Button(buttons, text="Détecter la RGL", command=self._auto).pack(side="left", padx=(7, 0))
        ttk.Button(buttons, text="Détecter WordBench", command=self._auto_wordbench).pack(side="left", padx=(7, 0))
        ttk.Button(buttons, text="Voir les fichiers de sortie", command=self._show_dir).pack(side="left", padx=(7, 0))
        ttk.Label(buttons, textvariable=self.count_text, font=("Segoe UI", 10, "bold")).pack(side="right")
        wb_buttons = ttk.Frame(outer)
        wb_buttons.pack(fill="x", pady=(5, 10))
        ttk.Label(wb_buttons, text="Validation WordBench : ").pack(side="left")
        ttk.Combobox(wb_buttons, textvariable=self.wb_mode, values=("quick", "practical"), state="readonly", width=11).pack(side="left")
        self.wb_selected_button = ttk.Button(wb_buttons, text="Tester sélection", command=lambda: self._start_wordbench(False))
        self.wb_selected_button.pack(side="left", padx=(7, 0))
        self.wb_all_button = ttk.Button(wb_buttons, text="Tester toutes", command=lambda: self._start_wordbench(True))
        self.wb_all_button.pack(side="left", padx=(7, 0))
        self.wb_stop_button = ttk.Button(wb_buttons, text="Arrêter après cette langue", command=self._stop_wordbench, state="disabled")
        self.wb_stop_button.pack(side="left", padx=(7, 0))
        ttk.Button(wb_buttons, text="Voir journal WB", command=self._show_wordbench_log).pack(side="left", padx=(7, 0))
        self.progress = ttk.Progressbar(outer, mode="indeterminate")
        self.progress.pack(fill="x")
        ttk.Label(outer, textvariable=self.state_text).pack(anchor="w", pady=5)
        tabs = ttk.Notebook(outer)
        self.tabs = tabs
        tabs.pack(fill="both", expand=True)
        tab1 = ttk.Frame(tabs, padding=8)
        tab2 = ttk.Frame(tabs, padding=8)
        tabs.add(tab1, text="Langues")
        tabs.add(tab2, text="Diagnostic / explications")
        self.diagnostic_tab = tab2
        toolbar = ttk.Frame(tab1)
        toolbar.pack(fill="x", pady=(0, 5))
        ttk.Label(toolbar, text="Filtrer :").pack(side="left")
        search = ttk.Entry(toolbar, textvariable=self.filter_text)
        search.pack(side="left", fill="x", expand=True, padx=8)
        self.filter_text.trace_add("write", lambda *_: self._render_rows())
        columns = ("code", "structure", "wordbench", "practical", "encyclopedic", "procedural", "failed", "unverified")
        panel = ttk.Frame(tab1)
        panel.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(panel, columns=columns, show="headings", height=12)
        headers = (("code", "Langue"), ("structure", "Structure"), ("wordbench", "WB rapide"), ("practical", "Usage pratique"),
                   ("encyclopedic", "Encyclopédie"), ("procedural", "Instructions"),
                   ("failed", "Échecs"), ("unverified", "Non testées"))
        for field, text in headers:
            self.tree.heading(field, text=text)
            self.tree.column(field, width=110 if field not in ("code", "structure") else 95,
                             minwidth=75, anchor="w")
        self.tree.column("code", width=85, stretch=False)
        self.tree.column("failed", width=75, stretch=False)
        self.tree.column("unverified", width=95, stretch=False)
        scroll = ttk.Scrollbar(panel, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scroll.set)
        self.tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.tree.bind("<<TreeviewSelect>>", self._show_selection)
        ttk.Label(tab1, text="Détails de la langue sélectionnée :").pack(anchor="w", pady=(7, 2))
        self.detail = Text(tab1, height=9, wrap="word", font=("Consolas", 10))
        self.detail.pack(fill="both", expand=False)
        self.detail.configure(state="disabled")
        self.explain = Text(tab2, wrap="word", font=("Consolas", 10))
        self.explain.pack(fill="both", expand=True)
        self._set_text(self.explain, "Aucune analyse encore réalisée.\n\n"
                       "1. Sélectionne le répertoire de ta RGL (la racine qui contient src/).\n"
                       "2. Si tu possèdes des sorties de WordBench, choisis leur dossier.\n"
                       "3. Lance 'Scanner les langues'.\n\n"
                       "Une langue n'est prête que si toutes les fonctions obligatoires ont des preuves vérifiables.\n"
                       "Sans résultats de tests linguistiques, la langue est 'non vérifiée'.\n"
                       "L'inventaire est sans exécution. Le bouton Tester lance explicitement WordBench.\n"
                       "Le mode quick vérifie UN module ciblé ; ne valide aucun scénario sémantique.\n"
                       "Le mode practical exige des profils .gfs et résultats gold propres à la langue.")

    def _path_row(self, parent, idx: int, label: str, variable: StringVar, directory: bool) -> None:
        ttk.Label(parent, text=label).grid(row=idx, column=0, sticky="w", padx=3, pady=3)
        ttk.Entry(parent, textvariable=variable).grid(row=idx, column=1, sticky="ew", padx=5, pady=3)
        def choose() -> None:
            value = filedialog.askdirectory(initialdir=variable.get() or str(Path.home())) if directory else filedialog.askopenfilename(filetypes=[("JSON", "*.json"), ("Tous", "*.*")])
            if value:
                variable.set(value)
        ttk.Button(parent, text="Parcourir…", command=choose).grid(row=idx, column=2, sticky="e", padx=3, pady=3)

    @staticmethod
    def _set_text(widget: Text, content: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", END)
        widget.insert("1.0", content)
        widget.configure(state="disabled")

    def _auto(self) -> None:
        guess = find_rgl_root(Path(self.workspace.get()).expanduser())
        if guess:
            self.rgl_root.set(str(guess))
            self.state_text.set("RGL suggérée : " + str(guess))
        else:
            messagebox.showinfo("RGL", "RGL non repérée automatiquement. Choisis son dossier avec 'Parcourir'.")

    def _auto_wordbench(self) -> None:
        found = resolve_wordbench_root(Path(self.wordbench_root.get()), Path(self.workspace.get()))
        if found:
            self.wordbench_root.set(str(found))
            self.state_text.set("WordBench détecté : " + str(found))
        else:
            messagebox.showwarning("WordBench introuvable", wordbench_missing_message(Path(self.wordbench_root.get())))

    def _show_dir(self) -> None:
        dest = Path(self.output_dir.get()).expanduser()
        if not dest.is_dir():
            messagebox.showinfo("Dossier", "Le dossier de sortie n'existe pas encore.")
            return
        # Display a path; avoid invoking a system shell or external process.
        messagebox.showinfo("Dossier de sortie", "Fichiers créés dans :\n" + str(dest.resolve()))

    @staticmethod
    def _save_error(phase: str, exc: Exception, *, output_dir: Path,
                    protected_paths: list[Path]) -> dict[str, str]:
        """Persist the full error, including traceback, outside the source trees."""
        full = (f"GF Observatory {APP_VERSION} — {phase}\n"
                f"{datetime.now(timezone.utc).isoformat()}\n\n"
                f"{type(exc).__name__}: {exc}\n\n"
                + traceback.format_exc())
        path = None
        try:
            output = output_dir.expanduser().resolve()
            _ensure_output_safe(output, [p for p in protected_paths if p.is_dir()])
            output.mkdir(parents=True, exist_ok=True)
            target = output / 'observatory_last_error.log'
            target.write_text(full, encoding='utf-8')
            path = str(target)
        except (OSError, ValueError):
            pass
        return {"phase": phase, "message": str(exc), "traceback": full, "log_path": path or ""}

    def _show_wordbench_log(self) -> None:
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Journal WordBench", "Sélectionne une langue dans le tableau.")
            return
        item = self._rows.get(selected[0], {})
        log = item.get('wordbench_quick_log')
        if not log:
            messagebox.showinfo("Journal WordBench", "Aucun journal de test rapide n'existe pour cette langue.")
            return
        try:
            path = Path(log).resolve()
            permitted = (Path(self.output_dir.get()).resolve() / 'wordbench_logs').resolve()
            if not path.is_relative_to(permitted) or not path.is_file():
                raise ValueError("Chemin du journal invalide")
            content = path.read_text(encoding='utf-8', errors='replace')[-40_000:]
            self._set_text(self.explain, f"Journal WordBench — {selected[0]}\n{path}\n\n{content}")
            self.tabs.select(self.diagnostic_tab)
        except (OSError, ValueError) as exc:
            messagebox.showerror("Journal WordBench", str(exc))

    def _start(self) -> None:
        if self._running:
            return
        root = self.rgl_root.get().strip()
        if not root:
            messagebox.showerror("RGL manquante", "Choisis le dossier RGL avant de scanner.")
            return
        self._running = True
        self.run_button.configure(state="disabled")
        self._set_busy(True)
        self.state_text.set("Inventaire et lecture des rapports en cours…")
        self.progress.start(12)
        values = dict(workspace=Path(self.workspace.get() or '.'), rgl_root=Path(root),
                      reports_root=Path(self.reports_root.get()) if self.reports_root.get().strip() else None,
                      identity_map_path=Path(self.identity_path.get()) if self.identity_path.get().strip() else None,
                      output_dir=Path(self.output_dir.get()),
                      profile_path=Path(self.profile_path.get()) if self.profile_path.get().strip() else None)
        def worker() -> None:
            try:
                with_profile = values.copy()
                if with_profile['profile_path'] is None:
                    # Standalone bundle, fixed-byte default profile written only
                    # in the designated output directory.
                    out = values['output_dir'].expanduser()
                    _ensure_output_safe(out, [values['rgl_root']] + ([values['reports_root']] if values['reports_root'] else []))
                    out.mkdir(parents=True, exist_ok=True)
                    profile = out / 'default_practical_generation_v1.json'
                    profile.write_text(DEFAULT_PROFILE_JSON, encoding='utf-8')
                    with_profile['profile_path'] = profile
                result = run_diagnostic(**with_profile)
                self._events.put(("success", result))
            except Exception as exc:
                self._events.put(("error", self._save_error("inventaire", exc,
                    output_dir=values['output_dir'], protected_paths=[values['rgl_root']])))
        threading.Thread(target=worker, name="observatory-inventory", daemon=True).start()

    def _set_busy(self, busy: bool) -> None:
        state = "disabled" if busy else "normal"
        self.wb_selected_button.configure(state=state)
        self.wb_all_button.configure(state=state)
        self.run_button.configure(state=state)
        self.wb_stop_button.configure(state="normal" if busy and self._cancel_wordbench.is_set() is False else "disabled")

    def _stop_wordbench(self) -> None:
        self._cancel_wordbench.set()
        self.wb_stop_button.configure(state="disabled")
        self.state_text.set("Annulation demandée : termine le test courant, puis arrête.")

    def _start_wordbench(self, all_languages: bool) -> None:
        if self._running:
            return
        # Keep WordBench out of source folders and use a separate process.
        if not self._result:
            messagebox.showinfo("Inventaire", "Lance d'abord Scanner les langues.")
            return
        selected = [x['code'] for x in self._result['inventory']['languages']] if all_languages else list(self.tree.selection())
        if not selected:
            messagebox.showinfo("Sélection", "Sélectionne une ou plusieurs langues dans le tableau.")
            return
        mode = self.wb_mode.get()
        found_wb = resolve_wordbench_root(Path(self.wordbench_root.get()), Path(self.workspace.get()))
        if found_wb is None:
            messagebox.showwarning("WordBench introuvable", wordbench_missing_message(Path(self.wordbench_root.get())))
            return
        self.wordbench_root.set(str(found_wb))
        if mode == 'practical' and not (found_wb / 'src/gf_wordbench/practical/cli.py').is_file():
            messagebox.showwarning("Extension pratique absente",
                "WordBench est détecté, mais l'extension de validation pratique n'est pas installée.\n\n"
                "Tu peux tester en mode quick. Le mode practical exige l'extension WordBench et les profils de scénarios propres à chaque langue.")
            return
        if all_languages and not messagebox.askyesno("Confirmation", f"Tester {len(selected)} langues, une à la fois, en mode {mode} ?\n"
                                                   "Cela peut prendre du temps. Les sources ne seront pas modifiées."):
            return
        self._running = True
        self._cancel_wordbench.clear()
        self._set_busy(True)
        self.progress.start(12)
        self.state_text.set(f"WordBench {mode} : {len(selected)} langues sélectionnées…")
        values = dict(inventory=self._result['inventory'], rgl_root=Path(self.rgl_root.get()),
                      wordbench_root=found_wb, output_dir=Path(self.output_dir.get()),
                      codes=selected, mode=mode, timeout=90,
                      practical_profile=Path(self.profile_path.get()) if self.profile_path.get().strip() else Path(self._result['output_dir']) / 'practical_generation_profile.json',
                      validation_profiles_root=Path(self.validation_profiles_root.get()) if self.validation_profiles_root.get().strip() else None,
                      stop=self._cancel_wordbench)
        # Tkinter variable access must stay on the GUI thread. The worker receives
        # an immutable snapshot of all paths to avoid Tcl cross-thread failures.
        scan_values = dict(workspace=Path(self.workspace.get()), rgl_root=Path(self.rgl_root.get()),
                           reports_root=Path(self.reports_root.get()) if self.reports_root.get().strip() else None,
                           profile_path=values['practical_profile'],
                           identity_map_path=Path(self.identity_path.get()) if self.identity_path.get().strip() else None,
                           output_dir=Path(self.output_dir.get()))
        def worker() -> None:
            try:
                batch = run_batch(**values, on_progress=lambda i,n,code,status: self._events.put(('progress', f"WB {mode}: {i}/{n} {code}: {status}")))
                scan = run_diagnostic(**scan_values)
                self._events.put(('wordbench_success', (batch, scan)))
            except Exception as exc:
                self._events.put(('error', self._save_error(f"WordBench {mode}", exc,
                    output_dir=values['output_dir'], protected_paths=[values['rgl_root'], found_wb])))
        threading.Thread(target=worker, name="observatory-wordbench", daemon=True).start()

    def _poll(self) -> None:
        try:
            while True:
                kind, value = self._events.get_nowait()
                if kind == 'progress':
                    self.state_text.set(value)
                    continue
                self.progress.stop()
                self._running = False
                self._set_busy(False)
                if kind == 'error':
                    details = value if isinstance(value, dict) else {"phase": "diagnostic", "message": str(value), "traceback": str(value), "log_path": ""}
                    self._last_error = details['traceback']
                    error_text = (f"Échec pendant {details['phase']} : {details['message']}")
                    self.state_text.set(error_text[:250])
                    self._set_text(self.explain, details['traceback'] + "\n\nJournal : " + (details['log_path'] or 'non disponible'))
                    self.tabs.select(self.diagnostic_tab)
                    messagebox.showerror("Erreur GF Observatory", error_text + "\n\nDétails dans l'onglet Diagnostic.\n" +
                                         ("Journal : " + details['log_path'] if details['log_path'] else ""))
                elif kind == 'wordbench_success':
                    batch, scanned = value
                    self._show_result(scanned)
                    done = sum(r['status'] == 'ok' for r in batch['results'])
                    failed = [r for r in batch['results'] if r['status'] not in ('ok', 'cancelled')]
                    message = f"WordBench {batch['mode']} : {batch['completed']} traitées, {done} réussies, {len(failed)} non réussies."
                    if failed:
                        first = failed[0]
                        message += f" {first['code']} : {first.get('reason') or first['status']}. Voir journal WB."
                    self.state_text.set(message)
                else:
                    self._show_result(value)
        except queue.Empty:
            pass
        self.after(120, self._poll)

    def _show_result(self, result: dict) -> None:
        self._result = result
        cat = result['catalog']
        self._rows = {entry['code']: entry for entry in cat['languages']}
        counts = cat['counts']
        self.count_text.set(f"{len(self._rows)} langues | {counts['ready']} prêtes | "
                            f"{counts['needs_work']} à compléter | {counts['unverified']} non vérifiées")
        self.state_text.set("Diagnostic terminé — fichiers dans " + result['output_dir'])
        self._render_rows()
        env = result['diagnostic']
        lines = ["GF Observatory — Rapport local", "", self.count_text.get(),
                 "", "RGL : " + str(env['rgl_root']),
                 "Rapports WordBench : " + str(env['reports_root']), "",
                 "Commandes repérées (aucune exécution) :"]
        lines += [f"  {name}: {x.get('path') or 'absente'}" for name, x in env['tools'].items()]
        lines += ["", "Dépôts repérés :"]
        lines += [f"  {name}: {'présent' if x['exists'] else 'absent'} ({x['path']})" for name, x in env['repositories'].items()]
        lines += ["", "'ready' exige une couverture des fonctions essentielles appuyée par",
                  "des résultats WordBench vérifiés. 'needs_work' exige des tests échoués.",
                  "'unverified' ne signifie PAS que la grammaire ne fonctionne pas.",
                  "'structural_gaps' ne sont PAS des fonctions linguistiques manquantes."]
        self._set_text(self.explain, '\n'.join(lines))
        if self._rows:
            code = next(iter(self._rows))
            self.tree.selection_set(code)
            self._show_selection()

    def _render_rows(self) -> None:
        if not hasattr(self, 'tree'):
            return
        term = self.filter_text.get().casefold().strip()
        selected = self.tree.selection()
        chosen = selected[0] if selected else None
        self.tree.delete(*self.tree.get_children())
        for code, item in sorted(self._rows.items()):
            if term and term not in code.casefold() and term not in item.get('status', '').casefold() and term not in item.get('project_id', '').casefold():
                continue
            dom = {d.get('domain'): d.get('status') for d in item.get('domains', [])}
            self.tree.insert('', 'end', iid=code,
                             values=(code, item.get('structural_status', '?'), item.get('wordbench_quick', 'non testé'), item['status'],
                                     dom.get('encyclopedic', 'non vérifié'), dom.get('procedural', 'non vérifié'),
                                     len(item.get('missing', [])), len(item.get('unverified', []))))
        if chosen and self.tree.exists(chosen):
            self.tree.selection_set(chosen)
            self._show_selection()

    def _show_selection(self, _event=None) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        item = self._rows.get(selected[0])
        if not item:
            return
        detail = [f"Langue : {item['code']}  / Projet WordBench : {item.get('project_id', '?')}",
                  f"Statut pratique : {item.get('status')}",
                  f"Source des preuves : {item.get('evidence_status')}",
                  f"WordBench quick (un module) : {item.get('wordbench_quick', 'non testé')}",
                  f"Journal WordBench : {item.get('wordbench_quick_log') or 'aucun'}",
                  f"Motif WordBench : {item.get('wordbench_quick_reason') or 'aucun'}",
                  f"Code de retour WordBench : {item.get('wordbench_quick_exit_code')}",
                  f"Structure : {item.get('structural_status')}",
                  "Modules conventionnels absents (indicatif) : " + (', '.join(item.get('structural_gaps', [])) or 'aucun'),
                  "Échecs fonctionnels prouvés : " + (', '.join(item.get('missing', [])) or 'aucun'),
                  "Fonctions non vérifiées : " + (', '.join(item.get('unverified', [])) or 'aucune'),
                  "", "Répertoires source :"]
        detail += [f"  {p}" for p in item.get('source_dirs', [])]
        for domain in item.get('domains', []):
            detail += [f"{domain.get('domain')}: {domain.get('status')} — {domain.get('required_passed')}/{domain.get('required_total')} obligatoires vérifiées"]
        self._set_text(self.detail, '\n'.join(detail))


def main() -> int:
    try:
        window = DiagnosticWindow()
        window.mainloop()
        return 0
    except Exception as exc:
        try:
            messagebox.showerror("GF Observatory", str(exc))
        except Exception:
            pass
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
