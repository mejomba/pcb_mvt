// === static/js/components/pcb-card.js ===
// جایگزین: SingleCart.tsx / PcbCard

(function () {

  // ─── Render یک کارت ──────────────────────────────
  function renderPcbCard(card) {
    var featuredClass = card.isFeatured ? 'pcb-card-featured' : '';
    var btnClass      = card.isFeatured ? 'pcb-card-btn-featured' : 'pcb-card-btn-default';

    var itemsHTML = (card.items || []).map(function (item) {
      return `<li>${item}</li>`;
    }).join('');

    var badgeHTML = card.isFeatured
      ? `<span class="pcb-card-badge">Limited Time Offer</span>`
      : '';

    return `
      <div class="pcb-card ${featuredClass}">
        ${badgeHTML}

        <!-- تصویر -->
        <div class="pcb-card-image">
          <img src="${card.image}" alt="${card.title}" loading="lazy" />
        </div>

        <!-- محتوا -->
        <div class="pcb-card-body">
          <h3 class="pcb-card-title">${card.title}</h3>
          <p class="pcb-card-subtitle">
            From <span class="pcb-price">${card.price}</span> /5pcs
            &nbsp;|&nbsp; Build Time: ${card.buildTime}
          </p>
          <ul class="pcb-card-list">${itemsHTML}</ul>
        </div>

        <!-- دکمه‌ها -->
        <div class="pcb-card-actions">
          <button type="button" class="pcb-card-btn ${btnClass}">
            Quote Now
          </button>
          <button type="button" class="pcb-learn-more">
            Learn More &rsaquo;
          </button>
        </div>
      </div>
    `;
  }

  // ─── Render همه کارت‌ها در یک container ──────────
  function renderPcbCards(containerId, cards) {
    var el = document.getElementById(containerId);
    if (!el) return;

    if (!cards || !cards.length) {
      el.innerHTML = '<p style="text-align:center;color:#9ca3af;">موردی یافت نشد.</p>';
      return;
    }

    el.innerHTML = cards.map(renderPcbCard).join('');
  }

  // ─── Public API ───────────────────────────────────
  window.renderPcbCards = renderPcbCards;

})();