// === static/js/pages/profile.js ===

(function () {
  'use strict';

  var allOrders   = [];
  var currentUser = {};
  var advTable    = null;

  var STATUS_CFG = {
    pending:          { text: 'در انتظار بررسی',           cls: 'st-yellow'  },
    quotation:        { text: 'پیش فاکتور — انتظار پرداخت', cls: 'st-blue'  },
    process:          { text: 'در حال ساخت',               cls: 'st-purple'  },
    pending_delivery: { text: 'در انتظار تحویل',           cls: 'st-teal'    },
    deliver:          { text: 'تحویل شده',                 cls: 'st-green'   },
    canceled:         { text: 'لغو شده',                  cls: 'st-red'     },
  };

  // ─── Tab switching ──────────────────────────────────
  function switchTab(name) {
    document.querySelectorAll('.pf-tab').forEach(function (b) { b.classList.remove('active'); });
    document.querySelectorAll('.pf-panel').forEach(function (p) { p.style.display = 'none'; });

    var btn   = document.querySelector('.pf-tab[data-tab="' + name + '"]');
    var panel = document.getElementById('tab-' + name);
    if (btn)   btn.classList.add('active');
    if (panel) panel.style.display = 'block';

    // Init advanced table lazily on first visit
    if (name === 'orders' && !advTable) {
      advTable = new AdvancedOrderTable({
        containerId: 'orders-advanced-table',
        apiBase:     '/api/v1/pcb/orders/',
        onUpload:    function (orderId, file) { console.log('Upload from table:', orderId); },
      });
    }
  }

  window.switchTab = switchTab; // used by inline onclick in template

  document.querySelectorAll('.pf-tab').forEach(function (btn) {
    btn.addEventListener('click', function () {
      switchTab(this.dataset.tab);
    });
  });

  // ─── Load page data ─────────────────────────────────
  async function loadPageData() {
    try {
      var results = await Promise.all([
        api.get('/api/v1/auth/profile/'),
        api.get('/api/v1/pcb/orders/'),
      ]);
      currentUser = results[0] || {};
      allOrders   = (results[1] && results[1].results) ? results[1].results : [];
    } catch (e) {
      console.error('Profile load error:', e);
      allOrders   = [];
      currentUser = {};
    }
    renderHero();
    renderOrderCards();
    populateSettings();
    populateUploadSelect();

    var tabsWrap = document.getElementById('pf-tabs-wrap');
    if (tabsWrap) tabsWrap.style.visibility = 'visible';
  }

  // ─── Hero ────────────────────────────────────────────
  function renderHero() {
    var loading = document.getElementById('pf-hero-loading');
    var inner   = document.getElementById('pf-hero-inner');
    if (loading) loading.style.display = 'none';
    if (inner)   inner.style.display   = 'flex';

    var nameEl = document.getElementById('pf-hero-name');
    if (nameEl) nameEl.textContent = currentUser.phone || currentUser.username || 'کاربر';

    var avatarWrap = document.getElementById('pf-avatar-wrap');
    if (avatarWrap && currentUser.avatar) {
      avatarWrap.innerHTML = '<img src="' + currentUser.avatar + '" alt="avatar" class="pf-avatar-img">';
    }

    // Stats
    var total     = allOrders.length;
    var pending   = allOrders.filter(function(o){return o.status==='pending';}).length;
    var quotation = allOrders.filter(function(o){return o.status==='quotation';}).length;
    var delivered = allOrders.filter(function(o){return o.status==='deliver';}).length;

    setText('stat-total',     total);
    setText('stat-pending',   pending);
    setText('stat-quotation', quotation);
    setText('stat-delivered', delivered);
  }

  function setText(id, val) {
    var el = document.getElementById(id);
    if (el) el.textContent = typeof formatNumber === 'function' ? formatNumber(val) : val;
  }

  // ─── Overview Order Cards ────────────────────────────
  function renderOrderCards() {
    var container = document.getElementById('pf-order-cards');
    if (!container) return;

    if (!allOrders.length) {
      container.innerHTML =
        '<div class="pf-empty-state">' +
          '<i class="bi bi-inbox pf-empty-icon"></i>' +
          '<p>هنوز سفارشی ثبت نشده است.</p>' +
          '<a href="/api/v1/pcb/new-order/" class="pf-btn pf-btn-primary pf-btn-sm mt-2">ثبت اولین سفارش</a>' +
        '</div>';
      return;
    }

    // Show last 5 orders in overview
    var recent = allOrders.slice(0, 5);
    container.innerHTML = recent.map(orderCardHTML).join('');
    attachCardEvents(container);
  }

  function orderCardHTML(order) {
    var cfg  = STATUS_CFG[order.status] || { text: order.status, cls: 'st-gray' };
    var date = '';
    try { date = new Intl.DateTimeFormat('fa-IR').format(new Date(order.created_at)); } catch(_){}

    // File buttons
    var files = '';
    if (order.file) {
      files += '<a href="' + order.file + '" target="_blank" class="pf-file-btn" title="فایل Gerber">' +
               '<i class="bi bi-cpu"></i><span>Gerber</span></a>';
    }
    if (order.quotation) {
      files += '<a href="' + order.quotation + '" target="_blank" class="pf-file-btn pf-file-btn--doc" title="پیش فاکتور">' +
               '<i class="bi bi-file-text"></i><span>پیش فاکتور</span></a>';
    }
    if (Array.isArray(order.payments_urls)) {
      order.payments_urls.forEach(function (url, i) {
        files += '<a href="' + url + '" target="_blank" class="pf-file-btn pf-file-btn--receipt" title="رسید ' + (i+1) + '">' +
                 '<i class="bi bi-receipt"></i><span>رسید ' + (i+1) + '</span></a>';
      });
    }

    // Upload for quotation orders
    var uploadSection = '';
    if (order.status === 'quotation') {
      uploadSection =
        '<div class="pf-card-upload" data-order-id="' + order.id + '">' +
          '<label class="pf-inline-upload" title="آپلود رسید پرداخت">' +
            '<i class="bi bi-cloud-upload"></i>' +
            '<span class="pf-inline-upload-text">آپلود رسید پرداخت</span>' +
            '<input type="file" class="pf-card-file-input" data-order-id="' + order.id + '" accept="image/*,.pdf">' +
          '</label>' +
          '<button class="pf-btn pf-btn-primary pf-btn-sm pf-card-submit-btn" ' +
                  'data-order-id="' + order.id + '" style="display:none;" disabled>' +
            'ارسال' +
          '</button>' +
          '<span class="pf-card-upload-msg" data-order-id="' + order.id + '" style="display:none;"></span>' +
        '</div>';
    }

    // Specs (collapsed)
    var specs = '';
    if (order.selections && order.selections.length) {
      specs = order.selections.map(function (s) {
        return '<span class="pf-spec-tag"><b>' + s.attribute_name + ':</b> ' + s.value + '</span>';
      }).join('');
    }

    return '<div class="pf-order-card" data-order-id="' + order.id + '">' +

      '<div class="pf-order-card-header">' +
        '<div class="pf-order-card-id">' +
          '<span class="pf-order-num">#' + order.id + '</span>' +
          '<span class="pf-status-badge ' + cfg.cls + '">' + cfg.text + '</span>' +
        '</div>' +
        '<div class="pf-order-card-meta">' +
          '<span><i class="bi bi-calendar3 me-1"></i>' + date + '</span>' +
          // '<span><i class="bi bi-layers me-1"></i>تعداد: ' + order.quantity + '</span>' +
        '</div>' +
      '</div>' +

      (files ? '<div class="pf-order-files">' + files + '</div>' : '') +

      uploadSection +

      (specs ?
        '<details class="pf-order-specs">' +
          '<summary>مشخصات فنی</summary>' +
          '<div class="pf-spec-tags">' + specs + '</div>' +
        '</details>'
      : '') +

    '</div>';
  }

  function attachCardEvents(container) {
    // File input change
    container.querySelectorAll('.pf-card-file-input').forEach(function (inp) {
      inp.addEventListener('change', function () {
        var id = this.dataset.orderId;
        var submitBtn = container.querySelector('.pf-card-submit-btn[data-order-id="' + id + '"]');
        var label     = this.closest('.pf-inline-upload');
        if (this.files && this.files[0]) {
          if (submitBtn) { submitBtn.style.display = 'inline-flex'; submitBtn.disabled = false; }
          if (label) {
            label.querySelector('.pf-inline-upload-text').textContent = this.files[0].name;
          }
        }
      });
    });

    // Submit upload
    container.querySelectorAll('.pf-card-submit-btn').forEach(function (btn) {
      btn.addEventListener('click', async function () {
        var id      = this.dataset.orderId;
        var inp     = container.querySelector('.pf-card-file-input[data-order-id="' + id + '"]');
        var msgEl   = container.querySelector('.pf-card-upload-msg[data-order-id="' + id + '"]');
        if (!inp || !inp.files[0]) return;

        btn.disabled    = true;
        btn.textContent = 'ارسال...';

        var fd = new FormData();
        fd.append('file',  inp.files[0]);
        fd.append('order', id);

        try {
          await api.upload('/api/v1/pcb/order_payment_receipt/upload/', fd);
          btn.style.display = 'none';
          if (msgEl) { msgEl.textContent = '✓ ذخیره شد'; msgEl.className = 'pf-card-upload-msg pf-msg-ok'; msgEl.style.display = 'inline'; }
        } catch (e) {
          btn.disabled    = false;
          btn.textContent = 'ارسال';
          if (msgEl) { msgEl.textContent = '✗ خطا'; msgEl.className = 'pf-card-upload-msg pf-msg-err'; msgEl.style.display = 'inline'; }
        }
      });
    });
  }

  // ─── Dropzone (overview sidebar upload) ─────────────
  (function initDropzone() {
    var zone  = document.getElementById('pf-dropzone');
    var inp   = document.getElementById('overview-receipt-input');
    var inner = document.getElementById('pf-dropzone-inner');
    var btn   = document.getElementById('overview-upload-btn');
    var msg   = document.getElementById('overview-upload-msg');

    if (!zone || !inp) return;

    // zone.addEventListener('click', function () { inp.click(); });

    zone.addEventListener('dragover', function (e) {
      e.preventDefault();
      zone.classList.add('pf-dropzone--hover');
    });
    zone.addEventListener('dragleave', function () {
      zone.classList.remove('pf-dropzone--hover');
    });
    zone.addEventListener('drop', function (e) {
      e.preventDefault();
      zone.classList.remove('pf-dropzone--hover');
      var file = e.dataTransfer.files[0];
      if (file) setDropzoneFile(file);
    });

    inp.addEventListener('change', function () {
      if (this.files[0]) setDropzoneFile(this.files[0]);
    });

    function setDropzoneFile(file) {
      if (inner) {
        inner.innerHTML =
          '<i class="bi bi-file-earmark-check pf-dropzone-icon pf-dropzone-icon--ok"></i>' +
          '<span class="pf-dropzone-text">' + file.name + '</span>' +
          '<span class="pf-dropzone-sub">' + (file.size / 1024).toFixed(1) + ' KB</span>';
      }
      if (btn) btn.disabled = false;
      inp._selectedFile = file;
    }

    if (btn) {
      btn.addEventListener('click', async function () {
        var orderId = document.getElementById('overview-order-select').value;
        var file    = inp._selectedFile;
        if (!orderId) { alert('لطفاً ابتدا سفارش را انتخاب کنید.'); return; }
        if (!file)    { alert('لطفاً فایل رسید را انتخاب کنید.'); return; }

        btn.disabled    = true;
        btn.innerHTML   = '<i class="bi bi-arrow-repeat pf-spin me-1"></i>در حال ارسال...';
        if (msg) msg.style.display = 'none';

        var fd = new FormData();
        fd.append('file',  file);
        fd.append('order', orderId);

        try {
          await api.upload('/api/v1/pcb/order_payment_receipt/upload/', fd);
          btn.disabled  = false;
          btn.innerHTML = '<i class="bi bi-send me-1"></i>ارسال رسید';
          if (msg) { msg.textContent = '✓ رسید با موفقیت ذخیره شد'; msg.className = 'pf-upload-msg pf-msg-ok'; msg.style.display = 'block'; }
          if (inner) {
            inner.innerHTML =
              '<i class="bi bi-cloud-arrow-up pf-dropzone-icon"></i>' +
              '<span class="pf-dropzone-text">کلیک یا کشیدن فایل</span>' +
              '<span class="pf-dropzone-sub">PNG, JPG, PDF — حداکثر ۱۰MB</span>';
          }
          inp._selectedFile = null;
        } catch (e) {
          btn.disabled  = false;
          btn.innerHTML = '<i class="bi bi-send me-1"></i>ارسال رسید';
          if (msg) { msg.textContent = '✗ خطا در ارسال. دوباره تلاش کنید.'; msg.className = 'pf-upload-msg pf-msg-err'; msg.style.display = 'block'; }
        }
      });
    }
  })();

  // ─── Populate upload select ──────────────────────────
  function populateUploadSelect() {
    var sel = document.getElementById('overview-order-select');
    if (!sel) return;

    var quotationOrders = allOrders.filter(function(o) { return o.status === 'quotation'; });
    if (!quotationOrders.length) {
      sel.innerHTML = '<option value="">— سفارشی در انتظار پرداخت نیست —</option>';
      return;
    }

    sel.innerHTML = '<option value="">— انتخاب سفارش —</option>' +
      quotationOrders.map(function (o) {
        return '<option value="' + o.id + '">#' + o.id + '</option>';
      }).join('');
  }

  // ─── Settings ────────────────────────────────────────
  function populateSettings() {
    debugger
    var u = currentUser;
    var set = function (id, val) { var el = document.getElementById(id); if (el && val) el.value = val; };
    set('settings-full-name', u.full_name);
    set('settings-email',     u.email);
    // set('settings-address',   u.address);
  }

  (function initSettingsForm() {
    var form = document.getElementById('settings-form');
    if (!form) return;

    form.addEventListener('submit', async function (e) {
      e.preventDefault();
      var errEl  = document.getElementById('settings-error');
      var btn    = form.querySelector('[type="submit"]');
      if (errEl) errEl.style.display = 'none';
      btn.disabled = true; btn.textContent = 'در حال ذخیره...';

      try {
        debugger
        await api.patch('/api/v1/auth/profile/', {
          first_name: form.querySelector('[name="full_name"]').value,
          email:     form.querySelector('[name="email"]').value,
          // address:   form.querySelector('[name="address"]').value,
        });
        btn.textContent = '✓ ذخیره شد';
        setTimeout(function () { btn.disabled = false; btn.textContent = 'ذخیره'; }, 2000);
      } catch (err) {
        btn.disabled = false; btn.textContent = 'ذخیره';
        if (errEl) {
          errEl.textContent    = (err.data && err.data.detail) || 'خطا در ذخیره اطلاعات.';
          errEl.style.display  = 'block';
        }
      }
    });

    var cancelBtn = document.getElementById('settings-cancel');
    if (cancelBtn) cancelBtn.addEventListener('click', populateSettings);
  })();

  // ─── Boot ────────────────────────────────────────────
  loadPageData();

})();