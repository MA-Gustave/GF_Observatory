# GF Observatory v0.4.0 — Journaux de lot et absence de Cat

## But

Rendre les journaux de plusieurs dizaines de langues consultables depuis la même interface, sans rechercher manuellement `wordbench_logs/*.log` et sans retester les langues.

## Utilisation

1. Lancer `GF_Observatory_Diagnostic.pyw` (pas le lanceur `.bat` pour éviter la console).
2. Sélectionner le dossier de sortie utilisé lors des tests (par défaut : `%USERPROFILE%\GF_Observatory_Diagnostic`).
3. Cliquer sur **Journaux du lot**, ou ouvrir l'onglet **Journaux de lot** puis **Actualiser**.
4. Dans le tableau, choisir une langue et un mode (`light` ou `quick`) : son journal s'affiche en dessous. Filtrer par réussites, erreurs/délais, ou tests non applicables.
5. **Exporter tous les journaux** produit `wordbench_batch_all_logs.txt` dans le dossier de sortie. L'export comprend les résultats de toutes les langues des deux modes et une copie bornée de chaque journal disponible.

L'onglet charge `wordbench_light_results.json` et `wordbench_quick_results.json`, y compris les résultats enregistrés par les versions antérieures. Les lignes de chaque langue sont conservées même lorsque les tests ont eu lieu dans plusieurs lots.

Le rapport n'est **pas** une preuve de couverture génération pratique : il concerne des compilations de modules GF.

## Groenlandais `Kal`

La grammaire peut contenir des modules publics sans `CatKal.gf`. Le mode `light` étant strictement limité à `Cat`, aucune compilation n'a lieu pour cette langue. Observatory affiche donc :

- `light: not_applicable` (raison `light_cat_module_absent`), **pas un échec** ;
- `quick: ok` si la compilation `quick` déjà réalisée a réussi ;
- `practical: unverified` tant que les scénarios sémantiques de génération pratique n'ont pas été validés.

Les rapports `light` v0.3.9 où `Kal` portait `not_tested` sont réinterprétés à l'affichage comme `not_applicable` sans modification des anciens fichiers.

## Fichiers et sécurité

Le lecteur n'ouvre que des journaux situés sous le sous-dossier local `wordbench_logs` du dossier de sortie sélectionné. Il refuse les chemins sortants. La lecture graphique est limitée aux 120 derniers Ko ; l'export utilise jusqu'à 300 Ko par journal. Aucun module RGL, aucune donnée WordBench source et aucun ancien journal ne sont modifiés.

## Tests

Tests unitaires du classement `not_applicable`, de la conservation de `quick: ok`, de l'import des anciens rapports, de la restriction des chemins de journaux, de l'export complet et du chargement de l'interface.
