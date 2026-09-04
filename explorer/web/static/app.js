/* RHACO Corpus Explorer -- keyboard navigation (integrator seed; owned by the web builder from wave 3).
   Vanilla JS, no framework. `/` focuses the search box; `?` lists the keys. */
(function () {
  "use strict";
  function searchBox() { return document.querySelector('input[name="q"]'); }
  document.addEventListener("keydown", function (ev) {
    if (ev.target && (ev.target.tagName === "INPUT" || ev.target.tagName === "TEXTAREA" || ev.target.tagName === "SELECT")) { return; }
    if (ev.key === "/") { var q = searchBox(); if (q) { ev.preventDefault(); q.focus(); q.select(); } }
    if (ev.key === "?") { var el = document.getElementById("keyhelp"); if (el) { el.hidden = !el.hidden; } }
  });
})();
