# GF Observatory — ADR-0001 — Read-Only Consumer

| Champ | Valeur |
|---|---|
| Document role | Workspace mutability decision |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Décision

Observatory ne modifie jamais un workspace observé. Toutes les écritures sont confinées à son état local.

## Conséquences

- le contrat est testable ;
- l’état d’implémentation reste séparé de la décision ;
- toute exception exige une nouvelle ADR.
