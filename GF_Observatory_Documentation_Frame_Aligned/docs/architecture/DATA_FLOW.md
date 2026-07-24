# GF Observatory — Data Flow

| Champ | Valeur |
|---|---|
| Document role | Data-flow authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## 1. Requête

```text
entrée externe
→ validation de transport
→ RequestNormalizer
→ NormalizedObservationRequest
```

## 2. Planification

```text
requête normalisée
→ résolution du workspace et du run
→ ObservationPlanner
→ ObservationPlan versionné
```

## 3. Observation

```text
plan
→ localisation
→ lecteurs versionnés
→ vérification du manifeste
→ EvidenceBinding
→ ObservationSnapshot immuable
→ persistance
```

## 4. Analyse

```text
observation + AnalysisProfile
→ fingerprint/cache
→ scanners one-shot par zone
→ matrice
→ santé + maturité + readiness + diagnostics
→ AnalysisResult
```

## 5. Projection

```text
AnalysisResult
→ ResponseMapper
→ terminal / JSON / Markdown / API / UI
```

## Règle d’unicité

Un artefact source est lu pendant l’ingestion. Les analyses et rapports utilisent ensuite l’observation persistée identifiée par son fingerprint, son lecteur et sa version de schéma.
