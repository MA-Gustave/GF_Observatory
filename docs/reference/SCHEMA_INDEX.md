# GF Observatory — Schema Index

| Champ | Valeur |
|---|---|
| Document role | Persisted schema authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

| Schema ID | Rôle |
|---|---|
| `gf-observatory.config/1.0` | Configuration. |
| `gf-observatory.workspace-registry/1.0` | Registre de workspaces. |
| `gf-observatory.observation-request/1.0` | Requête normalisée. |
| `gf-observatory.observation-plan/1.0` | Plan runtime canonique. |
| `gf-observatory.evidence-binding/1.0` | Preuve normalisée. |
| `gf-observatory.observation/1.0` | Observation immuable. |
| `gf-observatory.analysis-profile/1.0` | Profil de zones et règles. |
| `gf-observatory.analysis-plan/1.0` | Plan d’analyse. |
| `gf-observatory.evidence-matrix/1.0` | Matrice à quatre zones. |
| `gf-observatory.diagnostic/1.0` | Finding canonique. |
| `gf-observatory.project-health/1.0` | Santé synthétique. |
| `gf-observatory.analysis-result/1.0` | Résultat interne. |
| `gf-observatory.report/1.0` | Rapport public. |
| `gf-observatory.public-status/1.0` | Snapshot statique publiable de l’état des langues. |
| `gf-observatory.tool-registry/1.0` | Registre d’outils. |
| `gf-observatory.api-envelope/1.0` | Enveloppes API. |

## Règles

- toutes les données persistées portent `schema_id` et `schema_version` ;
- les contrats source gardent leur propre namespace ;
- une modification sémantique incompatible incrémente la version majeure ;
- les migrations et lecteurs externes sont des responsabilités distinctes ;
- le manifeste documentaire et les tests de contrat suivent chaque changement.
