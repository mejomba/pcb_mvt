// === static/js/components/orders/advanced-table.js ===
// جدول پیشرفته: جستجو، جابجایی ستون، تغییر اندازه، فیلتر تاریخ شمسی

(function (root) {
  'use strict';

  var STATUS_CFG = {
    pending:          { text: 'در انتظار بررسی',        cls: 'st-yellow'  },
    quotation:        { text: 'پیش فاکتور — انتظار پرداخت', cls: 'st-blue' },
    process:          { text: 'در حال ساخت',            cls: 'st-purple'  },
    pending_delivery: { text: 'در انتظار تحویل',        cls: 'st-teal'    },
    deliver:          { text: 'تحویل شده',              cls: 'st-green'   },
    canceled:         { text: 'لغو شده',               cls: 'st-red'     },
  };

  var STATUS_OPTIONS = Object.keys(STATUS_CFG).map(function(k) {
    return '<option value="' + k + '">' + STATUS_CFG[k].text + '</option>';
  }).join('');

  function debounce(fn, ms) {
    var t;
    return function() { var a=arguments,c=this; clearTimeout(t); t=setTimeout(function(){fn.apply(c,a);},ms); };
  }

  function formatPersianDate(iso) {
    try {
      var d = new Date(iso);
      return new Intl.DateTimeFormat('fa-IR').format(d);
    } catch(_) { return iso; }
  }

  // ════════════════════════════════════════════════════
  // AdvancedOrderTable
  // ════════════════════════════════════════════════════
  function AdvancedOrderTable(options) {
    this.containerId  = options.containerId;
    this.apiBase      = options.apiBase || '/pcb/orders/';
    this.onUpload     = options.onUpload || null;

    // Column definitions — ordered array, user can reorder
    this._cols = [
      { key:'expander', label:'',          width:48,  resizable:false, searchable:false, fixed:true  },
      { key:'id',       label:'شماره',     width:90,  resizable:true,  searchable:true,  type:'text'   },
      { key:'date',     label:'تاریخ',     width:150, resizable:true,  searchable:true,  type:'date'   },
      { key:'quantity', label:'تعداد',     width:80,  resizable:true,  searchable:true,  type:'text'   },
      { key:'status',   label:'وضعیت',     width:200, resizable:true,  searchable:true,  type:'select' },
      { key:'files',    label:'فایل‌ها',   width:160, resizable:true,  searchable:false, fixed:false   },
    ];

    this._filters   = { id:'', dateFrom:'', dateTo:'', quantity:'', status:'' };
    this._expanded  = {};   // { rowId: bool }
    this._allData   = [];
    this._loading   = false;

    this._dragSrc   = null; // dragged col index
    this._resizing  = null; // { colIdx, startX, startW }

    this._datepicker = null;
    this._render();
    this._loadData();
  }

  // ─── Build shell HTML ────────────────────────────────
  AdvancedOrderTable.prototype._render = function () {
    var c = document.getElementById(this.containerId);
    if (!c) return;

    var colGroup = this._cols.map(function(col){
      return '<col style="width:' + col.width + 'px;">';
    }).join('');

    c.innerHTML =
      '<div class="adt-wrapper">' +
        '<div class="adt-loading" id="adt-loading" style="display:none;">' +
          '<div class="adt-spinner"></div><span>در حال بارگذاری...</span>' +
        '</div>' +
        '<div class="adt-scroll">' +
          '<table class="adt-table" id="adt-table">' +
            '<colgroup id="adt-colgroup">' + colGroup + '</colgroup>' +
            '<thead id="adt-thead">' +
              '<tr id="adt-header-row" class="adt-header-row"></tr>' +
              '<tr id="adt-filter-row" class="adt-filter-row"></tr>' +
            '</thead>' +
            '<tbody id="adt-tbody"></tbody>' +
          '</table>' +
        '</div>' +
        '<div class="adt-empty" id="adt-empty" style="display:none;">' +
          '<i class="bi bi-inbox"></i><span>سفارشی یافت نشد.</span>' +
        '</div>' +
      '</div>';

    this._renderHeaders();
    this._renderFilters();
    this._initDatePicker();
  };

  // ─── Headers (with drag + resize handles) ───────────
  AdvancedOrderTable.prototype._renderHeaders = function () {
    var self = this;
    var tr = document.getElementById('adt-header-row');
    if (!tr) return;
    tr.innerHTML = '';

    this._cols.forEach(function (col, idx) {
      var th = document.createElement('th');
      th.className = 'adt-th' + (col.fixed ? ' adt-th-fixed' : '');
      th.dataset.colIdx = idx;
      th.style.width = col.width + 'px';

      if (!col.fixed) {
        th.draggable = true;
        th.innerHTML =
          '<div class="adt-th-inner">' +
            '<span class="adt-drag-handle" title="جابجایی"><i class="bi bi-grip-vertical"></i></span>' +
            '<span class="adt-th-label">' + col.label + '</span>' +
          '</div>' +
          (col.resizable ? '<div class="adt-resize-handle" data-resize-idx="' + idx + '"></div>' : '');
      } else {
        th.innerHTML =
          '<div class="adt-th-inner"><span class="adt-th-label">' + col.label + '</span></div>';
      }

      // Drag events for column reorder
      if (!col.fixed) {
        th.addEventListener('dragstart', function(e) {
          self._dragSrc = idx;
          e.dataTransfer.effectAllowed = 'move';
          th.classList.add('adt-dragging');
        });
        th.addEventListener('dragend', function() {
          th.classList.remove('adt-dragging');
          document.querySelectorAll('.adt-drag-over').forEach(function(el){el.classList.remove('adt-drag-over');});
        });
        th.addEventListener('dragover', function(e) {
          e.preventDefault();
          e.dataTransfer.dropEffect = 'move';
          document.querySelectorAll('.adt-drag-over').forEach(function(el){el.classList.remove('adt-drag-over');});
          th.classList.add('adt-drag-over');
        });
        th.addEventListener('drop', function(e) {
          e.preventDefault();
          th.classList.remove('adt-drag-over');
          if (self._dragSrc !== null && self._dragSrc !== idx) {
            self._moveColumn(self._dragSrc, idx);
          }
          self._dragSrc = null;
        });
      }

      tr.appendChild(th);
    });

    // Resize handles
    this._attachResizeHandles();
  };

  // ─── Resize handles ─────────────────────────────────
  AdvancedOrderTable.prototype._attachResizeHandles = function () {
    var self = this;
    document.querySelectorAll('[data-resize-idx]').forEach(function (handle) {
      handle.addEventListener('mousedown', function (e) {
        e.preventDefault();
        var idx = +this.dataset.resizeIdx;
        self._resizing = { colIdx: idx, startX: e.clientX, startW: self._cols[idx].width };

        function onMove(ev) {
          var diff = ev.clientX - self._resizing.startX;
          var newW = Math.max(60, self._resizing.startW + diff);
          self._cols[self._resizing.colIdx].width = newW;
          // Update colgroup
          var colgroup = document.getElementById('adt-colgroup');
          if (colgroup) {
            var cols = colgroup.querySelectorAll('col');
            if (cols[self._resizing.colIdx]) {
              cols[self._resizing.colIdx].style.width = newW + 'px';
            }
          }
          // Update th width
          var ths = document.querySelectorAll('#adt-header-row .adt-th');
          if (ths[self._resizing.colIdx]) ths[self._resizing.colIdx].style.width = newW + 'px';
        }

        function onUp() {
          self._resizing = null;
          document.removeEventListener('mousemove', onMove);
          document.removeEventListener('mouseup', onUp);
        }

        document.addEventListener('mousemove', onMove);
        document.addEventListener('mouseup', onUp);
      });
    });
  };

  // ─── Filter row ─────────────────────────────────────
  AdvancedOrderTable.prototype._renderFilters = function () {
    var self = this;
    var tr = document.getElementById('adt-filter-row');
    if (!tr) return;
    tr.innerHTML = '';

    this._cols.forEach(function (col) {
      var td = document.createElement('th');
      td.className = 'adt-filter-cell';

      if (!col.searchable) {
        td.innerHTML = '';
      } else if (col.type === 'select') {
        td.innerHTML =
          '<select class="adt-filter-select" data-filter="status">' +
            '<option value="">همه وضعیت‌ها</option>' +
            STATUS_OPTIONS +
          '</select>';
      } else if (col.type === 'date') {
        td.innerHTML =
          '<div class="adt-date-filter-wrapper">' +
            '<button type="button" class="adt-date-filter-btn" id="adt-date-btn">' +
              '<i class="bi bi-calendar3"></i>' +
              '<span id="adt-date-label">فیلتر تاریخ</span>' +
            '</button>' +
          '</div>' +
          '<div id="adt-date-picker-container" class="adt-date-picker-container"></div>';
      } else {
        td.innerHTML =
          '<input type="text" class="adt-filter-input" ' +
                 'data-filter="' + col.key + '" ' +
                 'placeholder="جستجو..." />';
      }

      tr.appendChild(td);
    });

    this._bindFilterEvents();
  };

  // ─── Bind filter inputs ──────────────────────────────
  AdvancedOrderTable.prototype._bindFilterEvents = function () {
    var self = this;
    var doSearch = debounce(function () { self._loadData(); }, 400);

    // Text filters
    document.querySelectorAll('.adt-filter-input').forEach(function (inp) {
      inp.addEventListener('input', function () {
        self._filters[this.dataset.filter] = this.value.trim();
        doSearch();
      });
    });

    // Status select
    var sel = document.querySelector('.adt-filter-select[data-filter="status"]');
    if (sel) sel.addEventListener('change', function () {
      self._filters.status = this.value;
      self._loadData();
    });
  };

  // ─── Date Picker init ────────────────────────────────
  AdvancedOrderTable.prototype._initDatePicker = function () {
    var self = this;
    var container = document.getElementById('adt-date-picker-container');
    var btn       = document.getElementById('adt-date-btn');
    var label     = document.getElementById('adt-date-label');
    if (!container || !btn || typeof JalaliDatePicker === 'undefined') return;

    this._datepicker = new JalaliDatePicker({
      range: true,
      container: container,
      onSelect: function (start, end) {
        if (start) {
          var v = JalaliUtils.getValue ? JalaliUtils.getValue(start) : (start.y+'/'+pad2(start.m)+'/'+pad2(start.d));
          // Convert to Gregorian for API
          var g = JalaliUtils.toGregorian(start.y, start.m, start.d);
          self._filters.dateFrom = g[0]+'-'+pad2(g[1])+'-'+pad2(g[2]);
          label.textContent = JalaliUtils.formatFa(start);
        } else {
          self._filters.dateFrom = '';
          label.textContent = 'فیلتر تاریخ';
        }
        if (end) {
          var g2 = JalaliUtils.toGregorian(end.y, end.m, end.d);
          self._filters.dateTo = g2[0]+'-'+pad2(g2[1])+'-'+pad2(g2[2]);
          label.textContent += ' — ' + JalaliUtils.formatFa(end);
        } else {
          self._filters.dateTo = '';
        }
        if (start) self._loadData();
      }
    });

    btn.addEventListener('click', function (e) {
      e.stopPropagation();
      self._datepicker.toggle();
    });

    function pad2(n) { return n < 10 ? '0' + n : String(n); }
  };

  // ─── Load data from API ──────────────────────────────
  AdvancedOrderTable.prototype._loadData = function () {
    var self = this;
    var f = this._filters;

    var params = new URLSearchParams();
    if (f.id)       params.set('id',        f.id);
    if (f.quantity) params.set('quantity',   f.quantity);
    if (f.status)   params.set('status',     f.status);
    if (f.dateFrom) params.set('created_at__gte', f.dateFrom);
    if (f.dateTo)   params.set('created_at__lte', f.dateTo);

    this._setLoading(true);

    api.get(this.apiBase + '?' + params.toString()).then(function (data) {
      self._allData = (data && data.results) ? data.results : (Array.isArray(data) ? data : []);
      self._renderRows();
      self._setLoading(false);
    }).catch(function (err) {
      console.error('Order fetch error:', err);
      self._setLoading(false);
    });
  };

  // ─── Render rows ─────────────────────────────────────
  AdvancedOrderTable.prototype._renderRows = function () {
    var self = this;
    var tbody = document.getElementById('adt-tbody');
    var empty = document.getElementById('adt-empty');
    if (!tbody) return;

    if (!this._allData.length) {
      tbody.innerHTML = '';
      if (empty) empty.style.display = 'flex';
      return;
    }
    if (empty) empty.style.display = 'none';

    var html = '';

    this._allData.forEach(function (order) {
      var isExpanded = !!self._expanded[order.id];
      var cfg = STATUS_CFG[order.status] || { text: order.status, cls: 'st-gray' };

      // Build cells per col order
      var cells = self._cols.map(function (col) {
        switch (col.key) {
          case 'expander':
            return '<td class="adt-td adt-td-expander">' +
              '<button class="adt-expand-btn" data-order-id="' + order.id + '" title="جزئیات">' +
                '<i class="bi bi-' + (isExpanded ? 'dash-lg' : 'plus-lg') + '"></i>' +
              '</button></td>';

          case 'id':
            return '<td class="adt-td"><span class="adt-order-id">#' + order.id + '</span></td>';

          case 'date':
            return '<td class="adt-td adt-td-date">' + formatPersianDate(order.created_at) + '</td>';

          case 'quantity':
            return '<td class="adt-td adt-td-center">' + order.quantity + '</td>';

          case 'status':
            return '<td class="adt-td">' + self._statusCell(order) + '</td>';

          case 'files':
            return '<td class="adt-td">' + self._filesCell(order) + '</td>';

          default: return '<td class="adt-td"></td>';
        }
      }).join('');

      html += '<tr class="adt-row" data-order-id="' + order.id + '">' + cells + '</tr>';

      // Detail row
      if (isExpanded) {
        html += '<tr class="adt-detail-row">' +
          '<td colspan="' + self._cols.length + '" class="adt-detail-td">' +
            self._detailPanel(order) +
          '</td></tr>';
      }
    });

    tbody.innerHTML = html;
    this._attachRowEvents();
  };

  // ─── Status cell (with payment upload) ──────────────
  AdvancedOrderTable.prototype._statusCell = function (order) {
    var cfg = STATUS_CFG[order.status] || { text: order.status, cls: 'st-gray' };
    if (order.status !== 'quotation') {
      return '<span class="adt-status-badge ' + cfg.cls + '">' + cfg.text + '</span>';
    }
    return '<div class="adt-status-upload">' +
      '<span class="adt-status-badge ' + cfg.cls + '">' + cfg.text + '</span>' +
      '<label class="adt-upload-trigger" title="آپلود رسید">' +
        '<i class="bi bi-upload"></i> آپلود رسید' +
        '<input type="file" class="adt-file-hidden" data-order-id="' + order.id + '" accept="image/*,.pdf">' +
      '</label>' +
    '</div>';
  };

  // ─── Files cell ──────────────────────────────────────
  AdvancedOrderTable.prototype._filesCell = function (order) {
    var html = '';
    if (order.file) {
      html += '<a href="' + order.file + '" target="_blank" class="adt-file-btn" title="فایل Gerber">' +
              '<i class="bi bi-cpu"></i></a>';
    }
    if (order.quotation) {
      html += '<a href="' + order.quotation + '" target="_blank" class="adt-file-btn" title="پیش فاکتور">' +
              '<i class="bi bi-file-text"></i></a>';
    }
    if (Array.isArray(order.payments_urls)) {
      order.payments_urls.forEach(function (url, i) {
        html += '<a href="' + url + '" target="_blank" class="adt-file-btn" title="رسید پرداخت ' + (i+1) + '">' +
                '<i class="bi bi-receipt"></i></a>';
      });
    }
    return html || '<span class="adt-no-file">—</span>';
  };

  // ─── Detail panel (expanded) ─────────────────────────
  AdvancedOrderTable.prototype._detailPanel = function (order) {
    var specs = '';
    if (order.selections && order.selections.length) {
      specs = order.selections.map(function (s) {
        return '<div class="adt-spec-item"><span class="adt-spec-label">' + s.attribute_name + '</span>' +
               '<span class="adt-spec-value">' + s.value + '</span></div>';
      }).join('');
    } else {
      specs = '<p class="adt-no-specs">مشخصات فنی ثبت نشده.</p>';
    }
    return '<div class="adt-detail-panel">' +
             '<h4 class="adt-detail-title">مشخصات فنی سفارش #' + order.id + '</h4>' +
             '<div class="adt-spec-grid">' + specs + '</div>' +
           '</div>';
  };

  // ─── Row event listeners ─────────────────────────────
  AdvancedOrderTable.prototype._attachRowEvents = function () {
    var self = this;

    // Expand/collapse
    document.querySelectorAll('.adt-expand-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        var id = +this.dataset.orderId;
        self._expanded[id] = !self._expanded[id];
        self._renderRows();
      });
    });

    // Payment upload (in table cell)
    document.querySelectorAll('.adt-file-hidden').forEach(function (inp) {
      inp.addEventListener('change', function () {
        var file = this.files[0];
        var orderId = this.dataset.orderId;
        if (!file) return;
        self._uploadPayment(orderId, file, this);
      });
    });
  };

  // ─── Upload payment ──────────────────────────────────
  AdvancedOrderTable.prototype._uploadPayment = function (orderId, file, inputEl) {
    var label = inputEl ? inputEl.closest('.adt-upload-trigger') : null;
    if (label) label.innerHTML = '<i class="bi bi-arrow-repeat adt-spin"></i> آپلود...';

    var formData = new FormData();
    formData.append('file', file);
    formData.append('order', orderId);

    api.upload('/pcb/order_payment_receipt/upload/', formData).then(function () {
      if (label) label.innerHTML = '<i class="bi bi-check-lg"></i> ذخیره شد';
    }).catch(function () {
      if (label) label.innerHTML = '<i class="bi bi-x-lg"></i> خطا — دوباره';
    });
  };

  // ─── Move column (reorder) ───────────────────────────
  AdvancedOrderTable.prototype._moveColumn = function (fromIdx, toIdx) {
    var col = this._cols.splice(fromIdx, 1)[0];
    this._cols.splice(toIdx, 0, col);
    this._render();
    this._renderRows();
    this._initDatePicker();
    this._bindFilterEvents();
  };

  // ─── Loading state ───────────────────────────────────
  AdvancedOrderTable.prototype._setLoading = function (show) {
    this._loading = show;
    var el = document.getElementById('adt-loading');
    if (el) el.style.display = show ? 'flex' : 'none';
  };

  // Expose
  root.AdvancedOrderTable = AdvancedOrderTable;

})(window);