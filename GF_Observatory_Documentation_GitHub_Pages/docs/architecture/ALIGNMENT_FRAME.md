# GF Observatory — Alignment Frame

| Champ | Valeur |
|---|---|
| Document role | Interoperability-frame authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Objectif

Préserver une structure d’interopérabilité prête à l’emploi sans introduire de dépendance actuelle.

## Enveloppe commune

Tous les échanges alignables utilisent les champs suivants :

```text
contract_id
contract_version
subject_type
subject_id
profile_id
profile_version
producer_id
producer_version
observed_at
fingerprint
status
evidence_refs
extensions
```

## Espaces d’identifiants

- `plan_id` : comportement d’orchestration ;
- `profile_id` : définition des zones, signaux et seuils ;
- `tool_id` : cas d’utilisation allowlisté ;
- `schema_id` : forme persistée ou publique ;
- `status_set_id` : vocabulaire de statuts ;
- `producer_id` : composant ayant produit la donnée.

## Règles

1. Les identifiants sont stables, ASCII et versionnés.
2. Les extensions inconnues sont conservées lorsqu’elles sont sûres.
3. Les champs obligatoires inconnus produisent `INCOMPATIBLE`.
4. Les tables de correspondance vivent dans des adaptateurs, jamais dans le domaine.
5. Les données externes gardent leur identité d’origine.
6. Une compatibilité n’accorde aucune autorité supplémentaire au producteur externe.

## Résultat attendu

Un futur connecteur doit pouvoir se limiter à :

- un lecteur de schéma ;
- une table de correspondance des identifiants ;
- un profil compatible ;
- des tests de contrat.
