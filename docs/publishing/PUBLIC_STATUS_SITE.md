# GF Observatory — Public Status Site

| Champ | Valeur |
|---|---|
| Document role | Static publication authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Décision

GF Observatory publie l’état détaillé des langues sous la forme d’un **site statique généré**. Aucun service Observatory, aucune base SQLite et aucune route d’administration ne sont exposés sur Internet.

La commande canonique est :

```text
gf-observatory publish --output <directory> [--profile public]
```

Elle lit uniquement des `AnalysisResult` déjà persistés. Elle ne relit pas les workspaces, ne relance pas les scanners et ne recalcule pas les analyses.

## Sortie minimale

```text
<directory>/
├── index.html
├── app.js
├── style.css
└── status.json
```

`index.html` contient la structure accessible. `app.js` charge `status.json`, affiche la liste des langues et utilise des routes par fragment, par exemple `#/languages/fr`, pour ouvrir une fiche détaillée sans générer une page HTML par langue.

Aucun framework JavaScript, serveur applicatif, moteur de template hébergé ou base distante n’est requis.

## Vue d’ensemble

La page principale affiche au minimum :

```text
language_id
code
name
health
maturity
readiness
strategy
freshness
observed_at
trend
```

La fiche détaillée affiche :

- les quatre zones et leurs quatorze signaux ;
- le statut, la confiance et la fraîcheur de chaque signal ;
- la santé, la maturité et le readiness ;
- la stratégie d’analyse ;
- les tendances compatibles ;
- le nombre de diagnostics par sévérité ;
- les identifiants de preuves publiables.

## Contrat `status.json`

```json
{
  "schema_id": "gf-observatory.public-status",
  "schema_version": "1.0",
  "generated_at": "...",
  "profile_id": "public",
  "profile_version": "1.0",
  "languages": [
    {
      "language_id": "...",
      "code": "fr",
      "name": "French",
      "health": "HEALTHY",
      "maturity": 8.4,
      "readiness": "T6",
      "strategy": "HIGH_ROAD",
      "freshness": "FRESH",
      "observed_at": "...",
      "trend": "IMPROVED",
      "zones": {},
      "signals": [],
      "diagnostics": {
        "error": 0,
        "warning": 2,
        "info": 4
      }
    }
  ]
}
```

Les tableaux utilisent un ordre déterministe. Une modification incompatible du contrat incrémente sa version majeure.

## Profil public et redaction

L’export est fondé sur une allowlist. Le profil `public` autorise uniquement les champs explicitement documentés.

Ne sont jamais publiés par défaut :

- chemins absolus ou relatifs des workspaces ;
- contenu des journaux bruts ;
- variables d’environnement et secrets ;
- configuration d’administration ;
- contenu de fichiers source ;
- extraits diagnostiques non redigés ;
- identifiants internes permettant de localiser une machine ;
- routes ou outils d’administration.

Une référence de preuve publique est un identifiant opaque ou une URL explicitement déclarée publique. Elle n’est jamais reconstruite depuis un chemin local.

## Hébergement canonique

Le site est hébergé sur **GitHub Pages depuis le compte GitHub personnel du propriétaire**.

```text
Dépôt public : gf-observatory-status
Branche      : main
Source Pages : /(root)
Adresse      : https://<github-username>.github.io/gf-observatory-status/
```

`<github-username>` est remplacé une fois par le nom réel du compte GitHub. Aucun domaine personnalisé ni workflow GitHub Actions n’est requis au lancement.

La procédure détaillée appartient à [`GITHUB_PAGES_DEPLOYMENT.md`](GITHUB_PAGES_DEPLOYMENT.md).

## Publication manuelle

Le dépôt dédié contient seulement les quatre fichiers générés :

```text
gf-observatory publish --output ../gf-observatory-status --profile public
cd ../gf-observatory-status
git add --all
git commit -m "Update language status"
git push
```

Dans GitHub, Pages est configuré avec `Deploy from a branch`, la branche `main` et le dossier `/(root)`. Une automatisation pourra être ajoutée plus tard sans modifier le contrat d’export.

## Règles

- le site est une projection, jamais une source de vérité ;
- le site n’effectue aucun scoring côté navigateur ;
- le navigateur ne contacte pas l’API locale ;
- une publication incomplète échoue avant de remplacer la version précédente ;
- les fichiers sont écrits dans un répertoire temporaire puis remplacés atomiquement ;
- `status.json` contient le profil, les versions et la date de génération ;
- l’export peut afficher des données périmées uniquement avec un statut de fraîcheur explicite ;
- l’absence d’une langue ne doit jamais être interprétée comme un succès.
