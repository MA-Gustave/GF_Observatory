# Observatory × GF WordBench — validation ciblée

## Objectif

Observatory inventorie les langues GF de la RGL et orchestre **des exécutions WordBench indépendantes, une langue à la fois**, sans modifier la RGL ni le dépôt WordBench. L'objectif final est de tester seulement les constructions requises par ChatSystem, pas toute la morphologie ou les temps littéraires.

## Deux modes à ne pas confondre

| Mode | Outil | Mesure | Limite |
| --- | --- | --- | --- |
| `quick` | WordBench standard : `validate --mode quick --target ...` | Réussite de compilation/validation du module public choisi (`Syntax`, sinon `Grammar`, `Lang`, `Cat`, `Res`) | **Aucune conclusion** sur les 15 capacités ChatSystem. Le nombre de capacités non vérifiées reste identique. |
| `practical` | Extension facultative `gf_wordbench.practical.cli run` | Un sous-ensemble de scénarios GF définis par le profil de couverture ChatSystem, comparés à des sorties de référence linguistiquement validées | Un profil de validation WordBench et les `.gfs`/`gold` sont nécessaires **pour chaque langue**. |

Les états `ready`, `needs_work` et `unverified` sont gérés par `tools/practical_catalog.py`. Un retour `quick=ok` n'est jamais transformé en `ready`.

## Utilisation de l'interface `.pyw`

1. Extraire ce dépôt dans `C:\mycode\Grammatical-Framework\GF_Observatory` (ou un autre emplacement).
2. Vérifier la RGL et le chemin du dépôt WordBench dans l'interface.
3. Cliquer sur **Scanner les langues**.
4. Sélectionner une ou quelques langues et choisir le mode `quick`.
5. Cliquer sur **Tester sélection**. Après un premier échantillon, le bouton **Tester toutes** permet une exécution séquentielle confirmée.
6. Inspecter la colonne **WB rapide** et les journaux `wordbench_logs/<code>_quick.log`.

Chaque processus WordBench est limité par un délai de 90 secondes dans l'interface ; un maximum de 70 secondes est affecté à la compilation `quick`. **Arrêter après cette langue** demande l'arrêt du lot après le processus en cours.

Les résultats se trouvent dans le dossier de sortie :
- `rgl_inventory.json`, `practical_catalog.json`, `practical_catalog.csv` ;
- `wordbench_quick_results.json` après des tests `quick` ;
- `wordbench_practical_executions.json` après des tests `practical` ;
- `wordbench_logs/` pour consulter les erreurs d'exécution ;
- `wordbench_identity_map.json` pour relier un code RGL (`Eng`) à la clé de langue WordBench (`english`).

## Mode pratique (`practical`)

Ce mode suppose l'installation **distincte** de l'extension `gf_wordbench.practical.cli` dans WordBench (le correctif WordBench communiqué précédemment). Il ne modifie pas WordBench automatiquement.

La zone **Profils WordBench par langue** doit référencer un dossier ayant la structure :

```text
mes_profils/
    Eng/project.toml
    Fre/project.toml
    Sqi/project.toml
```

Chaque `project.toml` doit enregistrer les **15 scénarios obligatoires** du profil `profiles/practical_generation_v1.json`, plus un checkpoint compilable, et pointer vers les scénarios `.gfs` et leurs fichiers gold. Le profil doit respecter les contrats WordBench. Sans ces fichiers, le résultat est `not_tested` ou `unverified`, **pas** `needs_work`.

Une fois WordBench exécuté, les preuves `summary.json`, `manifest.json` et `practical_coverage.json` sont traitées par le catalogue existant. Pour alimenter les colonnes de couverture, Observatory découvre automatiquement le sous-dossier `wb_artifacts` du dossier de sortie après un test. Si les résultats sont ailleurs, configurer **Rapports WordBench** explicitement. Les vérifications d’intégrité et de concordance avec le profil restent obligatoires.

**Limitation du prototype :** cette mise à jour ne fournit pas encore de scénarios GF et de golds linguistiquement revus pour les 15 fonctions dans chacune des langues. Elle rend l'orchestration et l'inventaire de compilation opérationnels ; la validation sémantique complète dépend de cette batterie de scénarios.

## CLI équivalente

Depuis le dossier `GF_Observatory` :

```powershell
py -3 tools\rgl_inventory.py --rgl-root 'C:\mycode\Grammatical-Framework\gf-rgl' --output 'C:\Users\Public\GF_Observatory_Diagnostic\rgl_inventory.json'
py -3 tools\wordbench_runner.py --inventory 'C:\Users\Public\GF_Observatory_Diagnostic\rgl_inventory.json' --rgl-root 'C:\mycode\Grammatical-Framework\gf-rgl' --wordbench-root 'C:\mycode\Grammatical-Framework\GF_Wordbench' --output-dir 'C:\Users\Public\GF_Observatory_Diagnostic' --codes Eng Fre Sqi --mode quick
```

Le runner utilise `python -m gf_wordbench validate ...` et non un second compilateur GF. Les fichiers GF sont lus, pas modifiés. Les preuves des tests doivent toujours être interprétées selon le niveau réellement exécuté.

## Politique d'évaluation

Une langue est `ready` pour ChatSystem uniquement si tous les scénarios obligatoires pertinents sont réussis et validés contre les golds pour chaque domaine. Une erreur de syntaxe/compilation dans `quick` indique un problème de compilation du module cible, mais ne démontre pas quelles fonctions sémantiques sont absentes. Les faux candidats techniques (`Abs`, `Cnc`, `Ext`, `TMP`) sont écartés de l'inventaire RGL.

## Versions du diagnostic

Le fichier `.pyw` autonome et les modules Python du dépôt utilisent la même règle
de découverte : exclusion des pseudo-codes techniques (`Abs`, `Cnc`, `Ext`,
`TMP`) sans éliminer les langues partielles telles que `Sqi`. Les anciens
inventaires doivent être rescannés pour bénéficier de la correction.

**Important :** un test `quick` réussi ne transforme jamais une langue en
« prête pour ChatSystem ». Les profils par langue, `.gfs` et sorties golden
restent nécessaires pour les 15 validations fonctionnelles.

## Correctif 0.3.2 — WordBench non trouvé malgré son installation

Si le bouton « Tester sélection » annonçait
`Dépôt WordBench non trouvé (src/gf_wordbench/__init__.py absent)`,
l'ancienne interface exigeait trop strictement un seul chemin.

Le diagnostic recherche désormais (sans modifier les sources) un dépôt qui
contient **directement** `src/gf_wordbench/__init__.py`, y compris les deux
structures suivantes :

```text
C:\mycode\Grammatical-Framework\GF_Wordbench\src\gf_wordbench\__init__.py
C:\mycode\Grammatical-Framework\GF_Wordbench\GF_Wordbench\src\gf_wordbench\__init__.py
```

La zone « Dépôt GF WordBench » est toujours éditable et peut pointer vers
le dossier parent. Le bouton **Détecter WordBench** repère et renseigne le
vrai chemin. Un dossier absent déclenche un avertissement avant le lancement,
plutôt qu'une exception avec traceback. La CLI `tools/wordbench_runner.py`
accepte elle aussi le dossier parent imbriqué.

La présence de WordBench ne garantit ni la présence du compilateur GF, ni celle
des scénarios et fichiers golden pour le mode `practical`. Commence par
`quick` sur **Eng** seulement, puis inspecte son journal.


## Correctif 0.3.3 : journaux, thread UI et erreurs WordBench

La fenêtre a deux rangées de boutons pour que **Détecter WordBench** et **Voir journal WB** soient accessibles même sur une résolution de 1024 px. Les erreurs d'Observatory sont visibles dans l'onglet Diagnostic et écrites dans `observatory_last_error.log` (dossier de sortie). Les erreurs de lancement WordBench sont inscrites dans `wordbench_quick_results.json` et dans `wordbench_logs/<Code>_quick.log` ; elles n'équivalent pas à des capacités linguistiques manquantes.

Sur la copie WordBench du snapshot, le CLI `validate --mode quick` a retourné, dans un test local sans GF, une erreur de configuration `The validation application requires a resolved RunConfig.` (sortie code 2). L'interface la rend désormais visible sous `wordbench_runconfig_unresolved` et conserve `unverified` pour le profil ChatSystem. La validation d'un GF installé reste distincte.
