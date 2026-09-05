"""Fake CorpusAdapter for the search tests that need a vector-AVAILABLE state
(task B5 deliverable 5). The fixture index carries no vector set
(docs/rounds/R01_probe.report.md), so `search_hybrid` / `search_graph`
against it are degraded by construction; this fake covers the state the
fixture cannot produce, matching the pattern in tests/diagnostics/fake_adapter.py
(not imported from there -- this module never touches a real database, the
real corpus, or RHACO_corpus_index).
"""
from __future__ import annotations

from explorer.models import (
    COMPONENT_RANK_NOT_EXPOSED,
    CardRow,
    Evidence,
    ModeResult,
    ResultItem,
    VectorAvailability,
)


def make_vector_available() -> VectorAvailability:
    return VectorAvailability(available=True, reason="ok", model_tag="nomic-embed-text", probe_ms=3.2, detail="")


def _card(doc_id: str, doc_type: str, seq: str, title: str, status: str = "Active") -> CardRow:
    slug = title.replace(" ", "_")
    card_ref = f"reports/{doc_id}_{slug}.card.yaml"
    doc_ref = f"reports/{doc_id}_{slug}.md"
    return CardRow(
        yaml_path=f"C:\\fake\\{card_ref}",
        doc_id=doc_id,
        doc_type=doc_type,
        date="2026-09-01",
        seq=seq,
        title=title,
        status=status,
        card_ref=card_ref,
        doc_ref=doc_ref,
    )


_ITEMS = [
    ResultItem(
        rank=1,
        doc_id="RHACO-ANL-20260901-101",
        cards=[_card("RHACO-ANL-20260901-101", "ANL", "101", "Fake Analysis One")],
        evidence=Evidence(
            retrieval_mode="hybrid",
            returned_rank=1,
            exact_identifier_match=False,
            degradation_status="none",
            component_rank=COMPONENT_RANK_NOT_EXPOSED,
        ),
    ),
    ResultItem(
        rank=2,
        doc_id="RHACO-HND-20260901-102",
        cards=[_card("RHACO-HND-20260901-102", "HND", "102", "Fake Handoff Two")],
        evidence=Evidence(
            retrieval_mode="hybrid",
            returned_rank=2,
            exact_identifier_match=False,
            degradation_status="none",
            component_rank=COMPONENT_RANK_NOT_EXPOSED,
        ),
    ),
    ResultItem(
        rank=3,
        doc_id="RHACO-CMP-20260901-103",
        cards=[_card("RHACO-CMP-20260901-103", "CMP", "103", "Fake Campaign Three")],
        evidence=Evidence(
            retrieval_mode="hybrid",
            returned_rank=3,
            exact_identifier_match=False,
            degradation_status="none",
            component_rank=COMPONENT_RANK_NOT_EXPOSED,
        ),
    ),
    ResultItem(
        rank=4,
        doc_id="RHACO-EVT-20260901-104",
        cards=[_card("RHACO-EVT-20260901-104", "EVT", "104", "Fake Event Four")],
        evidence=Evidence(
            retrieval_mode="hybrid",
            returned_rank=4,
            exact_identifier_match=False,
            degradation_status="none",
            component_rank=COMPONENT_RANK_NOT_EXPOSED,
        ),
    ),
]


class FakeAvailableAdapter:
    """Minimal stand-in exposing only the read-only surface
    explorer.search.service.run_search calls, with the vector channel
    reported available (mode badge "hybrid", no degradation notice)."""

    def __init__(self) -> None:
        self._vector = make_vector_available()

    def vector_availability(self) -> VectorAvailability:
        return self._vector

    def resolve_identifier(self, q: str) -> list[str]:
        return []

    def cards_for_doc_id(self, doc_id: str) -> list[CardRow]:
        return []

    def lexical_excerpt(self, q: str, doc_ref: str):
        return None

    def search_lexical(self, q: str, **kwargs) -> ModeResult:
        return ModeResult(
            query=q, mode_requested="lexical", mode_effective="lexical",
            items=[], truncated=False, total_matched=0, returned=0,
        )

    def search_hybrid(self, q: str, top_k: int = 10) -> ModeResult:
        items = [
            ResultItem(rank=it.rank, doc_id=it.doc_id, cards=it.cards, evidence=it.evidence, path=it.path)
            for it in _ITEMS[:top_k]
        ]
        return ModeResult(
            query=q, mode_requested="hybrid", mode_effective="hybrid",
            items=items, degradation_notice=None, returned=len(items), vector=self._vector,
        )

    def search_graph(self, q: str, top_k: int = 10) -> ModeResult:
        items = [
            ResultItem(
                rank=it.rank, doc_id=it.doc_id, cards=it.cards,
                evidence=Evidence(
                    retrieval_mode="graph",
                    returned_rank=it.evidence.returned_rank,
                    exact_identifier_match=False,
                    degradation_status="none",
                    component_rank=COMPONENT_RANK_NOT_EXPOSED,
                ),
                path=it.path,
            )
            for it in _ITEMS[:top_k]
        ]
        return ModeResult(
            query=q, mode_requested="graph", mode_effective="graph",
            items=items, degradation_notice=None, returned=len(items), vector=self._vector,
        )
