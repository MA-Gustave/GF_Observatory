# GF Observatory — Déploiement GitHub Pages personnel

| Champ | Valeur |
|---|---|
| Document role | GitHub Pages deployment authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; live deployment pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Décision

Le site public de GF Observatory est hébergé avec **GitHub Pages sur le compte GitHub personnel du propriétaire**.

Configuration canonique :

```text
Compte GitHub : <github-username>
Dépôt public  : gf-observatory-status
Branche       : main
Source Pages  : /(root)
Adresse       : https://<github-username>.github.io/gf-observatory-status/
```

`<github-username>` est le seul paramètre d’installation à remplacer. Il doit correspondre exactement au nom du compte GitHub qui possède le dépôt.

Aucun domaine personnalisé, serveur, conteneur, base distante ou workflow GitHub Actions n’est requis pour la première version.

## 1. Créer le dépôt public

Depuis l’interface GitHub du compte personnel :

1. créer un nouveau dépôt nommé exactement `gf-observatory-status` ;
2. choisir la visibilité **Public** ;
3. ne pas ajouter de code Observatory, de base SQLite, de journaux ou de fichiers de workspace ;
4. cloner le dépôt localement à côté du dépôt Observatory.

Disposition recommandée :

```text
<development-root>/
├── gf-observatory/
└── gf-observatory-status/
```

## 2. Générer le site dans le dépôt

Depuis le dépôt Observatory :

```text
gf-observatory publish \
  --output ../gf-observatory-status \
  --profile public
```

Le répertoire cible contient seulement :

```text
gf-observatory-status/
├── index.html
├── app.js
├── style.css
└── status.json
```

La commande doit refuser d’écrire dans un répertoire contenant des fichiers non gérés, sauf option explicite de remplacement sûre.

## 3. Publier la première version

```text
cd ../gf-observatory-status
git add index.html app.js style.css status.json
git commit -m "Publish language status"
git push -u origin main
```

Dans le dépôt GitHub :

```text
Settings
→ Pages
→ Build and deployment
→ Source: Deploy from a branch
→ Branch: main
→ Folder: /(root)
→ Save
```

GitHub affiche ensuite l’adresse effective du site. L’adresse attendue est :

```text
https://<github-username>.github.io/gf-observatory-status/
```

Une fiche de langue utilise une route par fragment :

```text
https://<github-username>.github.io/gf-observatory-status/#/languages/fr
```

Les routes par fragment évitent toute configuration de réécriture côté hébergeur.

## 4. Mettre le site à jour

Chaque nouvelle publication reste manuelle et explicite :

```text
gf-observatory observe --all
gf-observatory publish \
  --output ../gf-observatory-status \
  --profile public

cd ../gf-observatory-status
git add index.html app.js style.css status.json
git commit -m "Update language status"
git push
```

Chaque poussée vers `main` publie le nouveau snapshot depuis la racine du dépôt.

## 5. Configuration Observatory

Exemple dans `observatory.toml` :

```toml
[publication]
profile_id = "public"
output_directory = "../gf-observatory-status"
public_base_url = "https://<github-username>.github.io/gf-observatory-status/"
include_diagnostics = "counts-only"
include_evidence_refs = true
```

`public_base_url` sert uniquement à produire des liens publics cohérents. Il ne donne aucun accès à GitHub et ne contient aucun jeton.

## 6. Authentification Git

L’authentification du `git push` relève de Git, pas d’Observatory.

Utiliser l’une des méthodes déjà configurées sur la machine :

- Git Credential Manager ;
- clé SSH ;
- GitHub CLI.

Observatory ne stocke jamais de mot de passe, de jeton personnel ou de clé SSH.

## 7. Contrôle avant publication

Avant chaque `git push`, vérifier :

```text
[ ] status.json valide le schéma gf-observatory.public-status/1.0
[ ] generated_at est présent
[ ] profile_id et profile_version sont présents
[ ] aucun chemin local n’est publié
[ ] aucun secret ni journal brut n’est publié
[ ] index.html charge status.json avec un chemin relatif
[ ] la fiche #/languages/fr fonctionne localement
[ ] seuls les quatre fichiers générés sont ajoutés au commit
```

Test local facultatif :

```text
cd ../gf-observatory-status
python -m http.server 8080
```

Puis ouvrir :

```text
http://localhost:8080/
```

Ce serveur est uniquement un test local. Il ne fait pas partie du déploiement public.

## 8. Non-objectifs initiaux

La première version n’utilise pas :

- GitHub Actions ;
- domaine personnalisé ;
- publication automatique planifiée ;
- API publique ;
- authentification des visiteurs ;
- analytics ;
- formulaire ou écriture depuis le navigateur.

Ces capacités nécessitent une décision distincte. Elles ne doivent pas complexifier le lancement initial.

## 9. Références GitHub

- Configuration d’une source de publication : `https://docs.github.com/fr/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site`
- Présentation de GitHub Pages : `https://docs.github.com/fr/pages/getting-started-with-github-pages/what-is-github-pages`
