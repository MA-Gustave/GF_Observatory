# GF Observatory — Component Map

| Champ | Valeur |
|---|---|
| Document role | Component ownership authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

| Composant | Responsabilité principale |
|---|---|
| `RequestNormalizer` | Transformer les entrées CLI/API/UI en requêtes internes stables. |
| `ObservationPlanner` | Produire le plan canonique d’observation. |
| `ObservatoryOrchestrator` | Exécuter un plan sans dupliquer les scans. |
| `WorkspaceRegistry` | Posséder les identités et emplacements autorisés. |
| `ArtifactLocator` | Trouver les bundles candidats sans les interpréter. |
| `ArtifactReaderRegistry` | Sélectionner un lecteur par schéma et version. |
| `ManifestVerifier` | Vérifier chemins, tailles, hachages et rôles. |
| `EvidenceResolver` | Normaliser les preuves en `EvidenceBinding`. |
| `ObservationBuilder` | Construire une observation immuable. |
| `ObservationStore` | Persister registre, observations et cache local. |
| `AnalysisPlanner` | Lier observation, profil et analyseurs. |
| `EvidenceMatrixAssembler` | Exécuter une fois chaque scanner de zone et synthétiser la matrice. |
| `ProjectHealthEvaluator` | Calculer la santé selon des règles versionnées. |
| `DiagnosticEngine` | Produire des findings traçables. |
| `TrendAnalyzer` | Comparer des observations compatibles. |
| `ResponseMapper` | Transformer les résultats internes en contrats publics. |
| `ToolRegistry` | Exposer uniquement les cas d’utilisation allowlistés. |

## Règles de responsabilité

- Le normaliseur ne lit pas le filesystem.
- Le planner ne produit pas de rapport.
- Les lecteurs ne décident pas la santé.
- Les scanners sont sans effet de bord par défaut.
- L’orchestrateur appelle chaque scanner une fois par zone et cycle.
- Les rapports ne relisent jamais implicitement les workspaces.
- L’API et l’UI ne contiennent aucune règle de scoring.
