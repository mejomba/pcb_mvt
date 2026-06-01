// === static/js/components/jalali-datepicker.js ===
// تقویم شمسی — بدون وابستگی به کتابخونه خارجی

(function (root) {
  'use strict';

  // ─── Persian Numerals ───────────────────────────────
  function toFa(n) {
    return String(n).replace(/\d/g, function (d) {
      return '۰۱۲۳۴۵۶۷۸۹'[d];
    });
  }
  function toEn(s) {
    return String(s).replace(/[۰-۹]/g, function (d) {
      return '۰۱۲۳۴۵۶۷۸۹'.indexOf(d);
    });
  }
  function pad(n) { return n < 10 ? '0' + n : String(n); }

  var J_MONTHS = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور',
                  'مهر','آبان','آذر','دی','بهمن','اسفند'];
  var J_DAYS_SHORT = ['ش','ی','د','س','چ','پ','ج'];

  // ─── Gregorian → Jalali ─────────────────────────────
  function toJalali(gy, gm, gd) {
    var g_d_no, j_d_no, j_np, i;
    var g_days = [31,28,31,30,31,30,31,31,30,31,30,31];
    var j_days = [31,31,31,31,31,31,30,30,30,30,30,29];

    gy -= 1600; gm -= 1; gd -= 1;
    g_d_no = 365*gy + Math.floor((gy+3)/4) - Math.floor((gy+99)/100) + Math.floor((gy+399)/400);
    for (i = 0; i < gm; ++i) g_d_no += g_days[i];
    if (gm > 1 && ((gy%4===0 && gy%100!==0)||(gy%400===0))) g_d_no++;
    g_d_no += gd;

    j_d_no = g_d_no - 79;
    j_np = Math.floor(j_d_no / 12053); j_d_no %= 12053;
    var jy = 979 + 33*j_np + 4*Math.floor(j_d_no/1461);
    j_d_no %= 1461;
    if (j_d_no >= 366) { jy += Math.floor((j_d_no-1)/365); j_d_no = (j_d_no-1)%365; }
    for (i=0; i<11 && j_d_no>=j_days[i]; ++i) j_d_no -= j_days[i];
    return [jy, i+1, j_d_no+1];
  }

  // ─── Jalali → Gregorian ─────────────────────────────
  function toGregorian(jy, jm, jd) {
    jy += 1595;
    var days = -355779 + 365*jy + Math.floor((jy+3)/4) - Math.floor((jy+99)/100)
               + Math.floor((jy+399)/400) + jd
               + (jm <= 6 ? (jm-1)*31 : (jm-7)*30 + 186);
    var gy = 400 * Math.floor(days/146097); days %= 146097;
    if (days > 36524) { gy += 100*Math.floor(--days/36524); days%=36524; if(days>=365) days++; }
    gy += 4*Math.floor(days/1461); days %= 1461;
    if (days > 364) { gy += Math.floor((days-1)/365); days = (days-1)%365; }
    var sal_a = [0,31,(gy%4===0&&(gy%100!==0||gy%400===0))?29:28,31,30,31,30,31,31,30,31,30,31];
    var gm=1; while(gm<=12 && days>=sal_a[gm]) { days-=sal_a[gm]; gm++; }
    return [gy, gm, days+1];
  }

  // ─── Days in Jalali month ────────────────────────────
  function jMonthDays(jy, jm) {
    if (jm <= 6) return 31;
    if (jm <= 11) return 30;
    // اسفند: سال کبیسه
    var leapMod = [1,5,9,13,17,22,26,30];
    return leapMod.indexOf(jy % 33) !== -1 ? 30 : 29;
  }

  // ─── Day of week for Jalali date (0=Sat … 6=Fri) ───
  function jDayOfWeek(jy, jm, jd) {
    var g = toGregorian(jy, jm, jd);
    var jsDay = new Date(g[0], g[1]-1, g[2]).getDay(); // 0=Sun
    return (jsDay + 1) % 7; // Sat=0, Sun=1, Mon=2 … Fri=6
  }

  // ─── Compare dates {y,m,d} ───────────────────────────
  function dateNum(d) { return d.y * 10000 + d.m * 100 + d.d; }
  function dateLt(a, b) { return dateNum(a) < dateNum(b); }
  function dateEq(a, b) { return a && b && dateNum(a) === dateNum(b); }

  // ─── Format ──────────────────────────────────────────
  function formatDate(d) {
    return d ? d.y + '/' + pad(d.m) + '/' + pad(d.d) : '';
  }
  function formatDateFa(d) {
    return d ? toFa(d.y) + '/' + toFa(pad(d.m)) + '/' + toFa(pad(d.d)) : '';
  }

  // ════════════════════════════════════════════════════
  // CALENDAR WIDGET
  // ════════════════════════════════════════════════════
  function JalaliDatePicker(options) {
    this.options = Object.assign({
      range: true,           // true: انتخاب بازه | false: تک تاریخ
      onSelect: null,        // callback(startDate, endDate)
      anchorEl: null,        // input یا button که picker رو toggle می‌کنه
      container: null,       // container برای append کردن
      placeholder: 'انتخاب تاریخ',
      lang: 'fa',
    }, options || {});

    var today = toJalali(new Date().getFullYear(), new Date().getMonth()+1, new Date().getDate());
    this._state = {
      viewYear:    today[0],
      viewMonth:   today[1],
      startDate:   null,
      endDate:     null,
      hoverDate:   null,
      selecting:   'start',
      open:        false,
    };
    this._today = { y: today[0], m: today[1], d: today[2] };
    this._el = null;
    this._init();
  }

  JalaliDatePicker.prototype._init = function () {
    var self = this;
    // Wrapper
    this._el = document.createElement('div');
    this._el.className = 'jdp-wrapper';
    this._el.style.display = 'none';

    if (this.options.container) {
      this.options.container.appendChild(this._el);
    } else {
      document.body.appendChild(this._el);
    }

    // Anchor click
    if (this.options.anchorEl) {
      this.options.anchorEl.addEventListener('click', function (e) {
        e.stopPropagation();
        self.toggle();
      });
    }

    // Close on outside click
    document.addEventListener('click', function (e) {
      if (self._open && !self._el.contains(e.target)) self.close();
    });

    this._render();
  };

  JalaliDatePicker.prototype._render = function () {
    var s = this._state;
    var jy = s.viewYear, jm = s.viewMonth;
    var totalDays = jMonthDays(jy, jm);
    var firstDow  = jDayOfWeek(jy, jm, 1);

    // Prev / next month
    var prev = jm === 1 ? [jy-1, 12] : [jy, jm-1];
    var next = jm === 12 ? [jy+1, 1] : [jy, jm+1];

    // Build day cells
    var cells = '';
    var cellIdx = 0;

    // Empty cells
    for (var e = 0; e < firstDow; e++) {
      cells += '<td class="jdp-empty"></td>';
      cellIdx++;
    }

    for (var d = 1; d <= totalDays; d++) {
      var cur = { y: jy, m: jm, d: d };
      var cls = ['jdp-day'];

      if (dateEq(cur, this._today))    cls.push('jdp-today');
      if (dateEq(cur, s.startDate))    cls.push('jdp-sel-start');
      if (dateEq(cur, s.endDate))      cls.push('jdp-sel-end');

      if (s.startDate && s.endDate) {
        var n = dateNum(cur);
        var ns = dateNum(s.startDate), ne = dateNum(s.endDate);
        if (n > ns && n < ne) cls.push('jdp-in-range');
      } else if (s.startDate && s.hoverDate && !s.endDate) {
        var n2 = dateNum(cur), ns2 = dateNum(s.startDate), nh = dateNum(s.hoverDate);
        var lo = Math.min(ns2, nh), hi = Math.max(ns2, nh);
        if (n2 > lo && n2 < hi) cls.push('jdp-hover-range');
        if (n2 === lo) cls.push('jdp-sel-start');
        if (n2 === hi) cls.push('jdp-sel-end');
      }

      cells += '<td class="' + cls.join(' ') + '" ' +
               'data-y="' + jy + '" data-m="' + jm + '" data-d="' + d + '">' +
               toFa(d) + '</td>';
      cellIdx++;

      if (cellIdx % 7 === 0 && d < totalDays) cells += '</tr><tr>';
    }

    // Trailing empties
    var remaining = 7 - (cellIdx % 7);
    if (remaining < 7) {
      for (var r = 0; r < remaining; r++) cells += '<td class="jdp-empty"></td>';
    }

    // Display selected range
    var displayStr = '';
    if (s.startDate && s.endDate) {
      displayStr = formatDateFa(s.startDate) + ' — ' + formatDateFa(s.endDate);
    } else if (s.startDate) {
      displayStr = formatDateFa(s.startDate);
    }

    this._el.innerHTML =
      '<div class="jdp-panel">' +
        '<div class="jdp-header">' +
          '<button type="button" class="jdp-nav" data-nav="prev">' +
            '<i class="bi bi-chevron-right"></i>' +
          '</button>' +
          '<div class="jdp-month-year">' +
            '<span class="jdp-month-name">' + J_MONTHS[jm-1] + '</span>' +
            '<span class="jdp-year">' + toFa(jy) + '</span>' +
          '</div>' +
          '<button type="button" class="jdp-nav" data-nav="next">' +
            '<i class="bi bi-chevron-left"></i>' +
          '</button>' +
        '</div>' +

        '<table class="jdp-table">' +
          '<thead><tr>' +
            J_DAYS_SHORT.map(function(d){return '<th>'+d+'</th>';}).join('') +
          '</tr></thead>' +
          '<tbody><tr>' + cells + '</tr></tbody>' +
        '</table>' +

        (this.options.range ? '<div class="jdp-range-display">' +
          '<span>' + (displayStr || 'انتخاب بازه تاریخ') + '</span>' +
        '</div>' : '') +

        '<div class="jdp-footer">' +
          '<button type="button" class="jdp-btn jdp-btn-today">امروز</button>' +
          '<button type="button" class="jdp-btn jdp-btn-clear">پاک کردن</button>' +
          '<button type="button" class="jdp-btn jdp-btn-apply">تأیید</button>' +
        '</div>' +
      '</div>';

    this._attachEvents();
  };

  JalaliDatePicker.prototype._attachEvents = function () {
    var self = this;
    var el = this._el;

    // Nav buttons
    el.querySelectorAll('[data-nav]').forEach(function (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        var s = self._state;
        if (this.dataset.nav === 'prev') {
          if (s.viewMonth === 1) { s.viewYear--; s.viewMonth = 12; }
          else s.viewMonth--;
        } else {
          if (s.viewMonth === 12) { s.viewYear++; s.viewMonth = 1; }
          else s.viewMonth++;
        }
        self._render();
      });
    });

    // Day cells
    el.querySelectorAll('.jdp-day').forEach(function (td) {
      // Hover (range preview)
      td.addEventListener('mouseenter', function () {
        if (self._state.startDate && !self._state.endDate && self.options.range) {
          self._state.hoverDate = { y: +this.dataset.y, m: +this.dataset.m, d: +this.dataset.d };
          self._render();
        }
      });

      td.addEventListener('click', function (e) {
        e.stopPropagation();
        var clicked = { y: +this.dataset.y, m: +this.dataset.m, d: +this.dataset.d };
        var s = self._state;

        if (!self.options.range) {
          s.startDate = clicked;
          s.endDate   = null;
        } else if (s.selecting === 'start' || !s.startDate) {
          s.startDate = clicked;
          s.endDate   = null;
          s.selecting = 'end';
        } else {
          // Ensure start < end
          if (dateLt(clicked, s.startDate)) {
            s.endDate   = s.startDate;
            s.startDate = clicked;
          } else {
            s.endDate = clicked;
          }
          s.selecting = 'start';
        }
        s.hoverDate = null;
        self._render();
        if (self.options.onSelect) self.options.onSelect(s.startDate, s.endDate);
      });
    });

    // Today
    var todayBtn = el.querySelector('.jdp-btn-today');
    if (todayBtn) todayBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var t = self._today;
      self._state.viewYear  = t.y;
      self._state.viewMonth = t.m;
      self._state.startDate = { y: t.y, m: t.m, d: t.d };
      self._state.endDate   = null;
      self._state.selecting = 'end';
      self._render();
      if (self.options.onSelect) self.options.onSelect(self._state.startDate, null);
    });

    // Clear
    var clearBtn = el.querySelector('.jdp-btn-clear');
    if (clearBtn) clearBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      self._state.startDate = null;
      self._state.endDate   = null;
      self._state.selecting = 'start';
      self._render();
      if (self.options.onSelect) self.options.onSelect(null, null);
    });

    // Apply
    var applyBtn = el.querySelector('.jdp-btn-apply');
    if (applyBtn) applyBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      self.close();
    });
  };

  JalaliDatePicker.prototype.open = function () {
    this._open = true;
    this._el.style.display = 'block';
    this._render();
  };

  JalaliDatePicker.prototype.close = function () {
    this._open = false;
    this._el.style.display = 'none';
  };

  JalaliDatePicker.prototype.toggle = function () {
    this._open ? this.close() : this.open();
  };

  JalaliDatePicker.prototype.getValue = function () {
    var s = this._state;
    return {
      start:    s.startDate ? formatDate(s.startDate) : null,
      end:      s.endDate   ? formatDate(s.endDate)   : null,
      startFa:  s.startDate ? formatDateFa(s.startDate) : null,
      endFa:    s.endDate   ? formatDateFa(s.endDate)   : null,
    };
  };

  JalaliDatePicker.prototype.clear = function () {
    this._state.startDate = null;
    this._state.endDate   = null;
    this._state.selecting = 'start';
    this._render();
  };

  // Expose
  root.JalaliDatePicker = JalaliDatePicker;
  root.JalaliUtils = { toJalali: toJalali, toGregorian: toGregorian, format: formatDate, formatFa: formatDateFa, toFa: toFa };

})(window);