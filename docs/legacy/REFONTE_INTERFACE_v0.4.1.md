# GF Observatory v0.4.1 — refonte visuelle et ergonomique

La refonte concerne **la présentation et les parcours**, pas le moteur de validation.
Les guides fournis par l'utilisateur sont la référence :
`guide-architecture-interfaces-ia-v2` (UX-01 à UX-18) et
`Mecanismes_Abstraits_Brand_v1` (identité du framework grammatical).

## Parcours dominant

1. Ouvrir Observatory : les **journaux locaux existants** sont lus, sans GF ni test automatique.
2. Cliquer **Actualiser les langues** (inventaire des sources RGL sans compilation).
3. **Rechercher, trier, filtrer** les langues. Voir les statuts indépendants light / quick / génération pratique.
4. Choisir `light` / `quick` / `practical`, le délai puis **Tester sélection** ou **Tester toutes** (confirmation obligatoire pour le lot).
5. Suivre l'activité, consulter la langue et son journal dans **Journaux de lot**. Exporter l'ensemble en un clic.

## Architecture de l'interface

- **Langues** : espace principal. Résumé chiffré, parcours de test, liste et fiche de langue (panneaux redimensionnables).
- **Journaux de lot** : historique transversal avec filtres, consultation dans la fenêtre et export texte.
- **Diagnostic technique** : environnement, erreurs, détails destinés au débogage.
- **Paramètres** (repliés au démarrage) : workspace, GF, WordBench, RGL, profils et dossier de sortie.

L'ancien écran « Sources et sortie » à neuf lignes n'occupe plus la moitié supérieure du parcours normal. Les actions de test sont centralisées une seule fois, et l'accès au journal est contextuel, sans dupliquer la logique de lecture.

## Correspondance entre anciennes et nouvelles fonctions

| Fonction v0.4.0 | Emplacement v0.4.1 |
|---|---|
| Scanner les langues | Action principale « Actualiser les langues » |
| Sélecteur de mode WordBench et délai | Bande « Valider des langues » |
| Tester sélection / Tester toutes | Bande « Valider des langues » |
| Retester échecs/délais | Bande « Valider des langues », ligne secondaire |
| Arrêter après cette langue | Bande « Valider des langues » |
| Filtrer les langues | Recherche + filtre par statut dans « Langues » |
| Diagnostics d'une langue | Panneau redimensionnable sous la liste |
| Journal langue sélectionnée | « Voir le journal » dans le contexte de la langue |
| Dernier échec WB | Filtre « Échecs et délais » dans Journaux de lot |
| Journaux du lot | Section majeure « Journaux de lot » |
| Exporter tous les journaux | Journaux de lot → Exporter tous les journaux |
| Diagnostics / explications | « Diagnostic technique » |
| Détecter la RGL, WordBench, GF | « Paramètres » → boutons de détection |
| Voir les fichiers de sortie | « Paramètres » → Dossier de résultats |
| Neuf chemins de configuration | « Paramètres » repliables |

## Identité visuelle

Direction « modernisme artisanal explicatif » : papier ivoire `#F3EFE4`, encre
`#1B1C1A`, architecture bleu de Prusse `#24455B`, action vermillon
`#D95B38`, succès sauge `#91A18C`, seuil ocre `#C4A25A`.
Typographie d'interface Segoe UI (repli natif Windows) et Consolas pour les preuves GF.
Le texte est toujours explicite : **le code couleur seul ne signifie pas réussite ou échec**.
Aucune image décorative, police externe ni dépendance réseau n'a été ajoutée.

## Ce qui n'a PAS changé

- Les commandes WordBench et GF, le compilateur par défaut 3.12 et la suppression des fenêtres CMD.
- Le code métier d'inventaire RGL et la validation de preuves pratiques.
- Les `wordbench_light_results.json`, `wordbench_quick_results.json`, `.gfo`, journaux et formats d'export.
- La possibilité de retester seulement les échecs et de suspendre le lot après la langue courante.
- Les confirmations avant une validation multiple et les protections d'écriture hors des sources.

**Vérité des statuts** : `light` confirme la compilation du module choisi,
`quick` confirme la compilation plus étendue, et `practical` exige des scénarios
génération pratique et leurs preuves. Les 15 capacités ne sont **jamais** validées par
simple présence d'un module ou compilation.

## Ergonomie additionnelle

- Les chemins, le délai et le mode sont sauvegardés dans
  `%USERPROFILE%\\.gf_observatory_ui.json` (préférences locales seulement).
  Ce fichier ne contient **aucun résultat ni preuve**, et peut être supprimé pour
  restaurer les valeurs automatiques.
- Les anciens journaux s'affichent au démarrage **sans recompilation**.
- Recherche et tri par colonne, filtre « À examiner », détails et journaux
  accessibles sans quitter l'application.
- Les opérations longues se déroulent dans des threads existants ; les
  boutons concurrents sont désactivés pendant l'exécution.
- Fermer la fenêtre durant une opération ne tue pas silencieusement le
  diagnostic : il faut arrêter après la langue, puis fermer.

## Vérifications

- Suite `python -m pytest -q tests` : les tests des versions antérieures
  continuent à fonctionner, ainsi que les nouveaux tests de palette et de
  préférences.
- Instanciation sous Tk 8.6 avec Xvfb, sélection de langues, ouverture des
  paramètres et de Journaux de lot, captures d'écran de vérification.
- Non vérifié dans cet environnement : rendu Windows 11 exact, GF.exe et
  les performances d'un véritable lot de 67 langues.
