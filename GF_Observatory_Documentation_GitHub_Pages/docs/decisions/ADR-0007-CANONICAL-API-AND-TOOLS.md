# GF Observatory — ADR-0007 — Canonical API and Tools

| Champ | Valeur |
|---|---|
| Document role | Interface decision |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Décision

Une seule API /api/v1 sert CLI, UI et automatisations. Les outils sont allowlistés et mappés vers des cas d’utilisation internes.

## Conséquences

- le contrat est testable ;
- l’état d’implémentation reste séparé de la décision ;
- toute exception exige une nouvelle ADR.
