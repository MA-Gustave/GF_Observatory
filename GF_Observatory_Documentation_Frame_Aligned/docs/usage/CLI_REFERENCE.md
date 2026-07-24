# GF Observatory — CLI Reference

| Champ | Valeur |
|---|---|
| Document role | Public CLI authority |
| Decision status | Accepted |
| Implementation status | Not implemented |
| Verification status | Documentation structurally validated; implementation tests pending |
| Owner | GF Observatory maintainers |
| Last reviewed | 2026-07-24 |

## Exécutable

```text
gf-observatory
```

## Registre

```text
gf-observatory workspace add <path> [--label <label>]
gf-observatory workspace list
gf-observatory workspace show <workspace-id>
gf-observatory workspace enable <workspace-id>
gf-observatory workspace disable <workspace-id>
gf-observatory workspace remove <workspace-id>
```

## Observation

```text
gf-observatory observe <workspace-id>
gf-observatory observe --all
gf-observatory observe <workspace-id> --run <run-id>
gf-observatory observe <workspace-id> --force
gf-observatory observe <workspace-id> --reingest
```

## Analyse et rapports

```text
gf-observatory matrix refresh [--workspace <id>]
gf-observatory report status [--workspace <id>]
gf-observatory report matrix [--workspace <id>]
gf-observatory report trends <workspace-id>
gf-observatory diagnostics list [--workspace <id>]
```

## Contrats

```text
gf-observatory schemas check <artifact-or-run-directory>
gf-observatory config check
gf-observatory contracts check --strict
gf-observatory tools list
gf-observatory tools run <tool-id> [allowed arguments]
```

## Service local

```text
gf-observatory api serve
```

## Formats communs

```text
--format table
--format json
--format markdown
```

La CLI appelle les mêmes cas d’utilisation que l’API et l’UI. Elle ne contient ni logique d’ingestion, ni scoring, ni exécution arbitraire.
