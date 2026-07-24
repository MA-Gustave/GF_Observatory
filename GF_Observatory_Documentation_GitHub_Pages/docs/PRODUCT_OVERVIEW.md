# GF Observatory — Product Overview

| Champ | Valeur |
|---|---|
| Document role | Product authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Mission

GF Observatory transforme des artefacts Wordbench versionnés en un historique local de faits observables, puis en vues de santé, de maturité, de readiness et de tendance.

## Proposition de valeur

```text
artefacts publics
→ normalisation
→ plan d’observation
→ résolution des preuves
→ observation immuable
→ analyse profilée
→ rapports consolidés
```

## Source de vérité

Le plan d’observation et le profil d’analyse versionné définissent ce qui doit être lu, comment les preuves sont interprétées et quels résultats peuvent être calculés. Aucun renderer, rapporteur, endpoint ou écran ne peut redéfinir ces décisions.

## Capacités

- registre de workspaces ;
- ingestion compatible avec plusieurs versions de schémas ;
- vérification de manifestes et hachages ;
- snapshots immuables ;
- matrice à quatre zones et quatorze signaux ;
- maturité observée, readiness observé et santé synthétique ;
- diagnostics traçables ;
- tendances historiques ;
- CLI, API et UI locale au-dessus des mêmes cas d’utilisation ;
- registre d’outils internes allowlistés.
