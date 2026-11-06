# GF Observatory — Configuration Reference

| Champ | Valeur |
|---|---|
| Document role | Configuration authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Fichier canonique

```text
observatory.toml
```

## Exemple

```toml
schema_id = "gf-observatory.config"
schema_version = "1.0"

[api]
base_path = "/api/v1"
bind = "127.0.0.1"
port = 8765

[state]
directory = ".gf-observatory"
database = ".gf-observatory/observatory.db"
evidence_directory = ".gf-observatory/evidence"
report_directory = ".gf-observatory/reports"

[observation]
max_run_age_hours = 168
verify_hashes = true
follow_symlinks = false

[analysis]
profile_id = "gf-observatory-core"
profile_version = "1.0"
cache_enabled = true

[publication]
profile_id = "public"
output_directory = "../gf-observatory-status"
public_base_url = "https://<github-username>.github.io/gf-observatory-status/"
include_diagnostics = "counts-only"
include_evidence_refs = true

[security]
allowed_roots = ["D:/gf-workspaces"]
```

## Précédence

```text
valeurs intégrées sûres
→ observatory.toml
→ variables d’environnement documentées
→ options CLI explicites
```

Une option de niveau inférieur ne peut contourner un invariant de sécurité.

## Paramètre GitHub personnel

`<github-username>` doit être remplacé par le propriétaire réel du dépôt `gf-observatory-status`. Aucun identifiant GitHub, mot de passe ou jeton n’est accepté dans `observatory.toml`.
