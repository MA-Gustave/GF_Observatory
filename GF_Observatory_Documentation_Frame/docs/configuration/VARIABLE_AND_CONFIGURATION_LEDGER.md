# GF Observatory — Variable and Configuration Ledger

| Champ | Valeur |
|---|---|
| Document role | Variable-ledger authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Variables d’environnement

| Variable | Rôle | Défaut |
|---|---|---|
| `GF_OBSERVATORY_CONFIG` | chemin du fichier TOML | `observatory.toml` |
| `GF_OBSERVATORY_STATE_DIR` | répertoire d’état | `.gf-observatory` |
| `GF_OBSERVATORY_DB` | base SQLite | `<state>/observatory.db` |
| `GF_OBSERVATORY_API_BIND` | adresse locale | `127.0.0.1` |
| `GF_OBSERVATORY_API_PORT` | port local | `8765` |
| `GF_OBSERVATORY_LOG_LEVEL` | niveau de journal | `INFO` |
| `GF_OBSERVATORY_PROFILE` | profil actif | `gf-observatory-core@1.0` |

## Constantes gelées

```text
API_BASE_PATH          = /api/v1
STATE_SCHEMA_NAMESPACE = gf-observatory
SCORE_MIN              = 0.0
SCORE_MAX              = 10.0
DEFAULT_STRATEGIES     = HIGH_ROAD, SAFE_MODE, SKIP
```

## Codes d’erreur

```text
OBS_CONFIG_INVALID
OBS_WORKSPACE_NOT_FOUND
OBS_PATH_NOT_ALLOWED
OBS_SCHEMA_INCOMPATIBLE
OBS_MANIFEST_INVALID
OBS_HASH_MISMATCH
OBS_REQUIRED_ARTIFACT_MISSING
OBS_PROFILE_NOT_FOUND
OBS_TOOL_NOT_ALLOWED
OBS_STORAGE_ERROR
```

## Règles

- toute variable est documentée ici avant usage ;
- les secrets ne sont jamais requis pour le cœur local ;
- les constantes de contrat ne sont pas dupliquées dans le frontend ;
- les changements incompatibles suivent le protocole de schéma ;
- les anciennes variables disposent d’une fenêtre de migration explicite ou sont refusées.
