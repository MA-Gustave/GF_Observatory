# Security and authority

- **Read-only sources.** Archive bytes are read without extracting them or executing anything. All official GF compilation/qualification remains in WordBench.
- **ZIP handling.** Reject absolute paths, `../` traversal, symlinks, duplicate/case-colliding paths, excessive depth/size/compression ratios. Read every file through the `zipfile` API to verify CRC and SHA-256, then reconcile source run/scenario status counts and candidate sidecars. No archive member is used directly as a filesystem path.
- **Evidence limits.** Independently computed hashes prove only the bytes available locally, not their original author, release status or linguistic correctness. There is no producer-signed canonical manifest in the pilot ZIP.
- **Immutable derived state.** SQLite stores normalized candidate texts and local evidence hashes; source archive bytes are not modified. Database files are excluded from Git.
- **No credential handling.** The GUI has no remote login, cloud sync or arbitrary shell functionality. The HTTP interface binds only to loopback and exposes `GET` routes.
- **Public projection.** Requires an explicit CLI acknowledgment, allows only code/name/count/alert statistics, excludes raw candidate texts, local paths and producer logs. The four files remain local until separately published by the operator.
- **Confidentiality.** Local API scenario views can contain texts from your evidence. Do not expose the loopback port through a reverse proxy, port forward or untrusted browser extension.
- **Trust boundary.** `candidate_for_review` means GF produced candidate text. It is not human gold approval, linguistic certification, a release gate, or a RuntimeSet activation. Neither UI color nor a successful HTTP request upgrades those claims.
