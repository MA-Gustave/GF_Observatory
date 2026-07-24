# GF Observatory — Diagnostic Model

| Champ | Valeur |
|---|---|
| Document role | Diagnostic-model authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Finding canonique

```text
finding_id
rule_id
severity
finding_type
workspace_id
project_id
observation_id
subject_ref
evidence_refs
detected_at
analyzer_id
analyzer_version
message
suggested_action
```

## Sévérités

```text
INFO
WARNING
ERROR
BLOCKING
```

## Types cœur

- `EVIDENCE_STALE`
- `MANIFEST_INCONSISTENT`
- `HASH_MISMATCH`
- `SCHEMA_INCOMPATIBLE`
- `IDENTITY_COLLISION`
- `REQUIRED_ARTIFACT_MISSING`
- `SOURCE_UNREACHABLE`
- `CONTRADICTORY_STATUS`
- `BROKEN_EVIDENCE_REFERENCE`
- `ANALYSIS_PROFILE_MISMATCH`

## Règles

- un diagnostic référence les preuves ;
- un diagnostic ne remplace pas les sorties brutes ;
- mêmes entrées et versions produisent les mêmes findings ;
- les suggestions ne sont jamais exécutées automatiquement ;
- la suppression d’un finding exige un changement de preuve, de règle ou de version, jamais un filtrage silencieux.
