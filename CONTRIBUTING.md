# Contributing

Observe the canonical architectural constraints under `/docs`. No GF compilation or WordBench execution is allowed inside Observatory. Do not import private WordBench Python models, bypass schema checks, modify source workspaces, accept unreviewed candidates as golds, or publish externally from a local HTTP route.

Every contribution requires a versioned contract, explicit provenance, negative security tests, and no changes to the 14-language/15-intent baseline without an accepted policy decision. Run `python -m unittest discover -s tests -v`. Include complete real exported fixtures (appropriately redacted) when proposing a new external reader.
