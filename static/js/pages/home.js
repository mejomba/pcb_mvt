// === static/js/pages/home.js ===

(function () {
  // خواندن داده کارت‌ها از JSON script tag
  try {
    var dataEl = document.getElementById('pcb-cards-data');
    if (!dataEl) return;

    var cards = JSON.parse(dataEl.textContent || '[]');
    renderPcbCards('pcb-cards-grid', cards);

  } catch (err) {
    console.error('Error rendering PCB cards:', err);
  }
})();