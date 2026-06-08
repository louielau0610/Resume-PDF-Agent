var currentStatus = "all";
var allCollapsed = false;

function setStatusFilter(status) {
  currentStatus = status;
  document.querySelectorAll(".filter-btn").forEach(function(btn) {
    btn.classList.toggle("active", btn.getAttribute("data-status") === status);
  });
  applyFilters();
}

function applyFilters() {
  var queryEl = document.getElementById("search-input");
  var query = queryEl ? queryEl.value.toLowerCase().trim() : "";
  document.querySelectorAll(".candidate-card").forEach(function(card) {
    var statusMatch = currentStatus === "all" || card.getAttribute("data-status") === currentStatus;
    var searchText = card.getAttribute("data-search") || "";
    var queryMatch = !query || searchText.indexOf(query) !== -1;
    card.classList.toggle("hidden", !(statusMatch && queryMatch));
  });
}

function toggleCard(candidateId) {
  var body = document.getElementById("body-" + candidateId);
  if (!body) return;
  body.classList.toggle("collapsed");
}

function toggleAllCards() {
  allCollapsed = !allCollapsed;
  document.querySelectorAll(".candidate-body").forEach(function(body) {
    body.classList.toggle("collapsed", allCollapsed);
  });
}

function copyCandidateText(candidateId, text) {
  var message = "Candidate text for manual review copied: " + candidateId;
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(text).then(function() {
      console.log(message);
    }).catch(function() {
      copyWithSelection(text);
    });
  } else {
    copyWithSelection(text);
  }
}

function copyWithSelection(text) {
  var area = document.createElement("textarea");
  area.value = text;
  area.setAttribute("readonly", "readonly");
  area.style.position = "fixed";
  area.style.left = "-9999px";
  document.body.appendChild(area);
  area.select();
  try { document.execCommand("copy"); } catch (err) { console.log("Manual copy required."); }
  document.body.removeChild(area);
}

document.addEventListener("DOMContentLoaded", function() {
  applyFilters();
});
