# Real WordBench practical pilot archive — acceptance evidence

**Source:** user-supplied `defluens-batch-full-20261105T233034Z-3874400.zip`.

- SHA-256 of original ZIP: `d6b10174d490a4f7a1f5f9b61fcf70de3140a3d6e50e3c3c52c913cfd56bdcfd`
- Bytes: **413,660**; recalculated file members: **866**
- Recalculated member tree fingerprint: `0141899e0cb0f617eefd602a6ecb415c7f28d5191b1148730c0e7de50d888413`
- Source schema: `defluens.pilot-batch/1.0`, status: `completed_unverified`.
- Full producer campaign: **20 languages, 300 probes, 223 `candidate_for_review`, 77 `probe_failed`, 0 timeouts**.
- Approved *observation scope*: `Eng Fre Spa Ger Dut Swe Dan Nor Nno Fin Est Afr Ita Por`.
- Scope: **14 languages × 15 required practical intents = 210 candidates and 0 failed probes**.
- Human approvals: **0 confirmed**; canonical WordBench manifest: **absent from this pilot ZIP**.
- Canonical readiness: **R0, not evaluated as a release**; practical generation: `unverified`.

## Heuristic surface alerts (non-exhaustive)

| Language | Scenario | Alert |
|---|---|---|
| `Fre` | `factual-negation` | `GF_UNRESOLVED_GLUE_MARKER` |
| `Fre` | `prohibition` | `GF_UNRESOLVED_GLUE_MARKER` |
| `Est` | `possibility` | `GF_UNRESOLVED_GLUE_MARKER` |
| `Est` | `obligation` | `GF_UNRESOLVED_GLUE_MARKER` |

These are suspicious `&+` markers in candidate text, **not** proof of a grammar error or an exhaustive correctness audit. The 206 candidates without a flagged marker remain equally unreviewed. The six other producer languages are preserved in source aggregate totals but not included in the core-14 language table.

The genuine pilot archive is **not shipped** in the public repository, to avoid carrying raw logs or local Windows paths. On an authorized local machine, verify and import the operator-owned ZIP with `gf-observatory verify-pilot` and `import-pilot`.
