# GF Observatory — Independence Contract

| Champ | Valeur |
|---|---|
| Document role | Product-boundary authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Tests d’indépendance

GF Observatory doit pouvoir être installé, testé et utilisé avec seulement :

- ses propres dépendances ;
- des bundles d’artefacts publics ;
- un stockage local ;
- une horloge et un filesystem en lecture seule.

## Interdictions

- import d’un package interne producteur ;
- lecture d’une base privée ;
- appel obligatoire à une API distante ;
- exécution d’un outil externe ;
- écriture dans un workspace observé ;
- dépendance d’interface envers une implémentation particulière.

## Compatibilité

Les intégrations futures utilisent des adaptateurs et schémas publics. La suppression d’un connecteur optionnel ne doit modifier ni le domaine ni les cas d’utilisation cœur.
