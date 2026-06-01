// === static/js/components/orders/orders-table.js ===
// وابستگی: api.js, token.js باید قبلاً لود شده باشن

(function () {

  // ─── Status Config ─────────────────────────────────
  const STATUS_CONFIG = {
    pending:          { text: 'در انتظار بررسی',       cls: 'badge-yellow'  },
    quotation:        { text: 'پیش فاکتور شده',        cls: 'badge-blue'    },
    process:          { text: 'در حال ساخت',           cls: 'badge-purple'  },
    pending_delivery: { text: 'در انتظار تحویل',       cls: 'badge-green'   },
    deliver:          { text: 'تحویل شده',             cls: 'badge-green'   },
    canceled:         { text: 'لغو شده',               cls: 'badge-red'     },
  };

  // ─── Helpers ────────────────────────────────────────
  function debounce(fn, delay) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  function formatPersianDate(dateString) {
    try {
      return new Intl.DateTimeFormat('fa-IR', {
        year: 'numeric', month: 'long', day: 'numeric',
      }).format(new Date(dateString));
    } catch (_) {
      return dateString;
    }
  }

  // ─── Status Badge HTML ──────────────────────────────
  function statusBadgeHTML(order) {
    const { status, id } = order;

    if (status === 'quotation') {
      // حالت ویژه: آپلود رسید پرداخت
      return `
        <div class="payment-upload" data-order-id="${id}">
          <span class="badge badge-blue">پیش فاکتور شده — در انتظار پرداخت</span>
          <span class="badge badge-green-light upload-trigger"
                data-order-id="${id}"
                role="button"
                tabindex="0">
            <i class="bi bi-upload"></i> آپلود رسید
          </span>
          <input type="file"
                 class="upload-file-input"
                 data-order-id="${id}"
                 accept="image/*,.pdf"
                 style="display:none;" />
          <button class="btn btn-upload-submit"
                  data-order-id="${id}"
                  style="display:none;">
            ارسال رسید پرداخت
          </button>
          <span class="upload-msg badge" data-order-id="${id}" style="display:none;"></span>
        </div>
      `;
    }

    const cfg = STATUS_CONFIG[status] || { text: status, cls: 'badge-gray' };
    return `<span class="badge ${cfg.cls}">${cfg.text}</span>`;
  }

  // ─── Actions (دانلود فایل‌ها) ───────────────────────
  function actionsHTML(order) {
    let html = `
      <a href="${order.file || '#'}"
         target="_blank"
         class="action-icon-btn"
         title="دانلود فایل Gerber">
        <i class="bi bi-cpu"></i>
      </a>
    `;

    if (order.quotation) {
      html += `
        <a href="${order.quotation}"
           target="_blank"
           class="action-icon-btn"
           title="دانلود پیش فاکتور">
          <i class="bi bi-file-text"></i>
        </a>
      `;
    }

    if (Array.isArray(order.payments_urls)) {
      order.payments_urls.forEach(function (pay) {
        html += `
          <a href="${pay}"
             target="_blank"
             class="action-icon-btn"
             title="دانلود رسید پرداخت">
            <i class="bi bi-receipt"></i>
          </a>
        `;
      });
    }

    return html;
  }

  // ─── Order Details (expanded row) ───────────────────
  function orderDetailsHTML(order) {
    if (!order.selections || order.selections.length === 0) {
      return '<p class="order-details-empty">مشخصات فنی ثبت نشده است.</p>';
    }

    const items = order.selections.map(function (sel) {
      return `
        <div class="order-detail-item">
          <span class="detail-label">${sel.attribute_name}:</span>
          <span class="detail-value">${sel.value}</span>
        </div>
      `;
    }).join('');

    return `<div class="order-details-grid">${items}</div>`;
  }

  // ─── Render Table ────────────────────────────────────
  function renderOrdersTable(containerId, orders) {
    const container = document.getElementById(containerId);
    if (!container) return;

    if (!orders || orders.length === 0) {
      container.innerHTML = '<p class="orders-empty">هیچ سفارشی یافت نشد.</p>';
      return;
    }

    const rows = orders.map(function (order) {
      return `
        <tr class="orders-row" data-order-id="${order.id}">
          <td class="orders-td">
            <button class="expand-btn icon-btn" data-order-id="${order.id}" title="جزئیات">
              <i class="bi bi-plus-lg"></i>
            </button>
          </td>
          <td class="orders-td orders-id">
            <span class="font-mono">#${order.id}</span>
          </td>
          <td class="orders-td">${formatPersianDate(order.created_at)}</td>
          <td class="orders-td">${order.quantity}</td>
          <td class="orders-td">${statusBadgeHTML(order)}</td>
          <td class="orders-td orders-actions">${actionsHTML(order)}</td>
        </tr>
        <tr class="orders-detail-row" data-detail-for="${order.id}" style="display:none;">
          <td colspan="6" class="orders-detail-td">
            <div class="order-details-wrapper">
              <h4 class="order-details-title">مشخصات فنی سفارش</h4>
              ${orderDetailsHTML(order)}
            </div>
          </td>
        </tr>
      `;
    }).join('');

    container.innerHTML = `
      <div class="orders-table-wrapper">
        <table class="orders-table">
          <thead class="orders-thead">
            <tr>
              <th class="orders-th"></th>
              <th class="orders-th">شماره سفارش</th>
              <th class="orders-th">تاریخ ثبت</th>
              <th class="orders-th">تعداد</th>
              <th class="orders-th">وضعیت</th>
              <th class="orders-th" style="text-align:center;">فایل</th>
            </tr>
          </thead>
          <tbody>
            ${rows}
          </tbody>
        </table>
      </div>
    `;

    _attachTableEvents(container);
  }

  // ─── Event Listeners ─────────────────────────────────
  function _attachTableEvents(container) {

    // Expand/Collapse
    container.querySelectorAll('.expand-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const id = this.dataset.orderId;
        const detailRow = container.querySelector(`[data-detail-for="${id}"]`);
        const icon = this.querySelector('i');
        const isExpanded = detailRow.style.display !== 'none';

        detailRow.style.display = isExpanded ? 'none' : '';
        icon.className = isExpanded ? 'bi bi-plus-lg' : 'bi bi-dash-lg';
      });
    });

    // آپلود رسید — باز کردن file dialog
    container.querySelectorAll('.upload-trigger').forEach(function (trigger) {
      function openDialog() {
        const id = this.dataset.orderId;
        const input = container.querySelector(`.upload-file-input[data-order-id="${id}"]`);
        input && input.click();
      }
      trigger.addEventListener('click', openDialog);
      trigger.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' || e.key === ' ') openDialog.call(this, e);
      });
    });

    // وقتی فایل انتخاب شد، دکمه ارسال نمایش داده می‌شه
    container.querySelectorAll('.upload-file-input').forEach(function (input) {
      input.addEventListener('change', function () {
        const id = this.dataset.orderId;
        const submitBtn = container.querySelector(`.btn-upload-submit[data-order-id="${id}"]`);
        if (this.files && this.files[0] && submitBtn) {
          submitBtn.style.display = 'inline-block';
        }
      });
    });

    // ارسال فایل رسید
    container.querySelectorAll('.btn-upload-submit').forEach(function (btn) {
      btn.addEventListener('click', async function () {
        const id = this.dataset.orderId;
        const input  = container.querySelector(`.upload-file-input[data-order-id="${id}"]`);
        const msgEl  = container.querySelector(`.upload-msg[data-order-id="${id}"]`);

        if (!input || !input.files[0]) return;

        this.disabled = true;
        this.textContent = 'در حال آپلود...';

        const formData = new FormData();
        formData.append('file', input.files[0]);
        formData.append('order', id);

        try {
          // مستقیم به Django — بدون proxy
          await api.upload('/api/v1/pcb/order_payment_receipt/upload/', formData);

          this.style.display = 'none';
          if (msgEl) {
            msgEl.textContent = '✓ ذخیره شد';
            msgEl.className = 'upload-msg badge badge-green-light';
            msgEl.style.display = 'inline-block';
          }
        } catch (err) {
          this.disabled = false;
          this.textContent = 'ارسال رسید پرداخت';
          if (msgEl) {
            msgEl.textContent = '✕ خطا در آپلود';
            msgEl.className = 'upload-msg badge badge-red';
            msgEl.style.display = 'inline-block';
          }
          console.error('Upload error:', err);
        }
      });
    });
  }

  // ─── Search با Debounce ───────────────────────────────
  function initOrdersSearch(inputId, allOrders, tableContainerId) {
    const input = document.getElementById(inputId);
    if (!input) return;

    // مقدار اولیه از URL
    const initialQ = new URLSearchParams(window.location.search).get('q') || '';
    if (initialQ) input.value = initialQ;

    const filterAndRender = debounce(function (term) {
      // آپدیت URL بدون reload
      const params = new URLSearchParams(window.location.search);
      term ? params.set('q', term) : params.delete('q');
      window.history.replaceState({}, '', '?' + params.toString());

      // فیلتر سفارش‌ها
      const filtered = term
        ? allOrders.filter(function (o) {
            return (
              String(o.id).includes(term) ||
              (o.user_name && o.user_name.includes(term))
            );
          })
        : allOrders;

      renderOrdersTable(tableContainerId, filtered);
    }, 300);

    input.addEventListener('input', function () {
      filterAndRender(this.value.trim());
    });

    // رندر اولیه با فیلتر موجود در URL
    renderOrdersTable(tableContainerId,
      initialQ
        ? allOrders.filter(o =>
            String(o.id).includes(initialQ) ||
            (o.user_name && o.user_name.includes(initialQ))
          )
        : allOrders
    );
  }

  // ─── Public API ──────────────────────────────────────
  window.renderOrdersTable  = renderOrdersTable;
  window.initOrdersSearch   = initOrdersSearch;

})();