# GF Observatory — Evidence Retention

| Champ | Valeur |
|---|---|
| Document role | Evidence-retention authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Décision

Observatory conserve localement un sous-ensemble structuré et vérifié des preuves nécessaires à l’audit.

## Conservé par défaut

- `summary.json` ;
- `manifest.json` ;
- métadonnées de schéma et producteur ;
- statuts et résultats structurés requis par le profil ;
- hachages, tailles et références des preuves brutes ;
- diagnostics Observatory.

## Non copié par défaut

- gros logs bruts ;
- binaires ;
- PGF ;
- sources GF ;
- fichiers non référencés par le manifeste.

## Stockage

Les objets retenus sont adressés par contenu :

```text
.gf-observatory/evidence/sha256/<prefix>/<digest>
```

## États de référence

```text
AVAILABLE
SOURCE_MISSING
RETAINED_COPY
HASH_MISMATCH
PURGED
```

La copie locale ne transforme pas Observatory en autorité sur la preuve ; elle garantit seulement la vérifiabilité historique de ce qui a été observé.
