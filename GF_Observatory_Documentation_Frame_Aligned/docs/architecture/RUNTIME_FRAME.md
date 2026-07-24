# GF Observatory — Canonical Runtime Frame

| Champ | Valeur |
|---|---|
| Document role | Runtime-frame authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Pipeline canonique

```text
CLI / API / UI request
→ request normalization
→ ObservationPlanner
→ ObservationPlan
→ evidence resolution
→ ObservationSnapshot
→ AnalysisPlanner
→ AnalysisPlan
→ AnalyzerBackend
→ AnalysisResult
→ public response mapping
```

## Couche A — Entrées et normalisation

Accepte les intentions externes et les transforme en `NormalizedObservationRequest`.

Responsabilités :

- résoudre `workspace_id`, `project_id`, `run_id` et filtres ;
- appliquer les valeurs par défaut ;
- rejeter les paramètres contradictoires ;
- retirer les détails de transport ;
- produire une commande interne stable.

## Couche B — Planification et runtime d’observation

`ObservationPlanner` est le centre décisionnel. Il produit un `ObservationPlan` qui définit :

```text
plan_id
plan_version
subject_refs
reader_bindings
required_artifacts
optional_artifacts
verification_policy
freshness_policy
continuation_policy
output_contract
```

Le plan, et non l’interface ou le lecteur, décide ce qui doit être observé.

## Couche C — Résolution des preuves

Les résolveurs lient le plan aux artefacts réels :

- identité du workspace et du projet ;
- versions de schémas ;
- manifeste et hachages ;
- résumés, preuves brutes et statuts ;
- provenance et timestamps.

Ils produisent des `EvidenceBinding` communs, indépendants du format source.

## Couche D — Analyseurs et projections

Les analyseurs opèrent sur les mêmes observations et profils :

- matrice de preuves ;
- maturité ;
- readiness ;
- santé ;
- diagnostics ;
- tendances.

Chaque backend produit un `AnalysisResult`. Le mapping public crée ensuite les réponses CLI, API, UI ou fichiers sans recalculer l’analyse.

## Préoccupation transversale — Contexte d’observation

`ObservationContext` porte :

- corrélation du cycle ;
- horloge ;
- versions actives ;
- cache et fingerprints ;
- budgets de lecture ;
- politiques de continuation ;
- diagnostics accumulés.

Le contexte influence le runtime via les plans et politiques, jamais par mutations globales cachées.

## Compatibilité immédiate future

Le cadre réserve des identités stables pour les plans, profils, signaux, outils, statuts et schémas. Un autre produit conforme au même cadre peut s’aligner par échange de contrats publics et tables de correspondance, sans restructuration du cœur Observatory.
