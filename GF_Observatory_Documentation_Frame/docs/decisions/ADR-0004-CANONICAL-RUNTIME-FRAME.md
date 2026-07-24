# GF Observatory — ADR-0004 — Canonical Runtime Frame

| Champ | Valeur |
|---|---|
| Document role | Runtime-architecture decision |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Décision

Le comportement est centré sur la normalisation, ObservationPlan, EvidenceBinding, AnalysisPlan et AnalysisResult. Les interfaces et backends ne redéfinissent pas ces décisions.

## Conséquences

- le contrat est testable ;
- l’état d’implémentation reste séparé de la décision ;
- toute exception exige une nouvelle ADR.
