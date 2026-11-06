# Read-only observation: Defluens → SemantiK development handoff

`tools.semantik_development.project_handoff(path)` converts the WordBench
experimental handoff JSON into a concise, read-only language/contract-gap
projection. It **never** changes `RELEASED` state, approves linguistic gold,
or interprets GF candidate generation as SemantiK conformance. Observatory
must not compile PGF or publish RuntimeSets.

Readiness and activation come from SA manifests and the public Runtime
Orchestrator; candidates remain candidate observations even at 210/210.
