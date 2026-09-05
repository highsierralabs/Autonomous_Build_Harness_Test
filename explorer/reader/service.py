"""Reader view assembly (builder-owned: reader). ARCHITECTURE.md 4.4; PROMPT.md 5.4;
CONSTRAINTS.md S1/S4/S8/O7/O8/O13/O15/O19/O22/O23/O28.

`build_view(adapter, settings, card_ref, line)` is the reader's one entry point.
It never opens a database connection itself and never imports RHACO_corpus_index
or RHACO_tool_catalog_librarian -- it reads the adapter's already-defined
surface only (ARCHITECTURE.md 4.1: card, cards_for_doc_id, edges_for,
supersession_chain, read_document, read_card_text).

The view keeps three things distinct and never blends them (S1):
  (a) the CARD FILE -- the record: raw `.card.yaml` text plus its parsed form
      (every parsed key is preserved for display, never dropped, via the full
      `card_parsed` dump the template renders as JSON);
  (b) the INDEX ROW -- "as indexed": the adapter's CardRow, plus a per-field
      comparison against the card file so a stale index row is visible
      instead of silently displayed (`index_mismatch_fields`);
  (c) the DOCUMENT -- the canonical file on disk, rendered verbatim (no
      summarising, no truncation) with heading anchors independently
      re-verified against the source lines (O23), never trusted from the
      adapter or the markdown renderer's own token map.
"""
from __future__ import annotations

import datetime as dt
import re
from dataclasses import dataclass, field
from typing import Any

import yaml
from markdown_it import MarkdownIt

from explorer.config import Settings
from explorer.corpus_adapter.adapter import ConfigurationError
from explorer.corpus_adapter.paths import both_spellings
from explorer.models import FROZEN_STATUSES, CardRow, Heading

# CONSTRAINTS.md O23 / task B6 item 1: independently re-verify every heading
# anchor against the source line it claims, using the same ATX shape the
# adapter's own `_headings()` parses (never trust the line number blindly --
# this is exactly what catches the `broken_jump` fixture fault).
_ATX_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")

# task B6 item 1: markdown-it-py, CommonMark base, raw HTML escaped (html=False
# needs no sanitizer), tables + strikethrough enabled (ARCHITECTURE.md A1).
_MD = MarkdownIt("commonmark", {"html": False})
_MD.enable(["table", "strikethrough"])

# task B6 item 1(b): the fields compared between the index row and the card file.
INDEX_COMPARISON_FIELDS = ("title", "status", "lifecycle_state", "date", "doc_type")

# task B11 item 1: the native types `yaml.safe_load` resolves an UNQUOTED
# ISO-shaped scalar to (e.g. `date: 2026-06-24`, no quotes) -- 60.2% of the
# live corpus's `.card.yaml` files carry at least one (docs/rounds/
# R05_reader.report.md, blast-radius grep). None of these is JSON-serializable
# by `json.dumps`'s default encoder, which is exactly what crashed both
# `{{ view.card_parsed | tojson }}` (HTML) and `dataclasses.asdict(view)`
# (`/api/doc`, Starlette's `JSONResponse` calls `json.dumps` directly, no
# `default=` handler) with `TypeError: Object of type date is not JSON
# serializable` on the production card named in this round's dispatch.
_TEMPORAL_TYPES = (dt.datetime, dt.date, dt.time)
_JSON_NATIVE_LEAF_TYPES = (str, int, float, bool, type(None))


# --------------------------------------------------------------------------
# View dataclasses (reader-owned; not shared -- explorer/models.py is the
# integrator's shared shapes, ARCHITECTURE.md section 3).
# --------------------------------------------------------------------------


@dataclass
class HeadingView:
    level: int
    text: str
    slug: str
    line_no: int
    line_verified: bool


@dataclass
class LineView:
    number: int
    text: str
    is_hit: bool = False


@dataclass
class RefLink:
    """One depends_on / see_also entry from the card FILE (item 2), resolved
    against the index (`adapter.cards_for_doc_id`) when possible."""

    id: str
    note: str | None
    resolved: bool
    cards: list[CardRow] = field(default_factory=list)


@dataclass
class EdgeLink:
    """One index-derived (`adapter.edges_for`) lineage relation, rendered with
    its Edge.direction_label (O8) and the related card row(s)."""

    relation: str
    direction_label: str
    doc_id: str
    direction: str  # "outgoing" | "incoming"
    note: str | None = None
    resolved: bool = True
    cards: list[CardRow] = field(default_factory=list)


@dataclass
class SupersededBanner:
    head: CardRow


@dataclass
class DocumentView:
    kind: str | None
    sha256: str | None
    size_bytes: int | None
    line_count: int
    rendered_html: str | None = None
    plain_text: str | None = None
    unsupported_binary: bool = False
    headings: list[HeadingView] = field(default_factory=list)
    anchor_mismatches: list[HeadingView] = field(default_factory=list)
    lines: list[LineView] = field(default_factory=list)
    body_missing: bool = False
    body_missing_message: str | None = None


@dataclass
class CardPanelView:
    """Card panel content (task B6 item 2). Identity/status/tag-shaped fields
    come from the CARD FILE (S1: the file is the record); `doc_id` is the one
    field that only the index carries (O7) and is labelled accordingly by the
    template."""

    doc_id: str
    doc_type: str | None
    date: str | None
    seq: str | None
    title: str | None
    status: str | None
    frozen: bool
    lifecycle_label: str | None
    lifecycle_value: str | None
    programs: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    project_knowledge: str | None = None
    schema_version: Any = None
    naming_convention_version: str | None = None
    last_human_review: str | None = None
    reviewer: str | None = None
    abstract: str | None = None
    depends_on: list[RefLink] = field(default_factory=list)
    see_also: list[RefLink] = field(default_factory=list)
    superseded_banner: SupersededBanner | None = None
    supersedes_text: list[EdgeLink] = field(default_factory=list)
    amendment_of: list[CardRow] = field(default_factory=list)
    amended_by: list[CardRow] = field(default_factory=list)
    campaign_child_of: list[EdgeLink] = field(default_factory=list)
    lineage_links: list[EdgeLink] = field(default_factory=list)
    unresolved_edges: list[EdgeLink] = field(default_factory=list)
    local_path: str | None = None
    raw_text: str = ""


@dataclass
class ReaderView:
    card_ref: str
    doc_id: str
    card_row: CardRow
    card_parsed: dict
    card_parse_error: str | None
    index_mismatch_fields: list[str]
    card_panel: CardPanelView
    document: DocumentView
    jump_requested: int | None
    jump_found: bool
    jump_message: str | None
    jump_line_attr: str
    lineage_href: str


# --------------------------------------------------------------------------
# build_view
# --------------------------------------------------------------------------


def build_view(adapter: Any, settings: Settings, card_ref: str, line: int | None) -> ReaderView | None:
    """Assemble the reader view, or None when `adapter.card(card_ref)` finds
    nothing (unknown or out-of-root card_ref -- routes.py turns None into a
    404)."""
    card = adapter.card(card_ref)
    if card is None:
        return None

    raw_text = adapter.read_card_text(card)
    parsed, parse_error = _parse_card_yaml(raw_text)
    identity = parsed.get("identity") if isinstance(parsed.get("identity"), dict) else {}

    mismatch_fields = _index_mismatch(card, identity)
    document = _build_document_view(adapter, card)

    jump_requested = line
    jump_found = False
    jump_message: str | None = None
    jump_line_attr = ""
    if line is not None:
        if 1 <= line <= document.line_count:
            jump_found = True
            jump_message = f"jumped to line {line}"
            jump_line_attr = str(line)
            for lv in document.lines:
                if lv.number == line:
                    lv.is_hit = True
        else:
            jump_message = f"line {line} not found (document has {document.line_count} lines)"

    card_panel = _build_card_panel(adapter, card, parsed, identity, raw_text)

    return ReaderView(
        card_ref=card.card_ref,
        doc_id=card.doc_id,
        card_row=card,
        card_parsed=parsed,
        card_parse_error=parse_error,
        index_mismatch_fields=mismatch_fields,
        card_panel=card_panel,
        document=document,
        jump_requested=jump_requested,
        jump_found=jump_found,
        jump_message=jump_message,
        jump_line_attr=jump_line_attr,
        lineage_href=f"/lineage/{card.card_ref}",
    )


# --------------------------------------------------------------------------
# card file parsing / index comparison
# --------------------------------------------------------------------------


def _json_safe(value: Any) -> Any:
    """Recursively convert a value `yaml.safe_load` produced into a structure
    `json.dumps` can always serialize (task B11 item 1). Applied once, here,
    right after `yaml.safe_load` -- before `identity`, `card_parsed`, or any
    `CardPanelView` field derived from `parsed` is built -- so BOTH surfaces
    (the HTML page's `card_parsed | tojson` and the `/api/doc` twin's
    `dataclasses.asdict(view)`, which Starlette serializes with plain
    `json.dumps`, no `default=` handler) see the identical, already-safe
    value, and `_index_mismatch` never receives a native temporal object on
    one side of a comparison whose other side is always a string (item 2).

    `datetime.date` / `datetime.datetime` / `datetime.time` (the native types
    an UNQUOTED ISO-shaped YAML scalar resolves to) become their own
    `.isoformat()` text -- fidelity-preserving, since the card's own unquoted
    scalar was itself ISO-shaped to begin with, so the ISO string is the same
    characters the file already had, just without the type PyYAML attached to
    them; nothing is reformatted, localised, or re-zoned. Dicts and lists (and
    tuples, though `yaml.safe_load` never emits one) recurse. Every other
    non-JSON-native leaf `yaml.safe_load` can produce (`bytes` from a
    `!!binary` scalar, `set` from `!!set`, ...) is rendered via `str()` rather
    than left to crash `json.dumps` downstream -- a reader page must never 500
    because of a card's contents (S1)."""
    if isinstance(value, dict):
        return {k: _json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(v) for v in value]
    if isinstance(value, _TEMPORAL_TYPES):
        return value.isoformat()
    if isinstance(value, _JSON_NATIVE_LEAF_TYPES):
        return value
    return str(value)


def _parse_card_yaml(raw_text: str) -> tuple[dict, str | None]:
    try:
        data = yaml.safe_load(raw_text)
    except yaml.YAMLError as exc:
        return {}, f"{type(exc).__name__}: {exc}"
    if not isinstance(data, dict):
        return {}, "card file did not parse to a mapping"
    return _json_safe(data), None


def _norm(value: Any) -> str | None:
    if value is None:
        return None
    return str(value).strip()


def _index_mismatch(card: CardRow, identity: dict) -> list[str]:
    """task B6 item 1(b): per-field comparison of the index row against the
    card file; a field the file does not carry compares as None on both sides
    (a missing key is not, by itself, a mismatch)."""
    mismatches = []
    for name in INDEX_COMPARISON_FIELDS:
        index_value = getattr(card, name)
        file_value = identity.get(name)
        if _norm(index_value) != _norm(file_value):
            mismatches.append(name)
    return mismatches


# --------------------------------------------------------------------------
# document rendering
# --------------------------------------------------------------------------


def _verify_heading_line(lines: list[str], heading: Heading) -> bool:
    """O23: does `lines[heading.line_no - 1]` actually begin the heading's
    text? Re-derived independently from the adapter's own claim -- this is
    what makes the `broken_jump` fault (line numbers off by 50) visible
    instead of a silent wrong landing."""
    idx = heading.line_no - 1
    if idx < 0 or idx >= len(lines):
        return False
    m = _ATX_RE.match(lines[idx])
    if not m:
        return False
    text = m.group(2).rstrip("#").strip()
    return text == heading.text


def _heading_views(doc) -> tuple[list[HeadingView], list[HeadingView]]:
    views: list[HeadingView] = []
    mismatches: list[HeadingView] = []
    for h in doc.headings:
        verified = _verify_heading_line(doc.lines, h)
        hv = HeadingView(level=h.level, text=h.text, slug=h.slug, line_no=h.line_no, line_verified=verified)
        views.append(hv)
        if not verified:
            mismatches.append(hv)
    return views, mismatches


def _render_markdown(doc) -> str:
    """task B6 item 1: render the markdown body, injecting id/data-line (and
    data-line-verified="false" where O23's re-check fails) onto the rendered
    heading tokens -- matched to `doc.headings` by order, the adapter's own
    backend-provided jump targets, never re-derived from the renderer's token
    map (see the module docstring and this round's report, "Material
    alternatives")."""
    tokens = _MD.parse(doc.text)
    heading_token_indices = [i for i, t in enumerate(tokens) if t.type == "heading_open"]
    for idx, heading in zip(heading_token_indices, doc.headings, strict=False):
        token = tokens[idx]
        token.attrSet("id", heading.slug)
        token.attrSet("data-line", str(heading.line_no))
        if not _verify_heading_line(doc.lines, heading):
            token.attrSet("data-line-verified", "false")
    return _MD.renderer.render(tokens, _MD.options, {})


def _build_document_view(adapter: Any, card: CardRow) -> DocumentView:
    try:
        doc = adapter.read_document(card)
    except ConfigurationError as exc:
        return DocumentView(
            kind=None, sha256=None, size_bytes=None, line_count=0,
            body_missing=True, body_missing_message=str(exc),
        )
    except OSError as exc:
        path = card.doc_path or "(no document path on the card)"
        return DocumentView(
            kind=None, sha256=None, size_bytes=None, line_count=0,
            body_missing=True,
            body_missing_message=f"document not found on disk at {path!r}: {exc}",
        )

    headings, anchor_mismatches = _heading_views(doc)
    lines = [LineView(number=i, text=t) for i, t in enumerate(doc.lines, start=1)]

    rendered_html: str | None = None
    plain_text: str | None = None
    if doc.kind == "markdown":
        rendered_html = _render_markdown(doc)
    elif doc.kind == "text":
        plain_text = doc.text

    return DocumentView(
        kind=doc.kind,
        sha256=doc.sha256,
        size_bytes=doc.size_bytes,
        line_count=len(doc.lines),
        rendered_html=rendered_html,
        plain_text=plain_text,
        unsupported_binary=(doc.kind == "binary"),
        headings=headings,
        anchor_mismatches=anchor_mismatches,
        lines=lines,
    )


# --------------------------------------------------------------------------
# card panel
# --------------------------------------------------------------------------


def _build_ref_links(adapter: Any, entries: Any) -> list[RefLink]:
    links: list[RefLink] = []
    for entry in entries or []:
        if isinstance(entry, dict):
            ref_id = str(entry.get("id") or "")
            note = entry.get("note")
        else:
            ref_id = str(entry)
            note = None
        cards = adapter.cards_for_doc_id(ref_id) if ref_id else []
        links.append(RefLink(id=ref_id, note=note, resolved=bool(cards), cards=cards))
    return links


def _supersedes_narrative(edge_set) -> list[EdgeLink]:
    out: list[EdgeLink] = []
    for e in edge_set.outgoing:
        if e.relation == "supersedes":
            out.append(EdgeLink(
                relation="supersedes", direction_label="is superseded by", doc_id=e.to_id,
                direction="outgoing", note=e.note, cards=e.target_cards,
            ))
    for e in edge_set.incoming:
        if e.relation == "supersedes":
            out.append(EdgeLink(
                relation="supersedes", direction_label="supersedes", doc_id=e.from_id,
                direction="incoming", note=e.note, cards=e.source_cards,
            ))
    return out


def _campaign_child_of(edge_set) -> list[EdgeLink]:
    return [
        EdgeLink(
            relation="campaign_child", direction_label="campaign child of", doc_id=e.from_id,
            direction="incoming", note=e.note, cards=e.source_cards,
        )
        for e in edge_set.incoming if e.relation == "campaign_child"
    ]


def _lineage_links(edge_set) -> list[EdgeLink]:
    """Every resolved edge touching this card, typed and directional
    (Edge.direction_label, O8) -- the complete record, alongside (not instead
    of) the narrative sentences above."""
    links: list[EdgeLink] = []
    for e in edge_set.outgoing:
        links.append(EdgeLink(
            relation=e.relation, direction_label=e.direction_label, doc_id=e.to_id,
            direction="outgoing", note=e.note, cards=e.target_cards,
        ))
    for e in edge_set.incoming:
        links.append(EdgeLink(
            relation=e.relation, direction_label=e.direction_label, doc_id=e.from_id,
            direction="incoming", note=e.note, cards=e.source_cards,
        ))
    return links


def _unresolved_edges(edge_set) -> list[EdgeLink]:
    return [
        EdgeLink(
            relation=e.relation, direction_label=e.direction_label, doc_id=e.to_id,
            direction="outgoing", note=e.note, resolved=False,
        )
        for e in edge_set.unresolved
    ]


def _resolve_local_path(parsed: dict, card: CardRow) -> str:
    location = parsed.get("location")
    if isinstance(location, dict) and location.get("local_path"):
        return str(location["local_path"])
    junction, _physical = both_spellings(card.yaml_path)
    return junction


def _lifecycle_label(doc_type: str | None, lifecycle_value: str | None) -> str | None:
    """CONSTRAINTS.md S4: status and lifecycle_state are separate channels;
    lifecycle_state is meaningful only for CMP and is flagged informational
    otherwise -- never joined, substituted, or merged into one cell."""
    if not lifecycle_value:
        return None
    if (doc_type or "").upper() == "CMP":
        return "CMP lifecycle state"
    return "informational (non-CMP)"


def _build_card_panel(adapter: Any, card: CardRow, parsed: dict, identity: dict, raw_text: str) -> CardPanelView:
    status = identity.get("status") or card.status
    frozen = (status or "") in FROZEN_STATUSES
    doc_type = identity.get("doc_type") or card.doc_type
    lifecycle_value = identity.get("lifecycle_state") or card.lifecycle_state
    lifecycle_label = _lifecycle_label(doc_type, lifecycle_value)

    depends_on = _build_ref_links(adapter, parsed.get("depends_on"))
    see_also = _build_ref_links(adapter, parsed.get("see_also"))

    edge_set = adapter.edges_for(card)

    superseded_banner = None
    if status == "Superseded":
        chain = adapter.supersession_chain(card.doc_id)
        if chain and chain[-1].card_ref != card.card_ref:
            superseded_banner = SupersededBanner(head=chain[-1])

    amendment_of: list[CardRow] = []
    amended_by: list[CardRow] = []
    if card.doc_id:
        siblings = adapter.cards_for_doc_id(card.doc_id)
        if card.is_amendment:
            amendment_of = [c for c in siblings if not c.is_amendment and c.card_ref != card.card_ref]
        else:
            amended_by = [c for c in siblings if c.is_amendment and c.card_ref != card.card_ref]

    tags = list(parsed.get("tags") or card.tags or [])
    programs = list(identity.get("programs") or card.programs or [])

    return CardPanelView(
        doc_id=card.doc_id,
        doc_type=doc_type,
        date=identity.get("date") or card.date,
        seq=identity.get("seq") or card.seq,
        title=identity.get("title") or card.title,
        status=status,
        frozen=frozen,
        lifecycle_label=lifecycle_label,
        lifecycle_value=lifecycle_value,
        programs=programs,
        tags=tags,
        project_knowledge=identity.get("project_knowledge") or card.project_knowledge,
        schema_version=identity.get("schema_version", card.schema_version),
        naming_convention_version=identity.get("naming_convention_version") or card.naming_convention_version,
        last_human_review=identity.get("last_human_review") or card.last_human_review,
        reviewer=identity.get("reviewer") or card.reviewer,
        abstract=(parsed.get("abstract") or card.abstract or "").strip() or None,
        depends_on=depends_on,
        see_also=see_also,
        superseded_banner=superseded_banner,
        supersedes_text=_supersedes_narrative(edge_set),
        amendment_of=amendment_of,
        amended_by=amended_by,
        campaign_child_of=_campaign_child_of(edge_set),
        lineage_links=_lineage_links(edge_set),
        unresolved_edges=_unresolved_edges(edge_set),
        local_path=_resolve_local_path(parsed, card),
        raw_text=raw_text,
    )
