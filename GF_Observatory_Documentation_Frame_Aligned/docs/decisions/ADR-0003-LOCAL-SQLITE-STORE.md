# GF Observatory — ADR-0003 — Local SQLite Store

| Champ | Valeur |
|---|---|
| Document role | Persistence decision |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Décision

Le stockage cœur est SQLite local, derrière un port. Aucun serveur de base de données n’est requis.

## Conséquences

- le contrat est testable ;
- l’état d’implémentation reste séparé de la décision ;
- toute exception exige une nouvelle ADR.
