# GF Observatory — Artifact Ingestion

| Champ | Valeur |
|---|---|
| Document role | Ingestion authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Entrées admissibles

- répertoire de run Wordbench ;
- bundle exporté conforme au contrat public ;
- artefacts structurés explicitement listés par le manifeste.

## Pipeline

```text
locate
→ identify schema
→ choose reader
→ read once
→ verify manifest
→ normalize evidence
→ build immutable observation
→ retain audit subset
```

## Registre de lecteurs

Chaque lecteur déclare :

```text
reader_id
reader_version
supported_schema_id
supported_version_range
required_artifacts
optional_artifacts
normalization_contract
```

## Compatibilité

- version supportée : ingestion normale ;
- version plus récente compatible : ingestion avec avertissement explicite ;
- champ obligatoire inconnu : `INCOMPATIBLE` ;
- manifeste ou hachage invalide : `INVALID` ;
- preuve absente mais optionnelle : observation partielle ;
- preuve obligatoire absente : blocage du niveau dépendant.
