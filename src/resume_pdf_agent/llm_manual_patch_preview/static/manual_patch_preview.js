/* M27 Manual Patch Preview UI - Local static JS. No network. Preview-only. */
function filterItems(status) {
  document.querySelectorAll('.filter-btn').forEach(function(b){b.classList.remove('active');});
  document.querySelectorAll('.filter-btn').forEach(function(b){
    if(b.textContent.toLowerCase().indexOf(status.replace('_',' '))!==-1||status==='all')b.classList.add('active');
  });
  document.querySelectorAll('.candidate-card').forEach(function(card){
    if(status==='all'||card.getAttribute('data-status')===status){card.classList.remove('hidden');}
    else{card.classList.add('hidden');}
  });
}
