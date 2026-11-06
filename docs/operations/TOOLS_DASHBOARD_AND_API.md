# GF Observatory — Tools Dashboard and API

| Champ | Valeur |
|---|---|
| Document role | Tools-registry authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Principe

L’interface outils est orientée workflow. Elle expose des cas d’utilisation internes allowlistés, jamais un terminal ou une commande arbitraire.

## API

```text
GET  /api/v1/admin/tools/registry
POST /api/v1/admin/tools/run
```

## Métadonnées d’outil

```text
tool_id
label
description
workflow_tags
allowed_arguments
mutability
power_user_only
timeout_seconds
output_limit_bytes
result_schema_id
implementation_status
verification_status
```

## Workflows

- **Recommended** : registre → observation → matrice → santé → rapport ;
- **Inventory** : workspaces, identités et collisions ;
- **Evidence** : ingestion, manifestes, hachages et fraîcheur ;
- **Analysis** : matrice, profils, readiness et tendances ;
- **Diagnostics** : findings, incohérences et références cassées ;
- **Contracts** : schémas, API, configuration et compatibilité ;
- **Power user** : lecteurs et scanners isolés, sans écriture source.

## Sécurité

- aucune exécution shell ;
- arguments validés par schéma ;
- outils mutables limités au stockage Observatory ;
- aucun secret dans argv ou les logs ;
- sorties bornées ;
- request ID et journal structuré ;
- mêmes cas d’utilisation que la CLI et l’API standard.

## UI

Une éventuelle UI locale possède :

- un seul client API ;
- un sélecteur de workflow ;
- un mode normal curaté ;
- un mode power-user qui modifie la visibilité, pas les permissions ;
- aucune logique de scoring côté frontend.
