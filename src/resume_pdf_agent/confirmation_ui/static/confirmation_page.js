/* M20 Confirmation UI - Local static JavaScript.
 * No network requests. No external libraries. No eval.
 * Generates confirmation_decisions.json from form controls.
 */

function generateDecisions() {
  var selects = document.querySelectorAll('.decision-select');
  var decisions = [];
  selects.forEach(function(sel) {
    var itemId = sel.getAttribute('data-item-id');
    var decision = sel.value;
    if (!decision) return;
    var noteInput = document.querySelector('.decision-note[data-item-id="' + itemId + '"]');
    var note = noteInput ? noteInput.value : '';
    var entry = { item_id: itemId, decision: decision };
    if (note) entry.user_note = note;
    if (decision === 'needs_editing' && note) entry.replacement_text = note;
    if (decision === 'provide_evidence' && note) entry.provided_evidence = note;
    decisions.push(entry);
  });

  var result = {
    reviewer_name: null,
    reviewed_at: new Date().toISOString(),
    notes: null,
    decisions: decisions
  };

  var textarea = document.getElementById('decisions-json');
  textarea.value = JSON.stringify(result, null, 2);
}

function copyDecisions() {
  generateDecisions();
  var textarea = document.getElementById('decisions-json');
  textarea.select();
  try {
    navigator.clipboard.writeText(textarea.value).then(function() {
      alert('JSON copied to clipboard.');
    }).catch(function() {
      alert('Clipboard not available. Please copy manually from the text area.');
    });
  } catch(e) {
    alert('Clipboard not available. Please copy manually from the text area.');
  }
}

function downloadDecisions() {
  generateDecisions();
  var textarea = document.getElementById('decisions-json');
  var blob = new Blob([textarea.value], {type: 'application/json'});
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url;
  a.download = 'confirmation_decisions.json';
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function filterItems(priority) {
  var groups = document.querySelectorAll('.priority-group');
  var buttons = document.querySelectorAll('.filter-btn');
  buttons.forEach(function(b) { b.classList.remove('active'); });
  event.target.classList.add('active');
  groups.forEach(function(g) {
    if (priority === 'all' || g.getAttribute('data-priority') === priority) {
      g.style.display = '';
    } else {
      g.style.display = 'none';
    }
  });
}

// Auto-generate on any decision change
document.addEventListener('DOMContentLoaded', function() {
  var selects = document.querySelectorAll('.decision-select');
  selects.forEach(function(s) {
    s.addEventListener('change', generateDecisions);
  });
});
