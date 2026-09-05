/* RHACO Corpus Explorer -- keyboard navigation (builder-owned: web, wave 3).
   Vanilla JS, no framework, no network call of any kind. Inert on a page
   that carries none of these hooks: every handler guards its DOM reads and
   no-ops when nothing matches (ARCHITECTURE.md 4.7).

   Keys:
     /              focus the search box (input[name="q"], round-0 seed)
     ?              toggle the #keyhelp panel every merged page renders
     j / ArrowDown  move the result-list selection down
     k / ArrowUp    move the result-list selection up
     Enter          open the selected row's first <a href>
     Escape         clear the selection

   "Rows" are exactly the elements carrying data-doc-id (ARCHITECTURE.md
   A19: catalog <tr>, search <li>, lineage nodes and trail rows once that
   module lands) -- this file does not know or care which module rendered
   them. None of these keys ever fires while the event target is a form
   field (input/textarea/select/contenteditable), so typing is never
   hijacked. */
(function () {
  "use strict";

  var SELECTED_CLASS = "kbd-selected";
  var selectedIndex = -1;
  var rows = [];

  function isFormField(el) {
    if (!el) { return false; }
    var tag = el.tagName;
    return tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT" || !!el.isContentEditable;
  }

  function searchBox() {
    return document.querySelector('input[name="q"]');
  }

  function statusRegion() {
    return document.getElementById("kbd-status");
  }

  function announce(text) {
    var el = statusRegion();
    if (el) { el.textContent = text; }
  }

  function refreshRows() {
    rows = Array.prototype.slice.call(document.querySelectorAll("[data-doc-id]"));
  }

  function clearHighlight() {
    for (var i = 0; i < rows.length; i += 1) {
      if (rows[i] && rows[i].classList) { rows[i].classList.remove(SELECTED_CLASS); }
    }
  }

  function selectIndex(i) {
    if (!rows.length) { return; }
    if (i < 0) { i = 0; }
    if (i > rows.length - 1) { i = rows.length - 1; }
    clearHighlight();
    selectedIndex = i;
    var row = rows[selectedIndex];
    if (!row) { return; }
    row.classList.add(SELECTED_CLASS);
    if (typeof row.scrollIntoView === "function") { row.scrollIntoView({ block: "nearest" }); }
    var label = row.getAttribute("data-doc-id") || "";
    announce("Selected " + label + " (" + (selectedIndex + 1) + " of " + rows.length + ")");
  }

  function moveSelection(delta) {
    if (!rows.length) { return; }
    var next = selectedIndex < 0 ? (delta > 0 ? 0 : rows.length - 1) : selectedIndex + delta;
    selectIndex(next);
  }

  function openSelected() {
    if (selectedIndex < 0 || selectedIndex >= rows.length) { return; }
    var row = rows[selectedIndex];
    if (!row) { return; }
    var link = row.querySelector("a[href]");
    if (link) { window.location.href = link.getAttribute("href"); }
  }

  function clearSelection() {
    if (selectedIndex === -1 && !rows.length) { return; }
    clearHighlight();
    selectedIndex = -1;
    announce("Selection cleared");
  }

  document.addEventListener("keydown", function (ev) {
    if (isFormField(ev.target)) { return; }

    if (ev.key === "/") {
      var q = searchBox();
      if (q) { ev.preventDefault(); q.focus(); q.select(); }
      return;
    }

    if (ev.key === "?") {
      var help = document.getElementById("keyhelp");
      if (help) { help.hidden = !help.hidden; }
      return;
    }

    if (ev.key === "j" || ev.key === "ArrowDown") {
      refreshRows();
      if (rows.length) { ev.preventDefault(); moveSelection(1); }
      return;
    }

    if (ev.key === "k" || ev.key === "ArrowUp") {
      refreshRows();
      if (rows.length) { ev.preventDefault(); moveSelection(-1); }
      return;
    }

    if (ev.key === "Enter") {
      if (selectedIndex >= 0 && selectedIndex < rows.length) {
        ev.preventDefault();
        openSelected();
      }
      return;
    }

    if (ev.key === "Escape") {
      if (selectedIndex !== -1) {
        ev.preventDefault();
        clearSelection();
      }
      return;
    }
  });
})();
