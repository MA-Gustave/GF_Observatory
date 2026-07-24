# GF Observatory — Evidence Matrix

| Champ | Valeur |
|---|---|
| Document role | Evidence-matrix authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Objectif

La matrice synthétise les preuves observées sans remplacer les validations Wordbench. Elle est produite par un orchestrateur unique et des scanners one-shot sans effet de bord.

## Quatre zones et quatorze signaux

### Zone A — Structure et identité

| Signal | Signification |
|---|---|
| `IDNT` | identité du workspace et du projet |
| `CONF` | configuration lisible et cohérente |
| `SCHE` | schémas identifiés et compatibles |
| `MANI` | manifeste présent et interprétable |

### Zone B — Preuves et données

| Signal | Signification |
|---|---|
| `SUMM` | résumé structuré disponible |
| `RAWE` | preuves brutes référencées |
| `HASH` | intégrité vérifiée |
| `FRESH` | fraîcheur conforme au profil |

### Zone C — Capacité opérationnelle observée

| Signal | Signification |
|---|---|
| `COMP` | compilation réussie observée |
| `SCEN` | scénarios exécutés et interprétables |
| `ARTF` | artefacts attendus présents |

### Zone D — Qualité et gouvernance

| Signal | Signification |
|---|---|
| `GOLD` | golds et comparaisons observés |
| `REGR` | régressions et couverture observées |
| `GATE` | gates d’acceptation/release observées |

## Cellule canonique

```text
signal_id
score
status
confidence
evidence_refs
observed_at
producer_id
producer_version
profile_id
profile_version
```

## Exécution

1. calcul du fingerprint ;
2. lecture des inventaires prérequis ;
3. un scan par zone ;
4. lookups par projet ;
5. synthèse des zones ;
6. maturité, stratégie et santé ;
7. écriture de la matrice et du fingerprint.

## Stratégie d’analyse

```text
HIGH_ROAD  analyse complète, preuves compatibles et suffisantes
SAFE_MODE  analyse conservatrice limitée, preuves partielles ou anciennes
SKIP       aucune analyse fiable possible
```

Cette stratégie contrôle le chemin d’analyse d’Observatory. Elle ne commande aucune compilation ou modification externe.

## Règles

- score borné à `0..10` ;
- `MISSING`, `STALE` et `INVALID` ne deviennent jamais silencieusement zéro ;
- un blocage individuel n’est jamais masqué par une moyenne ;
- une matrice ne lit pas les workspaces après ingestion ;
- mêmes observation, profil et versions produisent le même résultat.
