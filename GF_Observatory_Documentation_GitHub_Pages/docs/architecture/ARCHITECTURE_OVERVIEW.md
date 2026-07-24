# GF Observatory — Architecture Overview

| Champ | Valeur |
|---|---|
| Document role | Canonical architecture |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Style architectural

GF Observatory est un monolithe modulaire local-first structuré selon une architecture hexagonale et un cadre runtime canonique.

### Modules fonctionnels

```text
registry       identités, workspaces et accès autorisés
ingestion      localisation, lecture, compatibilité et intégrité
runtime        normalisation, planification et orchestration
observations   faits immuables, snapshots, fraîcheur et historique
analysis       profils, matrice, santé, readiness, diagnostics et tendances
reporting      réponses API, vues UI, JSON, Markdown et terminal
tools          registre allowlisté de cas d’utilisation opérationnels
```

### Anneaux de dépendance

```text
domain → application → ports → adapters → entrypoints → bootstrap
```

- `domain` possède les identités, plans, observations, statuts et invariants ;
- `application` possède les cas d’utilisation et l’orchestrateur ;
- `ports` décrivent les sources d’artefacts, le stockage, l’horloge et les rendus ;
- `adapters` implémentent filesystem, SQLite, JSON, Markdown et HTTP local ;
- `entrypoints` collectent l’intention sans contenir de logique métier ;
- `bootstrap` compose une seule application.

## Source runtime de vérité

```text
NormalizedObservationRequest
+ ObservationPlan
+ AnalysisProfile
```

Ces objets déterminent le comportement. Les scanners, analyseurs, reporters et interfaces sont des exécutants ou projections de ce contrat.

## Contraintes

- un seul orchestrateur normal ;
- une seule API canonique `/api/v1` ;
- un seul client API partagé par l’UI ;
- aucun import interne de Wordbench ;
- aucun processus externe ;
- aucun write-back vers les workspaces ;
- analyses reproductibles pour les mêmes preuves, profils et versions ;
- compatibilité future par schémas et adaptateurs publics, jamais par couplage interne.
