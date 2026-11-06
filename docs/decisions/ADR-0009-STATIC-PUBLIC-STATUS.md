# ADR-0009 — Static Public Status

| Champ | Valeur |
|---|---|
| Document role | Architecture decision record |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Décision

L’état public détaillé des langues est publié comme site statique généré par le module `reporting`.

```text
persisted AnalysisResult
→ PublicStatusProjector
→ public allowlist and redaction
→ status.json
→ static HTML/CSS/JS
→ GitHub Pages on the owner personal account
```

La publication ne déploie ni l’API Observatory, ni SQLite, ni une interface d’administration.

Le fournisseur initial est **GitHub Pages**, depuis un dépôt public `gf-observatory-status` appartenant au compte personnel du propriétaire. La source est la branche `main`, dossier `/(root)`. L’adresse canonique suit le modèle :

```text
https://<github-username>.github.io/gf-observatory-status/
```

## Raisons

- surface opérationnelle minimale ;
- aucun serveur à maintenir ;
- séparation stricte entre observation locale et consultation publique ;
- déploiement reproductible et facile à remplacer ;
- configuration GitHub Pages disponible sans serveur ni domaine personnalisé.

## Conséquences

- les données ne sont pas temps réel ;
- chaque publication représente un snapshot horodaté ;
- les détails interactifs sont calculés avant publication ou rendus à partir de `status.json` ;
- l’automatisation est optionnelle et ne modifie pas le contrat public.

## Autorité détaillée

[`../publishing/PUBLIC_STATUS_SITE.md`](../publishing/PUBLIC_STATUS_SITE.md)

[`../publishing/GITHUB_PAGES_DEPLOYMENT.md`](../publishing/GITHUB_PAGES_DEPLOYMENT.md)
