# Windows operations — GF Observatory

## Prerequisites

Windows 10/11; CPython 3.11+ with Tkinter; PowerShell 7 is recommended. GF executable is **not needed** because Observatory observes evidence, not runs compilation.

1. Extract the complete ZIP to `C:\mycode\Grammatical-Framework`.
2. Verify that `GF_Observatory\GF_Observatory.pyw` and `GF_Observatory\src` exist.
3. Double-click `Lancer_GF_Observatory.bat` or launch `GF_Observatory.pyw` directly.
4. Select the most recent `defluens-batch-full-*.zip` from your WordBench output directory, e.g. `%USERPROFILE%\Downloads\Ars_Magna_Defluens\practical_pilot_runs`.
5. Import the archive. The application confirms the 14 languages, 210 probes and candidate-only state.
6. Click **Ouvrir le tableau de bord** to view at `http://127.0.0.1:8765/`. The dashboard has **no mutation endpoints**.

## PowerShell verification and audit

```powershell
Set-Location 'C:\mycode\Grammatical-Framework\GF_Observatory'
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
py -3 -m unittest discover -s tests -v
py -3 -m gf_observatory doctor
$zip = Join-Path $env:USERPROFILE 'Downloads\Ars_Magna_Defluens\practical_pilot_runs\defluens-batch-full-20261105T233034Z-3874400.zip'
py -3 -m gf_observatory verify-pilot $zip
py -3 -m gf_observatory import-pilot $zip
py -3 -m gf_observatory report --format markdown --output "$env:USERPROFILE\Downloads\GF_Observatory_Report.md"
```

If your ZIP filename differs, replace the example with the exact one. Never assume WordBench exported a canonical manifest from the pilot ZIP.

## Private database and backup

By default the database lives at `GF_Observatory\.gf-observatory\observatory.sqlite3`; it is git-ignored. To back it up while the app is running:

```powershell
py -3 -m gf_observatory backup "$env:USERPROFILE\Documents\GF_Observatory_backup_20261105.sqlite3"
```

Restore only after closing Observatory and after retaining the previous database file. Never delete producer run folders when cleaning Observatory.

## Manual static preview

```powershell
py -3 -m gf_observatory export-static "$env:USERPROFILE\Downloads\gf-observatory-status" --acknowledge-candidate-publication
```

The result is **four redacted local files**; it is not pushed to GitHub. Preview them with any trusted static HTTP server, read `status.json`, and independently decide whether to publish. No public path, raw candidate text, username, PGF or RuntimeSet is exported.

## Troubleshooting

- `OBS_ZIP_INTEGRITY`: unreadable/truncated ZIP. Re-export from WordBench.
- `OBS_ZIP_PATH`: archive contains traversal, ambiguous or unsafe member names. Do not bypass safeguards.
- `OBS_PILOT_INCONSISTENT`: source totals, scenario output or batch identity differ. Re-export and investigate.
- `OBS_PILOT_REVIEW_UNTRUSTED`: archive unexpectedly claims approved review without an approved review artifact contract.
- `OBS_BATCH_NOT_FOUND`: no matching evidence has been imported.
- `OBS_HOST_DENIED`: browser must use `http://127.0.0.1:8765`, not a remote/IP alias.
- `OBS_READ_ONLY_API`: import through the local `.pyw` or CLI, never over HTTP.
