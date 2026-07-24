# GF Observatory — Wordbench Artifact Contract

| Champ | Valeur |
|---|---|
| Document role | External artifact contract |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Principe

Observatory consomme uniquement les artefacts publics versionnés. Aucun chemin interne, modèle privé ou import Python de Wordbench n’est requis.

## Bundle minimal

```text
summary.json
manifest.json
```

Des preuves supplémentaires peuvent être déclarées par le manifeste : rapports, résultats de scénarios, métadonnées GF, release gates, logs et fichiers de reproductibilité.

## Champs requis

```text
schema_id
schema_version
project_id
run_id
created_at
producer_id
producer_version
status
artifacts[]
```

Chaque entrée de manifeste porte au minimum :

```text
role
relative_path
size_bytes
sha256
required
```

## Autorité

- Wordbench possède le statut source.
- Observatory possède le statut de lecture et d’interprétation.
- Observatory ne requalifie jamais un échec Wordbench en succès.
- Les champs inconnus sont conservés dans `extensions` lorsqu’ils ne compromettent pas la sécurité.
