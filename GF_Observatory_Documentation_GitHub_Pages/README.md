# GF Observatory

| Champ | Valeur |
|---|---|
| Document role | Product entry point |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

GF Observatory est un produit compagnon indépendant et en lecture seule. Il observe plusieurs workspaces GF Wordbench à partir de leurs artefacts publics versionnés, conserve des observations traçables et produit des analyses consolidées.

## Contrat essentiel

- Wordbench reste l’autorité pour la validation et la release d’un projet actif.
- Observatory ne lance ni GF ni Wordbench et ne modifie aucun workspace.
- Les interfaces CLI, API et UI utilisent les mêmes cas d’utilisation.
- Le runtime suit un cadre canonique fondé sur la normalisation, la planification, la résolution de preuves, l’analyse et le rendu.
- Toute donnée dérivée conserve l’identité de son profil, de son analyseur et de ses preuves sources.
- Un export statique optionnel permet de consulter publiquement l’état détaillé des langues sans exposer le runtime local.
- L’hébergement initial est GitHub Pages sur le compte personnel du propriétaire : `https://<github-username>.github.io/gf-observatory-status/`.

## Identité technique cible

```text
Produit       : GF Observatory
Package       : gf-observatory
Commande      : gf-observatory
API           : /api/v1
Configuration : observatory.toml
État local    : .gf-observatory/
```

Commencer par [`docs/00_START_HERE.md`](docs/00_START_HERE.md).
