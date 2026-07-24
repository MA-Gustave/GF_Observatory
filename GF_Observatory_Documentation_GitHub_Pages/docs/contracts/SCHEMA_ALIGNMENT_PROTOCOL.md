# GF Observatory — Schema Alignment Protocol

| Champ | Valeur |
|---|---|
| Document role | Schema-propagation authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Problème

Une modification isolée d’un champ peut désaligner le schéma persisté, le modèle de domaine, le lecteur, l’API, l’UI et les tests.

## Protocole obligatoire

Toute modification de contrat suit cet ordre :

1. mettre à jour l’autorité de schéma ;
2. mettre à jour le modèle de domaine ;
3. mettre à jour les lecteurs et writers ;
4. mettre à jour les mappings API et CLI ;
5. mettre à jour le client UI ;
6. mettre à jour fixtures, migrations et tests de contrat ;
7. mettre à jour le manifeste documentaire.

## Types de changement

- **additif compatible** : champ optionnel avec défaut explicite ;
- **additif requis** : nouvelle version mineure si négociable, majeure sinon ;
- **renommage ou suppression** : version majeure et migration ;
- **changement sémantique** : version majeure même si le type JSON ne change pas.

## Gate

Une PR de schéma est incomplète si l’un des éléments suivants manque :

```text
schema diff
compatibility decision
migration or reader behavior
contract tests
public documentation
rollback note
```
