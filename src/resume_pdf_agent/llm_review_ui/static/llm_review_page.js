/* M22 LLM Rewrite Review UI - Local static JS. No network. */

var decisions = {};

function updateDecision(candidateId, decision) {
  if (!decisions[candidateId]) decisions[candidateId] = {};
  decisions[candidateId].decision = decision;
  refreshDecisionsJSON();
}

function updateNote(candidateId, note) {
  if (!decisions[candidateId]) decisions[candidateId] = {};
  decisions[candidateId].reviewer_note = note;
  refreshDecisionsJSON();
}

function updateReplacement(candidateId, text) {
  if (!decisions[candidateId]) decisions[candidateId] = {};
  decisions[candidateId].replacement_text = text;
  refreshDecisionsJSON();
}

function refreshDecisionsJSON() {
  var output = {
    reviewer_name: null,
    reviewed_at: new Date().toISOString(),
    notes: null,
    decisions: []
  };
  if (typeof CANDIDATES !== 'undefined') {
    CANDIDATES.forEach(function(c) {
      var d = decisions[c.candidate_id] || {};
      output.decisions.push({
        candidate_id: c.candidate_id,
        decision: d.decision || "ignore_for_now",
        reviewer_note: d.reviewer_note || null,
        replacement_text: d.replacement_text || null
      });
    });
  }
  document.getElementById('decisions-output').value = JSON.stringify(output, null, 2);
}

function copyDecisionsJSON() {
  refreshDecisionsJSON();
  var el = document.getElementById('decisions-output');
  el.select();
  try { navigator.clipboard.writeText(el.value).then(function(){alert('Copied.');}).catch(function(){alert('Copy manually.');}); }
  catch(e) { alert('Copy manually from text area.'); }
}

function downloadDecisionsJSON() {
  refreshDecisionsJSON();
  var el = document.getElementById('decisions-output');
  var blob = new Blob([el.value], {type: 'application/json'});
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url;
  a.download = 'llm_rewrite_review_decisions.json';
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
}

function filterCandidates(group) {
  document.querySelectorAll('.filter-btn').forEach(function(b){b.classList.remove('active');});
  document.querySelectorAll('.filter-btn').forEach(function(b){if(b.textContent.toLowerCase().indexOf(group.replace('_',' '))!==-1||group==='all')b.classList.add('active');});
  document.querySelectorAll('.candidate-card').forEach(function(card){
    if(group==='all' || card.getAttribute('data-group')===group) {
      card.classList.remove('hidden');
    } else {
      card.classList.add('hidden');
    }
  });
}

// Expand/collapse candidate details on header click
document.addEventListener('DOMContentLoaded', function(){
  document.querySelectorAll('.candidate-header').forEach(function(hdr){
    hdr.style.cursor = 'pointer';
    hdr.addEventListener('click', function(){
      var card = hdr.closest('.candidate-card');
      var texts = card.querySelector('.candidate-texts');
      var meta = card.querySelector('.candidate-meta');
      var ctrls = card.querySelector('.decision-controls');
      if(texts) texts.style.display = texts.style.display==='none'?'':'none';
      if(meta) meta.style.display = meta.style.display==='none'?'':'none';
      if(ctrls) ctrls.style.display = ctrls.style.display==='none'?'':'none';
    });
  });
  // Initial JSON generation
  refreshDecisionsJSON();
});
