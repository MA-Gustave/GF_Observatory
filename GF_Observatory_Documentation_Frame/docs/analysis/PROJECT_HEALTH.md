# GF Observatory — Project Health

| Champ | Valeur |
|---|---|
| Document role | Project-health authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Propriétaire

`ProjectHealthEvaluator` est l’unique propriétaire du statut synthétique.

## Entrées

- observation fraîche sélectionnée ;
- matrice active ;
- diagnostics bloquants ;
- stratégie d’analyse ;
- statut Wordbench source ;
- règles `health_rules_version` du profil.

## Sorties

```text
HEALTHY
DEGRADED
BLOCKED
UNKNOWN
```

## Règles minimales

- `HEALTHY` : analyse `HIGH_ROAD`, aucune preuve obligatoire invalide ou manquante, aucun blocage ;
- `DEGRADED` : analyse possible en `SAFE_MODE` ou preuve non critique manquante/stale ;
- `BLOCKED` : incompatibilité, intégrité invalide, blocage déclaré ou échec source bloquant ;
- `UNKNOWN` : aucune observation admissible ou données insuffisantes pour conclure.

Le calcul retourne également `reason_codes[]`, `evidence_refs[]` et `rules_version`.
