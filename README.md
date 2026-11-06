# GF Observatory 1.0.0rc1

**Independent, local-first read model for versioned GF WordBench evidence.**

GF Observatory **reads and analyzes** evidence. It does not compile GF, modify the RGL, orchestrate WordBench, approve golds or linguistic reviews, publish a SemantiK RuntimeSet, activate a runtime, or create a language release.

The current installed reader supports **real WordBench/Defluens practical `full` pilot ZIP files** in `defluens.pilot-batch/1.0` format. A practical pilot is *not* the canonical `gf-wordbench.artifact-manifest/1.0` + `gf-wordbench.run-summary/1.0` evidence bundle. These producer formats remain separate. Successful pilot probes are **candidates awaiting linguistic review**, not `ready`/`R7`.

The application is a complete, runnable **release candidate** for this bounded use case: import genuine pilot archives, verify their content and consistency, persist immutable observations, analyze 14 languages × 15 useful semantic intents, browse their evidence, compare runs and generate a redacted local static status. Full product certification against real canonical WordBench releases and Windows integration remains a separate acceptance gate.

## Download and installation (Windows)

Extract the complete archive to `C:\mycode\Grammatical-Framework` so the directory becomes:

```text
C:\mycode\Grammatical-Framework\GF_Observatory\
    GF_Observatory.pyw                 desktop interface
    Lancer_GF_Observatory.bat         desktop launcher
    Tester_GF_Observatory.bat         tests
    Installer_GF_Observatory.ps1      local diagnostic
    observatory.example.toml          optional configuration
    src\gf_observatory\              real application code
    tests\                            Python test suite
    docs\                             canonical documents and implementation detail
```

Double-click **`Lancer_GF_Observatory.bat`** and choose **Importer un ZIP pilote WordBench…**. Select the `defluens-batch-full-*.zip` file produced by the WordBench practical qualification tool. The application imports only the 14 documented languages and 15 required capacities; it does not rerun GF. Press **Ouvrir le tableau de bord** to inspect the results.

The desktop UI is optional. Use PowerShell 7 for an audit-friendly workflow:

```powershell
Set-Location 'C:\mycode\Grammatical-Framework\GF_Observatory'
$env:PYTHONPATH = (Join-Path (Get-Location) 'src')
py -3 -m gf_observatory doctor
py -3 -m gf_observatory verify-pilot "$env:USERPROFILE\Downloads\defluens-batch-full-<ID>.zip"
py -3 -m gf_observatory import-pilot "$env:USERPROFILE\Downloads\defluens-batch-full-<ID>.zip"
py -3 -m gf_observatory status
py -3 -m gf_observatory report --format markdown --output .\rapport_observatory.md
py -3 -m gf_observatory serve
```

Replace `<ID>` with the actual filename (or drag the ZIP onto a PowerShell prompt). Once `serve` runs, open **http://127.0.0.1:8765/** on the same PC. For an import-free test run, `Tester_GF_Observatory.bat` executes the synthetic automated suite without GF.

## Périmètre validé utile (WordBench 0.1.4)

The accepted fixed selection is:

`Eng Fre Spa Ger Dut Swe Dan Nor Nno Fin Est Afr Ita Por`

Each language is assessed for exactly 15 intents:

`factual-present`, `past-event`, `past-state`, `future-reference`, `factual-negation`, `temporal-order`, `condition-real`, `possibility`, `source-attribution`, `quantity`, `location`, `instruction`, `prohibition`, `obligation`, `conditional-instruction`.

The optional capabilities (`anteriority`, `process-ongoing`, `passive-or-rephrase`, `counterfactual`, `habitual`) are **excluded**. No requirement to implement every verb tense or literary construction is introduced.

## Functionality

| Subsystem | Implemented behavior |
|---|---|
| ZIP importer | Read-only. Version-gated. Path traversal, duplicate members and ZIP bombs rejected; all member contents independently hashed; declared pilot counts independently reconciled. |
| Local storage | SQLite WAL, immutable batch/scenario snapshots, SHA-256 replay deduplication, import attempt ledger and safe backup. |
| Analysis | 4-zone / 14-signal conservative matrix, pilot technical outcomes, provenance, 15-intent coverage, surface marker alerts, trends between distinct source batches. |
| Interfaces | Desktop `.pyw`, CLI, local web dashboard and read-only `/api/v1` HTTP endpoints. |
| Reports | JSON, Markdown and redacted four-file static status (`index.html`, `app.js`, `style.css`, `status.json`). |
| Security | 127.0.0.1-only API; no web mutation endpoints, no imported script execution, no shell calls, no source changes, bounded inputs. |
| Release authority | `human_review_completed=0`; `linguistically_certified=false`; `canonical_readiness=R0` and `canonical_maturity=null` for a practical pilot. |

The pilot batch ZIP is a **technical** result, not a canonical manifest. Local checksums assert that the ZIP bytes were read consistently; they are *not* owner-certified signatures. The 14-signal matrix is **not scored** until canonical source evidence and accepted analysis profiles are present.

## CLI reference

```text
python -m gf_observatory [--config observatory.toml] COMMAND
  doctor
  verify-pilot ZIP [--languages Eng Fre ...]
  import-pilot ZIP [--languages Eng Fre ...]
  batches
  status [--batch-id ID]
  languages [--batch-id ID]
  scenarios [--batch-id ID] [--language Fre]
  matrix Fre [--batch-id ID]
  trends Fre
  report [--batch-id ID] [--format json|markdown] [--output FILE]
  backup FILE
  export-static DIRECTORY [--batch-id ID] --acknowledge-candidate-publication
  serve
  gui
```

The static export is not uploaded to GitHub. It uses operator confirmation, excludes local paths/raw candidates and intentionally labels all data as unreviewed. An operator must inspect and independently publish it, if appropriate.

## Source state and quality evidence

The code has been exercised against the genuine provided WordBench full-pilot archive `defluens-batch-full-20261105T233034Z-3874400.zip` (not shipped in the repository). It contains 20 producer languages, of which 14 fall within the fixed review scope. In that scope the reader found 210 technical candidates and 4 possible GF surface markers; this does **not** prove linguistic correctness. Full batch totals are 223 candidates and 77 failed probes across all 20 languages.

See [real-archive acceptance](docs/practical/REAL_BATCH_ACCEPTANCE_2026_11_05.md), [current implementation](docs/IMPLEMENTATION_STATUS_CURRENT.md), [Windows operations](docs/OPERATIONS_WINDOWS.md), [security](docs/SECURITY.md) and [API reference](docs/API_REFERENCE.md).

## Product boundaries

- GF / RGL owns GF compilation and realization.
- GF WordBench owns tests, practical qualification and source evidence.
- Ars Magna Defluens coordinates approved language development.
- GF Observatory explains, stores and displays immutable **observations**; no authority is transferred by import.

Original canonical architecture and contract documents from the provided `/docs` are preserved within `docs/`. Their dated implementation-status statements describe the original documentation baseline; `docs/IMPLEMENTATION_STATUS_CURRENT.md` reports this codebase's actual status.
