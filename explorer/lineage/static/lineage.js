/* RHACO Corpus Explorer -- lineage module (builder-owned: lineage).
   Progressive enhancement ONLY: the graph is a server-rendered inline <svg>
   and the reasoning trail is a plain server-rendered list, both fully
   legible and navigable with this file absent or JavaScript disabled (task
   B8 module-specific addition to rule 1). No fetch, no XHR, no external
   asset, no CDN -- this file only toggles CSS classes already shipped in
   lineage.css. */
(function () {
  "use strict";
  var svg = document.querySelector(".lineage-graph");
  if (!svg) { return; }

  function highlight(docId, on) {
    if (!docId) { return; }
    var edges = svg.querySelectorAll(
      '[data-edge-from="' + CSS.escape(docId) + '"], [data-edge-to="' + CSS.escape(docId) + '"]'
    );
    for (var i = 0; i < edges.length; i++) {
      edges[i].classList.toggle("lineage-edge-highlight", on);
    }
  }

  var links = svg.querySelectorAll("a[data-doc-id]");
  for (var j = 0; j < links.length; j++) {
    (function (a) {
      var id = a.getAttribute("data-doc-id");
      a.addEventListener("focus", function () { highlight(id, true); });
      a.addEventListener("blur", function () { highlight(id, false); });
      a.addEventListener("mouseenter", function () { highlight(id, true); });
      a.addEventListener("mouseleave", function () { highlight(id, false); });
    })(links[j]);
  }
})();
