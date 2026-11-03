"""One-module GF compilation using WordBench's canonical command builder.

Observatory invokes this in a separate Python process with WordBench on
PYTHONPATH. This deliberately does *not* call the broken WordBench 2026-11-02
`validate --mode quick` CLI, whose provider requires RunConfig but receives
ValidateCommandRequest. No WordBench source is patched.

Quick checks syntactic compilation of one public module, never linguistic
accuracy or génération pratique semantic readiness.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from datetime import datetime, timezone

try:
    from tools.windows_process import background_process_options
except ModuleNotFoundError:
    from windows_process import background_process_options


def fail(reason: str, code: int) -> int:
    print(f"[Observatory/WordBench quick] {reason}", file=sys.stderr, flush=True)
    return code


def rgl_search_paths(source: Path, rgl_root: Path) -> list[Path]:
    """Existing RGL import directories needed to compile a concrete module.

    A concrete GrammarEng imports the abstract Grammar. Omitting src/abstract
    makes GF 3.12 report `File Grammar.gf does not exist` even if the concrete
    grammar and GF executable are both valid. Keep the language folder first,
    then the RGL abstract grammar and common shared resources.
    """
    src_root = rgl_root / 'src' if (rgl_root / 'src').is_dir() else rgl_root
    candidates = [source.parent]
    # Other RGL languages depend on shared family resources. The 2026-11-02
    # audit identified CatBantu, NounEng and CatExt as existing but not on GF's
    # import path. Only add known dependency directories; avoid scanning all
    # languages into the GF import namespace.
    shared = ['abstract', 'api', 'prelude', 'common', 'romance',
              'scandinavian', 'hindustani', 'bantu']
    if source.parent.name.casefold() == 'scots':
        shared.append('english')
    if source.parent.name.casefold() == 'zulu':
        shared.append('zulu/abstract_ext')
    for relative in shared:
        candidate = src_root / relative
        if candidate.is_dir():
            candidates.append(candidate)
    candidates.append(src_root)
    # No non-existent paths or repeated directories, with stable search order.
    return list(dict.fromkeys(p.resolve() for p in candidates if p.is_dir()))


def execute(source: Path, rgl_root: Path, output_root: Path, gf_exe: Path | None) -> int:
    source, rgl_root, output_root = (Path(x).resolve() for x in (source, rgl_root, output_root))
    if not source.is_file() or source.suffix != '.gf' or not source.is_relative_to(rgl_root):
        return fail(f"Le module GF n'est pas un fichier dans la RGL : {source}", 6)
    if output_root == rgl_root or output_root.is_relative_to(rgl_root):
        return fail("Le dossier de sortie est dans les sources GF", 6)
    if gf_exe is not None:
        gf_path = Path(gf_exe).expanduser().resolve()
    else:
        discovered = shutil.which('gf') or shutil.which('gf.exe')
        if discovered is None:
            return fail("Compilateur GF introuvable sur PATH. Installe GF ou fournis --gf-exe.", 4)
        gf_path = Path(discovered).resolve()
    if not gf_path.is_file():
        return fail(f"Compilateur GF introuvable : {gf_path}", 4)

    try:
        from gf_wordbench.validation.compilation.commands import (
            GfCommandProfile, ValueOptionStyle, build_module_compile_command
        )
    except (ImportError, ModuleNotFoundError) as exc:
        return fail(f"Composant WordBench de compilation indisponible : {exc}", 5)

    gfo_dir, out_dir = output_root / 'gfo', output_root / 'out'
    gfo_dir.mkdir(parents=True, exist_ok=True)
    out_dir.mkdir(parents=True, exist_ok=True)
    paths = rgl_search_paths(source, rgl_root)
    expected = gfo_dir / (source.stem + '.gfo')
    # Avoid a false positive from a prior successful attempt.
    if expected.exists():
        if not expected.is_file() or expected.is_symlink():
            return fail(f"Artefact non régulier ou lien symbolique : {expected}", 6)
        expected.unlink()
    profile = GfCommandProfile(
        profile_id='observatory-single-module', path_separator=os.pathsep,
        value_option_style=ValueOptionStyle.EQUALS,
        gfo_dir_option='--gfo-dir', output_dir_option='--output-dir'
    )
    try:
        cmd = build_module_compile_command(
            executable=gf_path, working_directory=source.parent,
            source_file=source, gf_search_paths=paths, profile=profile,
            gfo_dir=gfo_dir, output_dir=out_dir, quiet=True, emit_cpu_stats=False
        )
    except (OSError, ValueError, TypeError) as exc:
        return fail(f"Échec de préparation par WordBench : {type(exc).__name__}: {exc}", 6)

    print(f"[Observatory/WordBench quick] Module : {source.name}", flush=True)
    print(f"[Observatory/WordBench quick] Compilateur : {gf_path}", flush=True)
    print("[Observatory/WordBench quick] Construction de la commande par gf_wordbench.validation.compilation.commands", flush=True)
    print("[Observatory/WordBench quick] Chemins RGL : " + os.pathsep.join(map(str, paths)), flush=True)
    try:
        result = subprocess.run(
            [str(cmd.executable), *cmd.arguments], cwd=str(cmd.working_directory),
            stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
            encoding='utf-8', errors='replace', check=False,
            **background_process_options()
        )
    except OSError as exc:
        return fail(f"Le compilateur GF ne démarre pas : {exc}", 4)
    print((result.stdout or '')[-500000:], flush=True)
    if result.returncode != 0:
        if (result.returncode & 0xFFFFFFFF) == 0xC000013A:
            return fail("Processus GF interrompu sous Windows (0xC000013A / STATUS_CONTROL_C_EXIT). "
                        "Ce résultat ne démontre pas une erreur de grammaire. Relance le test isolément.", 23)
        return fail(f"Compilation GF en échec (code {result.returncode}). Voir ci-dessus.", 2)
    # GF's standard output convention is .gfo. A successful exit without any
    # such artifact is not proof of successful compilation.
    produced = expected.is_file() and expected.stat().st_size > 0
    if not produced:
        return fail(f"GF a retourné 0, mais l'artefact attendu est absent ou vide : {expected}", 3)
    report = {"schema_id": "gf-observatory.wordbench-quick-probe", "schema_version": "1.0",
              "timestamp": datetime.now(timezone.utc).isoformat(),
              "source": str(source), "wordbench_component": "validation.compilation.commands",
              "gf_executable": str(gf_path), "artifact": str(expected), "status": "ok",
              "note": "Un seul module compilé; aucune validation sémantique génération pratique."}
    (output_root / 'quick_probe_result.json').write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"[Observatory/WordBench quick] OK : {expected}", flush=True)
    return 0


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source', type=Path, required=True)
    p.add_argument('--rgl-root', type=Path, required=True)
    p.add_argument('--out-root', type=Path, required=True)
    p.add_argument('--gf-exe', type=Path)
    args = p.parse_args(argv)
    return execute(args.source, args.rgl_root, args.out_root, args.gf_exe)


if __name__ == '__main__':
    raise SystemExit(main())
