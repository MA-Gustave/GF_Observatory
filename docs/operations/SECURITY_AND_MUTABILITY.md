# GF Observatory — Security and Mutability

| Champ | Valeur |
|---|---|
| Document role | Security authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Invariants cœur

```text
read_only_workspaces = true
allow_external_commands = false
allow_workspace_writes = false
```

Ils ne sont pas configurables.

## Écritures autorisées

Uniquement sous le répertoire d’état Observatory :

- base SQLite ;
- cache ;
- preuves retenues ;
- rapports ;
- journaux ;
- fichiers temporaires atomiques.

## Contrôles

- chemins canoniques et confinés ;
- liens symboliques contrôlés ;
- tailles et nombre de fichiers bornés ;
- parsing JSON défensif ;
- hachage avant confiance ;
- aucune désérialisation exécutable ;
- permissions locales minimales ;
- redaction des secrets ;
- écritures atomiques.
