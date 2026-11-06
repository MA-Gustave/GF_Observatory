# Implémentation Observatory — 2026-11-02

## Étendue exacte

Ajout d'un **chemin pratique minimal** qui complète le snapshot documentaire
original, sans revendiquer le runtime canonique complet.

1. **Découverte structurelle** (`tools/rgl_inventory.py`) : lecture récursive
   de `.gf` sous `src` ou la racine choisie. Les modules auxiliaires (`ResSqi`,
   `CatSqi`, etc.) révèlent aussi les langues en développement. L'ensemble de
   quatre modules publics `Grammar`, `Syntax`, `Paradigms`, `Lang` est utilisé
   comme **indicateur structurel seulement**.
2. **Profil fonctionnel** (`profiles/practical_generation_v1.json`) : 20
   capacités sémantiques, dont 15 obligatoires, pour encyclopédie/procédures.
3. **Consommation WordBench** (`tools/practical_catalog.py`) : importe un
   rapport de couverture préexistant, vérifie le hachage du profil, le
   `summary.json`, les artefacts déclarés et les conclusions de scénarios.
   Une incohérence dégrade l'état à `unverified`. Aucune grammaire n'est exécutée.
4. **Interface Tkinter** (`GF_Observatory_Diagnostic.pyw`) : choix des chemins,
   opération en thread, aperçu par langue, export de JSON et CSV, diagnostic
   local. L'UI est autonome afin de fonctionner par double-clic Windows.

## Limites explicites

- Ce module ne fournit **pas** le noyau complet (ObservationPlanner,
  observations persistées, API `/api/v1`, serveur, SQLite, release R0-R7,
  publication Pages). La documentation du snapshot les considère encore
  comme non implémentés.
- La vérification du consommateur vérifie les affirmations enregistrées par
  WordBench et les fichiers du manifeste. Elle ne remplace **pas** la relecture
  linguistique de sorties Gold et ne lance pas GF elle-même.
- Les sorties échouées sont des **preuves de défaut dans le scénario testé**,
  pas la preuve universelle d'une impossibilité d'expression de la langue.
- Si un projet WordBench porte un autre identifiant que le suffixe RGL, une
  table d'identité **explicite** est nécessaire.
- Les langues qui n'ont **aucun fichier GF** dans l'arbre scanné ne peuvent pas
  être inventoriées. Scanner les vraies sources RGL, pas seulement le snapshot
  Observatory.
- L'inventaire statique peut inclure des modules spécifiques n'appartenant pas
  à une grammaire de production : les candidats exigent confirmation humaine.

## Contrats respectés

- Le snapshot de documentation et les décisions originales sont conservés.
- Pas de dépendance à l'implémentation privée WordBench.
- Consommation de fichiers publics uniquement ; aucun write-back vers RGL,
  WordBench ou les répertoires source.
- R0–R7 reste distinct du profil de génération pratique.
- Un fichier de code ou une convention de nommage ne certifie pas `ready`.
- Pas de processus externe lancé depuis l'UI de diagnostic.

## Prochaine phase de développement

Créer des fixtures GF de référence pour les scénarios indispensables,
les exécuter dans WordBench sur quelques langues, puis brancher le catalogue
sur la future persistance et publication officielles d'Observatory.
