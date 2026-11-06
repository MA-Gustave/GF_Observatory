# GF Observatory — ADR-0002 — Independent Product

| Champ | Valeur |
|---|---|
| Document role | Product-independence decision |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Décision

Observatory utilise uniquement des contrats publics. Aucun package, stockage ou service privé d’un producteur n’est requis.

## Conséquences

- le contrat est testable ;
- l’état d’implémentation reste séparé de la décision ;
- toute exception exige une nouvelle ADR.
