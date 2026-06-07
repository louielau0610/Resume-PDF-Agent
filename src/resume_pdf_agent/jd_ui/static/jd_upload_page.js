/* M21 JD Upload UI - Local static JS. No network. */

var RISK_MARKERS = ["confidential","internal use only","do not distribute","proprietary hiring rubric","private recruiter notes","candidate evaluation form","interview scorecard","scoring rubric","leaked","not for public release","restricted access"];

var activeTab = "jd-text-output";

function showTab(id) {
  document.querySelectorAll('.tab-content').forEach(function(e){e.style.display='none'});
  document.querySelectorAll('.tab-btn').forEach(function(b){b.classList.remove('active')});
  document.getElementById(id).style.display='';
  event.target.classList.add('active');
  activeTab = id;
}

function analyzeLocally() {
  var text = document.getElementById('jd-text').value.toLowerCase();
  var container = document.getElementById('compliance-hints');
  if (!text.trim()) { container.innerHTML = '<p class="hint-neutral">Enter JD text first.</p>'; return; }
  var found = [];
  RISK_MARKERS.forEach(function(m){ if (text.indexOf(m) !== -1) found.push(m); });
  if (found.length === 0) {
    container.innerHTML = '<p class="hint-clear">No risky markers detected (local check only).</p>';
  } else {
    var html = '';
    found.forEach(function(m){ html += '<div class="hint-blocking"><strong>BLOCKED:</strong> "' + m + '" detected. Do not use confidential/internal content.</div>'; });
    html += '<p class="hint-neutral" style="margin-top:8px">Local hints only. Backend M15 compliance check remains authoritative.</p>';
    container.innerHTML = html;
  }
  generateOutputs();
}

function generateOutputs() {
  var text = document.getElementById('jd-text').value;
  var role = document.getElementById('target-role').value || 'User-provided JD';
  var outDir = document.getElementById('output-dir').value || 'outputs/jd_ui_run';
  document.getElementById('jd-text-output').value = text;

  var payload = { target_role: role, jd_text: text, use_user_provided_jd: true, write_jd_artifacts: true, pdf_backend: "mock", output_dir: outDir };
  document.getElementById('json-output').value = JSON.stringify(payload, null, 2);
}

function copyActiveTab() {
  generateOutputs();
  var el = document.getElementById(activeTab);
  el.select();
  try { navigator.clipboard.writeText(el.value).then(function(){alert('Copied.');}).catch(function(){alert('Copy manually.');}); }
  catch(e) { alert('Copy manually from text area.'); }
}

function downloadActiveTab() {
  generateOutputs();
  var el = document.getElementById(activeTab);
  var blob = new Blob([el.value], {type: activeTab === 'json-output' ? 'application/json' : 'text/plain'});
  var url = URL.createObjectURL(blob);
  var a = document.createElement('a');
  a.href = url;
  a.download = activeTab === 'json-output' ? 'jd_payload.json' : 'jd_text.txt';
  document.body.appendChild(a); a.click(); document.body.removeChild(a); URL.revokeObjectURL(url);
}

document.getElementById('jd-text').addEventListener('input', function(){ if (this.value.trim()) generateOutputs(); });
