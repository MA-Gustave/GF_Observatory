# Engineering invariants

1. The original accepted `/docs` is the authority for product boundaries.
2. Observatory is read-only relative to producers; no compiler subprocesses.
3. All importers are versioned, bounded, fail-closed and independently tested.
4. Do not confuse SHA-256 byte integrity with linguistic verification.
5. No automatic promotion to `ready`, R5–R7, gold approval, published RuntimeSet or activation.
6. CLI/Tk/API use the same application service and SQLite-derived read model.
7. API stays loopback-only and read-only; no arbitrary process or HTTP writes.
8. The fixed release-candidate scope is 14 documented languages × 15 required intents.
9. No private source ZIP or database should be checked into version control.
10. Record each implementation gap in `docs/IMPLEMENTATION_STATUS_CURRENT.md`.
