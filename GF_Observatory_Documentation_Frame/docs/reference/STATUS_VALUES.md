# GF Observatory — Status Values

| Champ | Valeur |
|---|---|
| Document role | Status-vocabulary authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Preuve

```text
OBSERVED
MISSING
STALE
INVALID
INCOMPATIBLE
NOT_APPLICABLE
UNREACHABLE
```

## Observation

```text
COMPLETE
PARTIAL
STALE
INCOMPATIBLE
INVALID
UNREACHABLE
DISABLED
```

## Cycle

```text
OK
PARTIAL
ERROR
```

## Stratégie

```text
HIGH_ROAD
SAFE_MODE
SKIP
```

## Santé

```text
HEALTHY
DEGRADED
BLOCKED
UNKNOWN
```

## Règles

- le statut source est conservé séparément ;
- `UNREACHABLE` ne signifie pas échec fonctionnel ;
- `INCOMPATIBLE` n’est pas converti en `UNKNOWN` ;
- les statuts persistés sont ASCII, en majuscules et versionnés ;
- toute projection publique conserve les `reason_codes`.
