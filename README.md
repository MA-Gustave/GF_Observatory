# GF Observatory — dépôt mis à jour (diagnostic pratique)

**Écosystème :** l'orchestrateur multi-langues prévu s'appelle désormais
**Ars Magna Defluens** (anciennement Ars Magna Lulli). Observatory demeure
le visualiseur des preuves GF / WordBench : ce renommage n'ajoute pas un
service d'orchestration qui n'existe pas encore.

[Contrat de nom et de responsabilités](docs/ARS_MAGNA_DEFLUENS.md).

Version du paquet : **0.4.2 — nom Ars Magna Defluens et compatibilité** — novembre 2026.

Interface moderne v0.4.1 conservée, sans changement du moteur WordBench.

Ce dépôt contient **tous les fichiers du snapshot Observatory reçu**, plus un
premier parcours de diagnostic utilisable immédiatement, sans modifier les
grammaires GF ni lancer de compilation massive.

> **Portée réelle** : l'application historique Observatory décrite dans
> `GF_Observatory_Documentation_GitHub_Pages/` était marquée *Not implemented*
> dans l'instantané fourni. Cet ajout rend fonctionnels l'**inventaire RGL**,
> l'**import des preuves WordBench** et le **catalogue pratique avec interface**.
> Il ne prétend pas implémenter la totalité du runtime canonique, SQLite, l'API
> `/api/v1` ou la publication GitHub Pages définis dans la documentation.

## Démarrage Windows (PowerShell 7 ou double-clic)

**Pré-requis :** Windows avec Python **3.10 ou plus récent**, y compris Tkinter
(fourni par l'installation standard de Python). Aucun `pip install` requis.

1. Extraire le ZIP dans `C:\mycode\Grammatical-Framework` : le ZIP contient déjà le dossier `GF_Observatory`.
2. Double-cliquer **`GF_Observatory_Diagnostic.pyw`** pour démarrer **sans fenêtre CMD**. Le lanceur historique `Launch_Observatory.bat` peut provoquer un bref flash de console Windows : ne pas l’utiliser si l’on souhaite zéro fenêtre noire.
3. Les chemins courants sont détectés automatiquement. Pour les vérifier ou
   les modifier, ouvrir **Paramètres** (repliés par défaut) et indiquer au besoin
   la racine RGL (`...\gf-rgl`), WordBench et `gf.exe`.
4. Cliquer **Actualiser les langues** pour établir l’inventaire sans lancer GF.
5. Choisir les langues, le mode `light` ou `quick`, puis **Tester sélection**.
   Les journaux historiques restent accessibles dans **Journaux de lot** sans recompilation.

L’interface `.pyw` est intégrée au dépôt. Elle nécessite le dossier voisin
`tools/` et doit être lancée depuis le dépôt complet. Le profil et les
fonctions d’inventaire sont fournis dans le dépôt.

### Produits du diagnostic

Dans le dossier de sortie :

- `diagnostic.json` — outils détectés, dossiers et présence des dépôts ;
- `rgl_inventory.json` — modules GF par code de langue et écarts structurels ;
- `practical_catalog.json` — aptitude pratique et statut des preuves ;
- `practical_catalog.csv` — tableau de synthèse Excel-compatible ;
- `practical_generation_profile.json` — profil utilisé pour la décision ;
- `LISEZ_MOI.txt` — chiffres clés et avertissements.

**À partager pour une analyse distante :** `diagnostic.json`,
`rgl_inventory.json` et, si pertinent, `practical_catalog.json`.
Les JSON incluent des chemins absolus locaux : relire avant partage.

## Classification correcte des langues

Chaque code peut être `ready`, `needs_work` ou `unverified` :

- **ready** : les capacités essentielles ont été validées par des scénarios
  WordBench et les preuves ont passé les contrôles du consommateur Observatory ;
- **needs_work** : au moins une fonction exigée possède des preuves d'échec ;
- **unverified** : preuves WordBench absentes, incomplètes, incompatibles ou
  non vérifiables. **Ce n'est pas une preuve de déficience linguistique.**

Le profil cible `encyclopedic` et `procedural` avec **15 capacités obligatoires
et 5 facultatives**. Les fonctions couvrent des **intentions sémantiques**, pas
la totalité des temps rares. Une reformulation idiomatique peut satisfaire le
même scénario, selon la langue.

Les fichiers de source nommés comme `GrammarEng.gf`, `SyntaxEng.gf` ou `ResSqi.gf`
permettent de découvrir les **candidats structurels**, y compris incomplets.
La présence d'un module ne prouve *jamais* qu'une fonction génération pratique fonctionne.
Un `structural_gap` n'est **pas** automatiquement un manque pratique.

**L’inventaire ne compile pas GF** ; les boutons de validation WordBench
lancent explicitement les compilations sélectionnées. Observatory ne confond
pas le catalogue pratique avec les niveaux généraux de maturité R0 à R7.

## Adapter les identités de langues

Les modules RGL sont identifiés par des suffixes : `Eng`, `Fra`, `Sqi`, etc.
Les identifiants de projet WordBench peuvent être `english`, `french`, etc.
Fournir une correspondance JSON facultative, sans déduction automatique :

```json
{"Eng": "english", "Fra": "french", "Sqi": "albanian"}
```

WordBench doit produire, **pour chaque langue testée**, un fichier
`practical_coverage.json` dans le même répertoire que ses `summary.json` et
`manifest.json`. Sans preuves d'exécution, la langue demeure `unverified`.

## Exécution CLI sans GUI

Depuis la racine du dépôt :

```powershell
py -3 tools\rgl_inventory.py --rgl-root 'C:\chemin\gf\lib' --output .\rgl_inventory.json
py -3 tools\practical_catalog.py --inventory .\rgl_inventory.json `
  --practical-profile .\profiles\practical_generation_v1.json `
  --reports-root 'C:\chemin\wordbench_runs' `
  --output .\practical_catalog.json --csv .\practical_catalog.csv
```

La CLI est un **prototype autonome** de lecture/agrégation (les chemins de
sortie ci-dessus sont simplement illustratifs ; éviter de versionner les
rapports de diagnostic). Les rapports WordBench sont optionnels dans l'UI.

## Tests

```powershell
py -3 -m pip install pytest
py -3 -m pytest -q tests
```

Le programme lui-même ne dépend que de la bibliothèque standard. Une suite de
tests en mémoire avec modules GF fictifs vérifie la découverte de `Sqi`, les
résultats `unverified`, la certification sur preuve et le rejet d'un artefact
WordBench altéré. Ces tests ne remplacent **pas** une exécution réelle avec le
compilateur GF et une RGL installée.

## Fichiers importants

```text
GF_Observatory_Diagnostic.pyw                Interface autonome
Launch_Observatory.bat                      Lanceur Windows
tools/rgl_inventory.py                      Inventaire structurel en CLI
tools/practical_catalog.py                 Agrégation de preuves en CLI
profiles/practical_generation_v1.json       Profil fonctionnel versionné
tests/                                      Tests ciblés
GF_Observatory_Documentation_GitHub_Pages/  Documentation d'origine conservée
```

Le contenu et les contrats documentaires d'origine sont conservés ; la portée
exacte de cette livraison est décrite dans `docs/IMPLEMENTATION_2026_11.md`.

## Nouveauté — WordBench ciblé depuis l'interface

Le fichier `GF_Observatory_Diagnostic.pyw` permet désormais de lancer WordBench sur une ou plusieurs langues en mode **quick** (compilation d'un module public), ou en mode **practical** quand les profils et scénarios d'essai existent. Les résultats sont distincts de la complétude génération pratique ; un `quick` réussi ne rend pas la langue `ready`.

Voir [Validation ciblée WordBench](docs/VALIDATION_CIBLEE_WORDBENCH.md) pour les instructions, restrictions et prérequis.

### Utilisation recommandée dans le GUI

Après un scan, sélectionne **Eng** et/ou **Fre**, choisis `quick`, puis
**Tester sélection**. Le bouton **Tester toutes** demande une confirmation,
exécute une langue à la fois, et **Arrêter après cette langue** interrompt
le lot entre deux tests. Les colonnes « WB rapide » et « Usage pratique »
sont séparées. Le mode `practical` nécessite l'extension WordBench et des
scénarios de langue avec leurs références gold : il ne les invente pas.

Les résultats WordBench produits par le GUI sont importés automatiquement
du dossier `wb_artifacts` vers le catalogue quand ils contiennent des preuves
compatibles et vérifiées. Les tests `quick` ne constituent jamais ces preuves.

### Correctif WordBench — détection du dépôt (0.3.2)

Le bouton **Détecter WordBench** reconnaît la structure habituelle et le cas
`GF_Wordbench/GF_Wordbench/src/gf_wordbench/__init__.py` après extraction d'une
archive. Les boutons de validation vérifient le chemin avant de démarrer et
signalent clairement les prérequis manquants. Voir
[la documentation ciblée](docs/VALIDATION_CIBLEE_WORDBENCH.md#correctif-032--wordbench-non-trouvé-malgré-son-installation).


### Correctif 0.3.3 — diagnostic des erreurs de validation

- Bouton **Détecter WordBench** visible dans la première rangée d'actions, même sur une fenêtre étroite.
- La validation s'exécute en arrière-plan sans lire les variables Tk depuis le thread de travail.
- En cas d'exception, ouvrir l'onglet **Diagnostic / explications** et consulter `observatory_last_error.log` dans le dossier de sortie.
- En cas d'échec de compilation WordBench (exit code différent de zéro), le balayage continue et la colonne **WB rapide** indique `error`. Choisir une langue et cliquer sur **Voir journal WB** pour afficher sa sortie.
- Une erreur du moteur WordBench n'est **jamais** automatiquement interprétée comme une capacité grammaticale manquante ; l'état pratique reste `unverified` jusqu'à obtention de preuves de scénarios validés.
- Le code `wordbench_runconfig_unresolved` signale notamment le message du WordBench fourni : `The validation application requires a resolved RunConfig`. Cette situation exige une correction ou une configuration dans WordBench ; Observatory ne la masque pas.
- Les sources RGL et WordBench ne sont jamais modifiées par ce correctif.

**Limites :** test sur une installation GF réelle à effectuer sur Windows. Le mode `quick` ne valide pas les 15 fonctions sémantiques ; le mode `practical` exige les scénarios/golds WordBench correspondants.


### Correctif v0.3.4 (2 novembre 2026)

L'interface `.pyw` intégrée dans ce dépôt lance maintenant le **composant de
compilation GF de WordBench** par `tools/wordbench_quick_probe.py`, sans
utiliser le point d'entrée WordBench `validate --mode quick` qui présente
une incompatibilité `RunConfig` dans le snapshot fourni. Le journal d'une langue
échouée est ouvert automatiquement et la sélection est conservée. Consulter
`docs/VALIDATION_CIBLEE_WORDBENCH.md` pour les détails et limites.

**Ne pas copier le `.pyw` seul** : installer le répertoire complet `GF_Observatory`
afin que le module voisin `tools/wordbench_quick_probe.py` soit disponible.


### Correctif v0.3.5 — détection du compilateur Grammatical Framework

Le message « Compilateur GF introuvable sur PATH » signifie que WordBench est
accessible, mais que l'exécutable `gf.exe` requis pour compiler les modules ne
l'est pas. **Les langues ne sont pas fautives**, et `gf-rgl` seul ne contient
pas nécessairement le compilateur.

- Champ **Compilateur GF (gf.exe)** dans l'interface, avec sélecteur de fichier.
- Bouton **Détecter GF** : cherche le compilateur sur le PATH, dans quelques
  emplacements habituels de Windows et, de façon bornée, dans les arbres de
  compilation `gf-core` du workspace.
- Avant de tester une ou plusieurs langues, Observatory vérifie le compilateur
  une seule fois ; si GF n'est pas disponible, le lot ne démarre pas.
- Le test rapide communique le chemin explicite à WordBench. La RGL est
  toujours seulement lue, et aucun binaire n'est installé automatiquement.

Si la détection ne trouve rien, ouvre PowerShell 7 et vérifie :

```powershell
Get-Command gf -ErrorAction SilentlyContinue
Get-ChildItem 'C:\mycode\Grammatical-Framework' -Filter gf.exe -Recurse -File -ErrorAction SilentlyContinue |
  Select-Object -First 10 -ExpandProperty FullName
```

Si `gf.exe` est trouvé, indique son chemin dans l'interface. Sinon, il faudra
installer ou compiler GF avant d'exécuter WordBench. Un résultat de compilation
`quick` n'est **pas** une preuve de couverture des 15 fonctions génération pratique.


## v0.3.6 — GF 3.12 par défaut et chemin des grammaires abstraites

Sur l'installation Windows vérifiée, Observatory préremplit automatiquement
`C:\mycode\Grammatical-Framework\gf-3.12-windows\gf.exe` **si le fichier
existe**. Sur les autres installations, la détection locale ou le `PATH` reste
disponible, et l'utilisateur peut toujours sélectionner un exécutable différent.

Le mode WordBench `quick` passe maintenant `gf-rgl/src/abstract` dans les chemins
de recherche du compilateur. Cela corrige l'erreur `File Grammar.gf does not exist`
lors de la compilation de `GrammarEng.gf`. Les sources RGL sont conservées
en lecture seule; les artefacts sont écrits dans le dossier de sortie.

Le test `quick` confirme uniquement une compilation ponctuelle; **il ne prouve
aucune des 15 capacités fonctionnelles génération pratique**. Une autre erreur de GF peut
se manifester selon la grammaire et la version des sources.


## Correctif 0.3.7 — exécution sans fenêtres CMD

Le mode interface graphique utilise `pythonw` via l’association `.pyw`. Les
processus Python de validation WordBench, `gf.exe` et `taskkill.exe` sont
lancés avec `CREATE_NO_WINDOW` sous Windows. Les sorties standard et erreurs
restent capturées dans les journaux WordBench et dans le panneau Diagnostic.
Les groupes de processus et délais existants sont conservés.

**Démarrer par `GF_Observatory_Diagnostic.pyw`, et non par le `.bat`** si tu veux
éviter le flash initial d’une fenêtre CMD. Cette politique n’affecte pas les
applications lancées séparément en dehors d’Observatory.


## v0.3.8 — Diagnostic des compilations RGL (2026-11-02)

Analyse des journaux de 67 langues du balayage fourni : 52 `ok`, 6 `timeout`,
9 `error`. Le code Windows `3221225786` (`0xC000013A`) signifie une interruption
du processus; ce n'est pas une preuve d'un défaut grammatical catalan.

- La commande `quick` inclut désormais le répertoire partagé `src/bantu`
  (notamment pour Gus, Kam, Swa), et, seulement lorsque pertinent,
  `src/english` (Sco) et `src/zulu/abstract_ext` (Zul).
- La sortie du compilateur est classée : interruption Windows, délai,
  dépendance absente, erreur interne GF, symbole API manquant et erreur de type.
- Le bouton **Retester échecs/délais** relance uniquement les validations `quick`
  dont le résultat est `error`, `timeout` ou `interrupted`. Les `ok` existants
  sont conservés dans `wordbench_quick_results.json`.
- Le champ **Délai/langue (s)** est réglable de 5 à 3600, défaut 180.
- Le compte rendu de lot (nouveaux tests) est distinct du catalogue
  historique fusionné.

Une réussite `quick` confirme seulement une compilation du module choisi ;
**elle ne certifie pas les 15 capacités fonctionnelles génération pratique**.
Les six délais dépassés peuvent être dus au coût de compilation, à la mémoire
ou à d'autres facteurs : il faut les retester individuellement. La cause de
l'interruption catalane ne peut pas être déduite du seul code Windows.

## v0.3.9 — Prévalidation légère des langues lentes

Le mode `light` de l’interface `.pyw` compile uniquement le module `CatXXX.gf`
quand il existe. Il est proposé initialement avec un délai de 60 s, pour éviter
de refaire sans raison une compilation complète `GrammarXXX.gf` qui a déjà
dépassé 300 s (`Lav`). Les sorties sont isolées dans
`wordbench_light_results.json` et `wordbench_logs/XXX_light.log`.
Ce signal ne remplace ni le `quick` complet ni les tests `practical` de
couverture génération pratique. La liste des résultats `quick` existants est préservée.

## v0.4.0 — Consulter tous les journaux de lot dans l'interface

Dans `GF_Observatory_Diagnostic.pyw`, le bouton **Journaux du lot** et l'onglet **Journaux de lot** permettent de consulter tous les résultats `light` et `quick` enregistrés dans le dossier de sortie, même après fermeture de l'application. L'onglet propose des filtres (réussites, erreurs/délais, non applicables), une consultation immédiate du journal sélectionné et un bouton **Exporter tous les journaux** qui produit `wordbench_batch_all_logs.txt`.

Le cas `Kal` (groenlandais) n'est plus classé comme échec lorsque le module `CatKal.gf` n'existe pas : le test strictement `Cat` est **non applicable**. Un ancien résultat `quick: ok` reste affiché séparément. Les anciens fichiers v0.3.9 sont pris en charge sans recompilation ni modification. Voir `docs/INTERFACE_JOURNAUX_LOT_v040.md`.

## Nouvelle interface — v0.4.1

L'écran principal privilégie les **langues, résultats, actions de validation et
preuves**, avec une présentation moderne selon la palette Mécanismes Abstraits.
Les neuf chemins techniques sont disponibles dans **Paramètres** (repliés).
La vue **Journaux de lot** centralise résultats, aperçu et export en un clic.
Les réglages sont sauvegardés localement lors de la fermeture normale.

Voir [Refonte d’interface v0.4.1](docs/REFONTE_INTERFACE_v0.4.1.md).
