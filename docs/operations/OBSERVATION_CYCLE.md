# GF Observatory — Observation Cycle

| Champ | Valeur |
|---|---|
| Document role | Observation-cycle authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Entrée normale unique

`ObservatoryOrchestrator` est la seule entrée normale pour un cycle complet. Les scanners et lecteurs individuels restent disponibles pour les tests et diagnostics, sans effet de bord par défaut.

## Cycle

1. normaliser la requête ;
2. construire le plan ;
3. vérifier le cache/fingerprint ;
4. localiser et lire les artefacts une fois ;
5. construire l’observation ;
6. exécuter chaque scanner de zone une fois ;
7. produire les analyses ;
8. persister résultats et fingerprint ;
9. rendre la réponse demandée.

## Cache

- cache hit : retour du résultat compatible existant ;
- `--touch-timestamp` : met à jour uniquement les métadonnées non probantes ;
- `--force` : recalcule les analyses ;
- `--reingest` : relit explicitement les artefacts ;
- changement de profil : invalide l’analyse, pas nécessairement l’ingestion.

## Continuation

L’échec d’un workspace ne bloque pas les autres. Le cycle global devient `PARTIAL`, et chaque sujet conserve son statut et ses diagnostics.
