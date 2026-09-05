"""Catalog module (builder-owned: catalog). ARCHITECTURE.md section 4.2; PROMPT.md 5.1.

The home / browse surface: "What is in the RHACO corpus?" -- a filtered,
sorted, paginated list of card rows over the read-only catalog/facet queries
(D-Q2, D-Q5, D-Q6) exposed by explorer.corpus_adapter.CorpusAdapter. Never a
write path; filtering never fabricates a value not present in the index
(CONSTRAINTS.md O14).
"""
