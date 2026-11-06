# GF Observatory — implementation status (2026-11-05)

**Release:** `1.0.0rc1` — executable full repository, **not a linguistically certified or Windows-qualified release**.

## Implemented and tested

- Strict version-1 `defluens.pilot-batch` real ZIP reader, all-member rehash, archive identity, status count reconciliation and explicit 14×15 scope.
- SQLite WAL derived read model: batch/scenario persistence, unique content fingerprints, import attempts, backups.
- Four-zone / fourteen-signal evidence matrix: unqualified canonical signals remain `MISSING` or `INCOMPATIBLE`, not a fabricated zero score.
- Technical candidate coverage, fail/timeout status, heuristic markers, separate human review status, stable source SHA-256.
- Basic trend comparisons between distinct source ZIP hashes. Reimport is not a new data point.
- Read-only local HTTP API and accessible lightweight dashboard, CLI, `.pyw` desktop, redacted manual static export.
- Unit, HTTP, negative security and real source-archive acceptance tests.

## Deliberately blocked or not demonstrated

- **Canonical WordBench release reader:** real `gf-wordbench.artifact-manifest/1.0` and corresponding summary pair not provided; their code-level schemas alone do not certify an adapter.
- **Linguistic review:** no owner-issued decision set or native speaker approved golds provided. Technical candidates remain `candidate_for_review`.
- **R5-R7 and formal maturity:** no qualifying canonical gates; pilot readiness remains `R0` and maturity `null`.
- **Windows native acceptance:** `.pyw`, PowerShell launch, junction handling and GF 3.12 coexistence must be exercised on the user's Windows machine. No Windows success is fabricated.
- **External publishing:** static output is local; no GitHub push, no RuntimeSet creation, release or activation.
- **Real-time polling:** no background tasks; all imports and analysis are operator-initiated.

Current implementation is deliberately *bounded*. Expanding to canonical WordBench validation, signing, advanced release states or extra languages requires source evidence and explicit approval of the applicable ADRs. The original `/docs` acceptance rules remain the governing reference.
