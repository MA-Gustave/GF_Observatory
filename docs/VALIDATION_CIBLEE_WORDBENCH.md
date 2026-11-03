# Observatory × GF WordBench — validation ciblée

## Objectif

Observatory inventorie les langues GF de la RGL et orchestre **des exécutions WordBench indépendantes, une langue à la fois**, sans modifier la RGL ni le dépôt WordBench. L'objectif final est de tester seulement les constructions requises par génération pratique, pas toute la morphologie ou les temps littéraires.

## Trois modes à ne pas confondre

| Mode | Outil | Mesure | Limite |
| --- | --- | --- | --- |
| `light` | Composant de compilation WordBench, via la sonde Observatory | Compile seulement `CatXXX.gf` si ce module existe ; privilégie un diagnostic de structure peu coûteux | **Ne vérifie ni `GrammarXXX.gf`, ni les 15 capacités génération pratique.** Un résultat `ok` reste un signal partiel. |
| `quick` | Composant `gf_wordbench.validation.compilation.commands` appelé par une sonde Observatory (sans CLI `validate`) | Réussite de compilation/validation du module public choisi (`Syntax`, sinon `Grammar`, `Lang`, `Cat`, `Res`) | **Aucune conclusion** sur les 15 capacités génération pratique. Le nombre de capacités non vérifiées reste identique. |
| `practical` | Extension facultative `gf_wordbench.practical.cli run` | Un sous-ensemble de scénarios GF définis par le profil de couverture génération pratique, comparés à des sorties de référence linguistiquement validées | Un profil de validation WordBench et les `.gfs`/`gold` sont nécessaires **pour chaque langue**. |

Les états `ready`, `needs_work` et `unverified` sont gérés par `tools/practical_catalog.py`. Un retour `quick=ok` n'est jamais transformé en `ready`.

## Utilisation de l'interface `.pyw`

1. Extraire ce dépôt dans `C:\mycode\Grammatical-Framework\GF_Observatory` (ou un autre emplacement).
2. Vérifier la RGL et le chemin du dépôt WordBench dans l'interface.
3. Cliquer sur **Scanner les langues**.
4. Pour un premier passage léger, sélectionner une ou quelques langues et choisir `light`. Choisir `quick` lorsqu’une compilation complète du module public est nécessaire.
5. Cliquer sur **Tester sélection**. Après un premier échantillon, le bouton **Tester toutes** permet une exécution séquentielle confirmée.
6. Inspecter les colonnes **WB léger** / **WB rapide** et les journaux `wordbench_logs/<code>_light.log` ou `<code>_quick.log`.

Le délai est configurable de 5 à 3 600 secondes par langue. La valeur initiale est de **60 secondes en mode `light`** ; l’utilisateur peut choisir un autre délai, par exemple 300 secondes pour `quick`. **Arrêter après cette langue** demande l'arrêt du lot après le processus en cours.

Les résultats se trouvent dans le dossier de sortie :
- `rgl_inventory.json`, `practical_catalog.json`, `practical_catalog.csv` ;
- `wordbench_light_results.json` après les tests `light` ;
- `wordbench_quick_results.json` après les tests `quick` ;
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

Le mode `quick` appelle `tools/wordbench_quick_probe.py`, qui importe le composant de construction de commandes GF de WordBench et exécute **un seul module**, avec sorties conservées hors du dépôt. Le mode `practical` utilise `gf_wordbench.practical.cli` si installé. Les fichiers GF sont lus, pas modifiés. Les preuves des tests doivent toujours être interprétées selon le niveau réellement exécuté.

## Politique d'évaluation

Une langue est `ready` pour génération pratique uniquement si tous les scénarios obligatoires pertinents sont réussis et validés contre les golds pour chaque domaine. Une erreur de syntaxe/compilation dans `quick` indique un problème de compilation du module cible, mais ne démontre pas quelles fonctions sémantiques sont absentes. Les faux candidats techniques (`Abs`, `Cnc`, `Ext`, `TMP`) sont écartés de l'inventaire RGL.

## Versions du diagnostic

Le fichier `.pyw` intégré au dépôt et les modules Python partagent la même règle
de découverte : exclusion des pseudo-codes techniques (`Abs`, `Cnc`, `Ext`,
`TMP`) sans éliminer les langues partielles telles que `Sqi`. Les anciens
inventaires doivent être rescannés pour bénéficier de la correction.

**Important :** un test `quick` réussi ne transforme jamais une langue en
« prête pour génération pratique ». Les profils par langue, `.gfs` et sorties golden
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

Sur la copie WordBench du snapshot, le CLI `validate --mode quick` a retourné, dans un test local sans GF, une erreur de configuration `The validation application requires a resolved RunConfig.` (sortie code 2). L'interface la rend désormais visible sous `wordbench_runconfig_unresolved` et conserve `unverified` pour le profil génération pratique. La validation d'un GF installé reste distincte.


## Correctif 0.3.4 : vrai déclencheur de compilation ciblée et bon journal

L'ancien mode `quick` passait par `python -m gf_wordbench validate --mode quick`, mais
le snapshot WordBench reçu présente un défaut de routage : sa commande `validate`
transmet un `ValidateCommandRequest` au moteur qui exige un `RunConfig`
(`GF-WB-CONFIG-914`). L'erreur peut survenir **avant d'appeler GF**. Ce constat a
été reproduit séparément avec le code source WordBench du snapshot.

Pour conserver WordBench intact, le mode `quick` appelle maintenant
`tools/wordbench_quick_probe.py`. Cette sonde importe le constructeur canonique
`gf_wordbench.validation.compilation.commands.build_module_compile_command`,
puis lance le **compilateur GF réel** avec un module RGL sélectionné. La sonde
vérifie le code de retour et exige un fichier `.gfo` non vide et nouveau ; elle
journalise les erreurs de compilateur et les problèmes d'outillage. Le délai
est borné et les artefacts restent sous le dossier de sortie Observatory.

Cela utilise **une partie de WordBench**, pas toute sa chaîne de reporting et
validation. Une réussite `quick` ne constitue **pas** une preuve des 15 fonctions
génération pratique ; le mode `practical` et ses golds restent nécessaires.

L'interface garde maintenant la langue testée sélectionnée après chaque lot,
ouvre automatiquement le journal du premier échec, et propose les boutons
**Journal langue sélectionnée** et **Dernier échec WB**. Si `Eng` échoue, son
journal apparaît même si la première ligne du tableau est `Afr`.

**L'interface `.pyw` n'est plus destinée à être copiée hors du dépôt** : elle
requiert son dossier voisin `tools/`. Lancer le `.pyw` depuis le ZIP extrait
complet, comme demandé pour un projet unique et maintenable.

**Installation** : remplacer la version précédente d'Observatory avec ce ZIP,
relancer la fenêtre, scanner les langues, choisir **Eng** puis **Tester sélection**
en mode `quick`. En cas d'échec, transmettre
`wordbench_logs/Eng_quick.log` et `wordbench_quick_results.json`.


## v0.3.5 — résolution du compilateur GF

Lorsque le journal indique « Compilateur GF introuvable sur PATH », ce n'est
pas un échec linguistique : le processus n'a pas exécuté GF. Cliquer sur
**Détecter GF** ou choisir explicitement le fichier `gf.exe` dans le champ
**Compilateur GF (gf.exe)**. Observatory vérifie cette présence avant toute
exécution en lot et transmet l'exécutable par `--gf-exe` au probe Quick.
La détection est bornée : elle ne parcourt pas tout le disque C:.
L'installation ou la compilation de GF reste une étape externe.


### Correction 0.3.6 — recherche abstraite

Le compilateur cherche notamment `Grammar.gf` dans `gf-rgl/src/abstract`, en plus du dossier propre à la langue et des ressources partagées. Sans ce chemin, `GrammarEng.gf` échoue même avec GF 3.12 opérationnel. La fenêtre préremplit le GF 3.12 local lorsqu’il existe.


## Correctif 0.3.7 — processus cachés sous Windows

L’inventaire graphique ne lance pas de console. Lors des tests `quick` ou
`practical`, le lanceur Python de WordBench (enfant), `gf.exe` (petit-enfant)
et `taskkill.exe` (en cas de timeout) sont tous invoqués avec
`CREATE_NO_WINDOW`. Les sorties et diagnostics sont capturés et conservés
dans `wordbench_logs/`. La politique est partagée dans
`tools/windows_process.py` et reste compatible POSIX.

Pour éviter aussi la brève console produite par le lanceur `.bat`, lancer
`GF_Observatory_Diagnostic.pyw` directement (association Windows à `pythonw`).

## v0.3.9 — Test de structure économique pour les compilations coûteuses

Un `timeout` à **300 secondes** sur `GrammarLav.gf` ne signifie pas que le
letton échoue linguistiquement. Le test `quick` peut reconstruire de nombreuses
dépendances RGL. L’ancien audit contenait déjà `CatLav.gfo`, sans atteindre
`GrammarLav.gfo` avant la limite.

La nouvelle option **`light`** compile uniquement le module `Cat` déclaré dans
l’inventaire de la langue, avec le constructeur de commandes GF de WordBench.
Elle n’écrase pas les anciens résultats `quick`, et son statut a une colonne
ainsi qu’un fichier distinct. Si aucun module `Cat` n’existe, elle retourne
`not_tested`, jamais un faux échec.

Pour `Lav`, commencer par `light` avec 60 secondes. Si cette opération réussit,
le problème de durée concerne la compilation plus large, pas nécessairement
la catégorie de base. Pour l’analyse des 15 capacités génération pratique, seuls les
tests `practical` avec résultats golden vérifiés sont probants.

Les compilations sont lancées sans fenêtre CMD visible sous Windows ;
le journal des délais conserve la limite choisie et le module concerné.
