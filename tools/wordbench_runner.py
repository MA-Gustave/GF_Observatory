"""Bounded, explicit WordBench subprocess runner for Observatory.

Quick: a single public RGL module is compiled through canonical WordBench.
Practical: selected .gfs scenarios through optional WordBench practical extension,
           requiring a reviewed language-specific validation profile and golds.
Neither quick success nor module discovery proves practical semantic readiness.
"""
from __future__ import annotations

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
                    record["reason"] = ("wordbench_runconfig_unresolved" if
                        "The validation application requires a resolved RunConfig" in captured else "wordbench_exit_nonzero")
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


if __name__ == "__main__":
    raise SystemExit(main())
