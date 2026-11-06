# GF Observatory — Reporting Overview

| Champ | Valeur |
|---|---|
| Document role | Reporting authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Principe

Les rapports projettent des `AnalysisResult` persistés. Ils ne relisent pas les workspaces et ne recalculent pas les scores.

## Formats

- terminal ;
- JSON ;
- Markdown ;
- réponse API ;
- vue UI locale ;
- site statique public optionnel.

## Enveloppe

```text
report_id
schema_id
schema_version
generated_at
subject_refs
observation_refs
profile_id
profile_version
analyzer_versions
status
matrix
health
maturity
readiness
diagnostics
trends
evidence_refs
```

## Règles

- chaque valeur dérivée indique son profil et sa version ;
- les références cassées restent visibles ;
- aucun rapport ne masque un sujet en échec ;
- la pagination et les filtres ne modifient pas les résultats ;
- CLI, API et UI rendent les mêmes décisions applicatives.

## Publication statique

Le `PublicStatusProjector` consomme uniquement des `AnalysisResult` persistés et produit le contrat `gf-observatory.public-status/1.0` ainsi que les fichiers statiques de consultation. Cette projection applique une allowlist et une redaction avant toute écriture.

Autorité : [`../publishing/PUBLIC_STATUS_SITE.md`](../publishing/PUBLIC_STATUS_SITE.md).
