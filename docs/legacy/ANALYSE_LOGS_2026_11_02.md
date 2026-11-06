# Analyse des journaux de 67 langues — 2026-11-02

Les résultats fournis par l'utilisateur montrent 52 compilations réussies,
9 erreurs et 6 délais dépassés (90 s/langue). Aucun de ces résultats ne
mesure la fidélité des réalisations linguistiques génération pratique.

| Langue(s) | Observation initiale | Action / prudence |
|---|---|---|
| Cat | Code 3221225786 / 0xC000013A | Processus Windows interrompu ; retester isolément |
| Gus, Kam, Swa | `File CatBantu.gf does not exist` | Ajouter `src/bantu` au chemin GF |
| Sco | `File NounEng.gf does not exist` | Ajouter `src/english` pour Sco |
| Zul | `File CatExt.gf does not exist` | Ajouter `src/zulu/abstract_ext` pour Zul |
| Grc | `constant not found` (API Constructors.gf) | Évaluer l'interface RGL, sans prétendre qu'une fonction génération pratique manque |
| Lit | `unknown label hasDot` dans NumeralLit.gf | Erreur de typage/linéarisation à investiguer |
| Tur | `Internal error in Compute.Concrete` | Erreur interne du compilateur GF 3.12 ; collecter un repro minimal |
| Fre, Ita, Lav, Mlt, Por, Ron | `wordbench_timeout` | Retester avec délai augmenté et surveiller l'utilisation mémoire |

Les correctifs de chemins ne prouvent pas que les grammaires affectées
compileront désormais : seul un nouveau test sur la RGL réelle peut le dire.

Procédure recommandée : lancer Observatory, **Scanner les langues**, puis
**Retester échecs/délais** en `quick`, avec 180 ou 300 secondes par langue.
Conserver `wordbench_quick_results.json` et les journaux après le nouveau scan.
