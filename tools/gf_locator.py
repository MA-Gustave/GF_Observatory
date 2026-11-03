"""Bounded GF compiler discovery for Observatory / WordBench.

Only locates *actual local executables* named gf or gf.exe. It neither
installs GF nor trusts a repository containing source code as a compiler.
"""
from __future__ import annotations

import os
from pathlib import Path
import shutil


def _valid(candidate: Path | str | None) -> Path | None:
    if not candidate:
        return None
    try:
        path = Path(candidate).expanduser().resolve()
        if path.name.casefold() not in {"gf.exe", "gf"} or not path.is_file():
            return None
        if os.name != 'nt' and not os.access(path, os.X_OK):
            return None
        return path
    except (OSError, ValueError):
        return None


def resolve_gf_executable(preferred: Path | None = None, workspace: Path | None = None) -> Path | None:
    """Find gf.exe on PATH, common Windows installer paths or within the GF source workspace.

    An explicitly selected invalid file is *not* silently replaced by another
    binary: the user must fix the selection. Workspace search is bounded and
    skips the large RGL and unrelated project sources to avoid a slow startup.
    """
    if preferred is not None:
        return _valid(preferred)

    for command in ('gf', 'gf.exe'):
        found = _valid(shutil.which(command))
        if found:
            return found

    home = Path.home()
    appdata = os.environ.get('APPDATA')
    localappdata = os.environ.get('LOCALAPPDATA')
    fixed = [home / '.cabal' / 'bin' / 'gf.exe',
             home / 'scoop' / 'shims' / 'gf.exe']
    if appdata:
        fixed.append(Path(appdata) / 'cabal' / 'bin' / 'gf.exe')
    if localappdata:
        fixed += [Path(localappdata) / 'Programs' / 'GF' / 'bin' / 'gf.exe',
                  Path(localappdata) / 'Microsoft' / 'WinGet' / 'Links' / 'gf.exe']
    for folder in (os.environ.get('ProgramFiles'), os.environ.get('ProgramFiles(x86)')):
        if folder:
            fixed += [Path(folder) / 'GF' / 'bin' / 'gf.exe',
                      Path(folder) / 'Grammatical Framework' / 'bin' / 'gf.exe']
    for path in fixed:
        found = _valid(path)
        if found:
            return found

    if workspace is None:
        return None
    root = Path(workspace).expanduser().resolve()
    if not root.is_dir():
        return None
    for relative in ('gf-3.12-windows/gf.exe', 'gf.exe', 'bin/gf.exe', 'gf-core/gf.exe',
                     'gf-core/bin/gf.exe', 'GF/bin/gf.exe', 'gf/bin/gf.exe',
                     'gf-core/dist/build/gf/gf.exe'):
        found = _valid(root / relative)
        if found:
            return found

    # Compiler build trees can be deeply nested in dist-newstyle/.stack-work.
    # Restrict traversal to likely compiler project directories, never gf-rgl.
    starts = [root / item for item in ('gf-core', 'GF', 'gf', 'compiler', 'GF-core', 'gf-binary')]
    try:
        starts.extend([child for child in root.iterdir() if child.is_dir() and
                       not child.is_symlink() and child.name.casefold() in {'grammatical-framework-core', 'grammaticalframework'}])
    except OSError:
        return None
    checked = 0
    skip = {'.git', '.venv', 'venv', 'node_modules', 'tests',
            'docs', 'documentation', 'examples', 'lib', 'library', 'gf-rgl',
            'gf_wordbench', 'gf_observatory'}
    for start in starts:
        if not start.is_dir() or start.is_symlink():
            continue
        start = start.resolve()
        if not start.is_relative_to(root):
            continue
        for directory, subdirs, files in os.walk(start, followlinks=False):
            checked += 1
            if checked > 4000:
                return None
            depth = len(Path(directory).relative_to(start).parts)
            subdirs[:] = sorted(d for d in subdirs if d.casefold() not in skip and
                                not (Path(directory) / d).is_symlink()) if depth < 13 else []
            for filename in files:
                if filename.casefold() in {'gf.exe', 'gf'}:
                    found = _valid(Path(directory) / filename)
                    if found:
                        return found
    return None


def missing_gf_message(workspace: Path) -> str:
    return ("Compilateur Grammatical Framework introuvable.\n\n"
            "WordBench est présent, mais gf.exe n'est pas accessible.\n"
            "Un dépôt gf-core ou gf-rgl ne suffit pas : il faut un exécutable GF compilé.\n\n"
            "Clique sur « Détecter GF » ou choisis gf.exe avec « Parcourir… ».\n"
            "Le compilateur peut aussi être installé dans le PATH de Windows.\n\n"
            f"Workspace inspecté : {workspace}\n\n"
            "Dans PowerShell 7 : Get-Command gf -ErrorAction SilentlyContinue")


def default_gf_executable(workspace: Path) -> Path | None:
    """Prefer the verified local GF 3.12 binary; fall back to normal discovery.

    Other installations are not forced to use the user's Windows path. The
    UI can always override the selection with the file picker.
    """
    root = Path(workspace).expanduser()
    verified_local = _valid(root / 'gf-3.12-windows' / 'gf.exe')
    return verified_local or resolve_gf_executable(workspace=root)
