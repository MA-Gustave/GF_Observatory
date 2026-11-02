"""Discover language candidates in an actual GF RGL checkout (read-only)."""
from __future__ import annotations

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
    # Ignore fabricated "languages" caused by module endings (e.g. AllEngAbs.gf),
    # the GF prelude, extension conventions, and the RGL's TEMPLATE folder.
    # A candidate must have a recognisable language-level module outside those
    # purely technical directories, including partial Cat/Res-only languages.
    core = {"Grammar", "Syntax", "Paradigms", "Lang", "All", "Cat", "Res",
            "Noun", "Verb", "Adjective", "Phrase", "Sentence", "Question"}
    filtered = {}
    for code, info in found.items():
        if code in {"Abs", "Cnc", "Ext", "TMP"}:
            continue
        real = any(
            role in core and any(
                not set(Path(path).parts).intersection({"TEMPLATE", "prelude", "abstract_ext", "abstract_to_api"})
                for path in paths
            ) for role, paths in info["modules"].items()
        )
        if real:
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


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--rgl-root", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    args = p.parse_args(argv)
    data = inventory(args.rgl_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Inventory: {len(data['languages'])} language candidates -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
