# GF Observatory — Observed Maturity and Readiness

| Champ | Valeur |
|---|---|
| Document role | Derived scoring authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Maturité observée

Somme pondérée des zones de la matrice, bornée à `0..10`. Elle mesure la richesse, la couverture, l’intégrité et la fraîcheur des preuves disponibles.

## Readiness observé

Plus haut niveau dont toutes les preuves obligatoires sont présentes, compatibles, fraîches et vérifiées.

| Niveau | Interprétation observable |
|---|---|
| `R0` | Workspace enregistré, aucune preuve admissible. |
| `R1` | Projet et artefacts localisés. |
| `R2` | Identité et schémas cohérents. |
| `R3` | Manifeste et intégrité vérifiés. |
| `R4` | Exécution GF réussie observée. |
| `R5` | Familles de validation linguistique déclarées comme passées. |
| `R6` | Acceptation et régressions satisfaites dans les preuves. |
| `R7` | Statut de release prêt et reproductibilité observée. |

## Règle conservatrice

```text
readiness_effectif = plus haut niveau dont toutes les preuves obligatoires sont OBSERVED et fraîches
```

Une maturité élevée ne compense pas un readiness faible. `R7` exige le statut source et les preuves correspondantes ; Observatory ne recalcule pas les gates.
