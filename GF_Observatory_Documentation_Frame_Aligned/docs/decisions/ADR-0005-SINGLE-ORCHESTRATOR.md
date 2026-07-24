# GF Observatory — ADR-0005 — Single Orchestrator

| Champ | Valeur |
|---|---|
| Document role | Orchestration decision |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Décision

ObservatoryOrchestrator est l’entrée normale unique. Chaque scanner est appelé une fois par zone et cycle ; les outils isolés sont sans effet de bord par défaut.

## Conséquences

- le contrat est testable ;
- l’état d’implémentation reste séparé de la décision ;
- toute exception exige une nouvelle ADR.
