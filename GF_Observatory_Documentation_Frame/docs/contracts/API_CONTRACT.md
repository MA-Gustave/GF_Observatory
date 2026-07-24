# GF Observatory — API Contract

| Champ | Valeur |
|---|---|
| Document role | Public API authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Base canonique

```text
/api/v1
```

Une seule application backend et un seul routeur public sont autorisés. L’UI locale utilise un client API partagé.

## Routes publiques

```text
GET  /api/v1/health/live
GET  /api/v1/health/ready
GET  /api/v1/workspaces
GET  /api/v1/workspaces/{workspace_id}
GET  /api/v1/observations
GET  /api/v1/observations/{observation_id}
GET  /api/v1/matrix
GET  /api/v1/reports/status
GET  /api/v1/reports/trends/{workspace_id}
```

## Routes d’administration locale

```text
POST   /api/v1/admin/workspaces
DELETE /api/v1/admin/workspaces/{workspace_id}
POST   /api/v1/admin/observe
GET    /api/v1/admin/tools/registry
POST   /api/v1/admin/tools/run
```

## Enveloppe de succès

```json
{
  "data": {},
  "meta": {
    "request_id": "...",
    "contract_version": "1.0",
    "generated_at": "..."
  }
}
```

## Enveloppe d’erreur

```json
{
  "error": {
    "code": "OBSERVATORY_ERROR_CODE",
    "message": "Human-readable message",
    "details": {},
    "request_id": "..."
  }
}
```

## Règles

- aucune logique métier dans les routes ;
- réponses et erreurs versionnées ;
- séparation publique/admin ;
- outils strictement allowlistés ;
- aucun argument secret dans les requêtes d’outil ;
- tests de contrat obligatoires pour chaque route.
