# GF Observatory — Analysis Profiles

| Champ | Valeur |
|---|---|
| Document role | Analysis-profile authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Profil canonique

Un profil définit la structure de la matrice, les pondérations et les règles de blocage.

```text
profile_id
profile_version
subject_type
zones[]
signals[]
weights
required_signals
blocking_rules
freshness_policy
not_applicable_policy
strategy_thresholds
health_rules_version
```

## Profil cœur

```text
profile_id      = gf-observatory-core
profile_version = 1.0
score_scale     = 0..10
zones           = A, B, C, D
signals         = 14
```

## Invalidation

Une analyse dérivée est identifiée par :

```text
observation_fingerprint
profile_id
profile_version
analyzer_id
analyzer_version
```

Toute modification de profil ou d’analyseur invalide seulement les résultats dérivés. Elle ne force pas une nouvelle ingestion lorsque l’observation source reste valide.

## Compatibilité

Un profil externe peut être importé s’il respecte l’enveloppe commune, les statuts de preuve et l’échelle canonique. Les mappings spécifiques restent dans un adaptateur.
