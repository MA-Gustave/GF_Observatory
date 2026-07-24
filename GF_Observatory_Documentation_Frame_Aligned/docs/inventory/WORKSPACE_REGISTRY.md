# GF Observatory — Workspace Registry

| Champ | Valeur |
|---|---|
| Document role | Workspace-registry authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Identité

```text
workspace_id
label
canonical_path
enabled
registered_at
last_seen_at
project_identity
metadata
```

`workspace_id` est stable après déplacement uniquement lorsqu’une identité de projet publique permet de confirmer la continuité. Sinon, un nouvel enregistrement est créé.

## Découverte

Le registre ne découvre pas silencieusement tout le disque. Les racines autorisées sont configurées et l’ajout d’un workspace est explicite.

## Normalisation

- chemin canonique ;
- contrôle de racine ;
- détection de collision ;
- refus des liens symboliques sortant des racines ;
- conservation de l’identité source séparément de l’identité locale.
