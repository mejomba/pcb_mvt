// === static/js/pages/profile.js ===
// وابستگی: api.js, token.js, utils.js, orders-table.js

(function () {

  // ─── داده‌های ثابت (sampleDesigns) ────────────────
  var sampleDesigns = [
    { id: 1, name: 'Motor controller',    updated: '1404/06/19', layers: 2 },
    { id: 2, name: 'Power board (mini)',  updated: '1404/06/08', layers: 4 },
    { id: 3, name: 'Breakout module',     updated: '1404/04/30', layers: 1 },
  ];

  var allOrders = [];
  var currentUser = {};

  // ─── وضعیت‌های سفارش ───────────────────────────────
  var STATUS_CONFIG = {
    pending:          { text: 'در انتظار بررسی',   cls: 'badge-yellow'  },
    quotation:        { text: 'پیش فاکتور شده',    cls: 'badge-blue'    },
    process:          { text: 'در حال ساخت',       cls: 'badge-purple'  },
    pending_delivery: { text: 'در انتظار تحویل',   cls: 'badge-green'   },
    deliver:          { text: 'تحویل شده',         cls: 'badge-green'   },
    canceled:         { text: 'لغو شده',           cls: 'badge-red'     },
  };

  // ─── بارگذاری داده‌ها ──────────────────────────────
  async function loadPageData() {
    try {
      var results = await Promise.all([
        api.get('/auth/profile/'),
        api.get('/pcb/orders/'),
      ]);

      currentUser = results[0] || {};
      allOrders   = (results[1] && results[1].results) || [];

    } catch (err) {
      console.error('خطا در بارگذاری داده‌ها:', err);
      allOrders   = [];
      currentUser = {};
    }

    renderAll();
  }

  // ─── رندر همه بخش‌ها ────────────────────────────────
  function renderAll() {
    renderHeader();
    renderStats();
    renderRecentOrders();
    renderDesigns();
    populateSettings();

    // نمایش بخش‌های پنهان
    var statsEl   = document.getElementById('profile-stats');
    var tabNavEl  = document.getElementById('profile-tabs-nav');
    if (statsEl)  statsEl.style.display   = '';
    if (tabNavEl) tabNavEl.style.display  = '';

    // رندر جدول سفارش‌ها در تب orders
    initOrdersSearch('orders-search-input', allOrders, 'orders-table-container');
  }

  // ─── Header ────────────────────────────────────────
  function renderHeader() {
    var loading = document.getElementById('profile-loading');
    var inner   = document.getElementById('profile-header-inner');
    var nameEl  = document.getElementById('profile-name');
    var avatarEl= document.getElementById('profile-avatar');

    if (loading) loading.style.display = 'none';
    if (inner)   inner.style.display   = 'flex';

    if (nameEl)   nameEl.textContent = currentUser.phone || currentUser.username || '—';
    if (avatarEl) {
      if (currentUser.avatar) {
        avatarEl.src = currentUser.avatar;
      } else {
        // placeholder avatar با اول نام
        avatarEl.style.display = 'none';
        var wrapper = avatarEl.closest('.profile-avatar-wrapper');
        if (wrapper) {
          wrapper.innerHTML = `
            <div class="profile-avatar-placeholder">
              <i class="bi bi-person-fill"></i>
            </div>
          `;
        }
      }
    }
  }

  // ─── Stats ─────────────────────────────────────────
  function renderStats() {
    var el = document.getElementById('stat-orders-count');
    if (el) el.textContent = formatNumber(allOrders.length);
  }

  // ─── Recent Orders (overview tab) ──────────────────
  function renderRecentOrders() {
    var container = document.getElementById('recent-orders-list');
    if (!container) return;

    if (!allOrders.length) {
      container.innerHTML = '<p class="text-muted">هیچ سفارشی ثبت نشده است.</p>';
      return;
    }

    var items = allOrders.map(function (order) {
      var cfg  = STATUS_CONFIG[order.status] || { text: order.status, cls: 'badge-gray' };
      var date = '';
      try {
        date = new Intl.DateTimeFormat('fa-IR').format(new Date(order.created_at));
      } catch (_) { date = order.created_at; }

      var selectionsHTML = '';
      if (order.selections && order.selections.length > 0) {
        var selItems = order.selections.map(function (sel) {
          return `<li><span class="sel-label">${sel.attribute_name}:</span> ${sel.value}</li>`;
        }).join('');
        selectionsHTML = `
          <div class="order-card-selections">
            <div class="sel-heading">ویژگی‌ها:</div>
            <ul class="sel-list">${selItems}</ul>
          </div>
        `;
      }

      return `
        <li class="order-card-item">
          <div class="order-card-header">
            <span class="order-card-id">
              سفارش #${order.id} —
              <span class="badge ${cfg.cls}">${cfg.text}</span>
            </span>
            <span class="order-card-date">${date}</span>
          </div>
          ${selectionsHTML}
        </li>
      `;
    }).join('');

    container.innerHTML = `<ul class="orders-card-list">${items}</ul>`;
  }

  // ─── Designs (actions tab) ─────────────────────────
  function renderDesigns() {
    var grid = document.getElementById('designs-grid');
    if (!grid) return;

    if (!sampleDesigns.length) {
      grid.innerHTML = '<p class="text-muted">پروژه‌ای ذخیره نشده است.</p>';
      return;
    }

    grid.innerHTML = sampleDesigns.map(function (d) {
      return `
        <div class="design-card">
          <div class="design-card-info">
            <div class="design-name">${d.name}</div>
            <div class="design-date">${d.updated}</div>
          </div>
          <div class="design-layers">${d.layers}L</div>
        </div>
      `;
    }).join('');
  }

  // ─── Settings (تنظیمات) ────────────────────────────
  function populateSettings() {
    var fnEl   = document.getElementById('settings-full-name');
    var emailEl= document.getElementById('settings-email');
    var addrEl = document.getElementById('settings-address');

    if (fnEl    && currentUser.full_name) fnEl.value    = currentUser.full_name;
    if (emailEl && currentUser.email)     emailEl.value = currentUser.email;
    if (addrEl  && currentUser.address)   addrEl.value  = currentUser.address;
  }

  // ─── Tabs ──────────────────────────────────────────
  function initTabs() {
    var tabBtns   = document.querySelectorAll('.profile-tab-btn');
    var tabPanels = document.querySelectorAll('.tab-panel');

    tabBtns.forEach(function (btn) {
      btn.addEventListener('click', function () {
        var target = this.dataset.tab;

        tabBtns.forEach(function (b)   { b.classList.remove('active'); });
        tabPanels.forEach(function (p) { p.style.display = 'none'; });

        this.classList.add('active');
        var panel = document.getElementById('tab-' + target);
        if (panel) panel.style.display = 'block';

        // جدول orders رو فقط وقتی تب فعاله render کن (lazy)
        if (target === 'orders') {
          initOrdersSearch('orders-search-input', allOrders, 'orders-table-container');
        }
      });
    });
  }

  // ─── Settings Form Submit ──────────────────────────
  function initSettingsForm() {
    var form = document.getElementById('settings-form');
    if (!form) return;

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      var errEl  = document.getElementById('settings-form-error');
      var submitBtn = form.querySelector('[type="submit"]');

      if (errEl) errEl.style.display = 'none';
      submitBtn.disabled    = true;
      submitBtn.textContent = 'در حال ذخیره...';

      var payload = {
        full_name: form.querySelector('[name="full_name"]').value,
        email:     form.querySelector('[name="email"]').value,
        address:   form.querySelector('[name="address"]').value,
      };

      try {
        await api.patch('/auth/profile/', payload);
        submitBtn.textContent = '✓ ذخیره شد';
        setTimeout(function () {
          submitBtn.disabled    = false;
          submitBtn.textContent = 'ذخیره';
        }, 2000);
      } catch (err) {
        submitBtn.disabled    = false;
        submitBtn.textContent = 'ذخیره';
        if (errEl) {
          errEl.textContent    = (err.data && err.data.detail) || 'خطا در ذخیره اطلاعات.';
          errEl.style.display  = 'block';
        }
      }
    });

    var cancelBtn = document.getElementById('settings-cancel');
    cancelBtn && cancelBtn.addEventListener('click', function () {
      populateSettings(); // برگشت به مقادیر اولیه
    });
  }

  // ─── Init ──────────────────────────────────────────
  initTabs();
  initSettingsForm();
  loadPageData();

})();