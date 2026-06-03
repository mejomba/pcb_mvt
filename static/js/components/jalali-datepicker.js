// === static/js/components/jalali-datepicker.js ===
// تقویم شمسی — بدون وابستگی به کتابخونه خارجی

(function (root) {
  'use strict';

  function toFa(n) {
    return String(n).replace(/\d/g, function (d) { return '۰۱۲۳۴۵۶۷۸۹'[d]; });
  }
  function pad(n) { return n < 10 ? '0' + n : String(n); }

  var J_MONTHS = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور',
                  'مهر','آبان','آذر','دی','بهمن','اسفند'];
  var J_DAYS_SHORT = ['ش','ی','د','س','چ','پ','ج'];

  // ════════════════════════════════════════════════
  // الگوریتم استاندارد فرهادی (سازگار و درست)
  // ════════════════════════════════════════════════

  // ─── Gregorian → Jalali ────────────────────────────
  function toJalali(gy, gm, gd) {
    var g_d_m = [0,31,59,90,120,151,181,212,243,273,304,334];
    var jy;
    if (gy > 1600) { jy = 979; gy -= 1600; } else { jy = 0; gy -= 621; }
    var gy2 = (gm > 2) ? (gy + 1) : gy;
    var days = (365 * gy) + Math.floor((gy2 + 3) / 4) - Math.floor((gy2 + 99) / 100)
             + Math.floor((gy2 + 399) / 400) - 80 + gd + g_d_m[gm - 1];
    jy += 33 * Math.floor(days / 12053);
    days %= 12053;
    jy += 4 * Math.floor(days / 1461);
    days %= 1461;
    if (days > 365) { jy += Math.floor((days - 1) / 365); days = (days - 1) % 365; }
    var jm = (days < 186) ? 1 + Math.floor(days / 31) : 7 + Math.floor((days - 186) / 30);
    var jd = 1 + ((days < 186) ? (days % 31) : ((days - 186) % 30));
    return [jy, jm, jd];
  }

  // ─── Jalali → Gregorian ────────────────────────────
  function toGregorian(jy, jm, jd) {
    var gy;
    if (jy > 979) { gy = 1600; jy -= 979; } else { gy = 621; }
    var days = (365 * jy) + (Math.floor(jy / 33) * 8) + Math.floor(((jy % 33) + 3) / 4)
             + 78 + jd + ((jm < 7) ? (jm - 1) * 31 : ((jm - 7) * 30) + 186);
    gy += 400 * Math.floor(days / 146097);
    days %= 146097;
    if (days > 36524) {
      gy += 100 * Math.floor(--days / 36524);
      days %= 36524;
      if (days >= 365) days++;
    }
    gy += 4 * Math.floor(days / 1461);
    days %= 1461;
    if (days > 365) { gy += Math.floor((days - 1) / 365); days = (days - 1) % 365; }
    var gd = days + 1;
    var sal_a = [0, 31, ((gy % 4 === 0 && gy % 100 !== 0) || (gy % 400 === 0)) ? 29 : 28,
                 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
    var gm;
    for (gm = 0; gm < 13; gm++) {
      var v = sal_a[gm];
      if (gd <= v) break;
      gd -= v;
    }
    return [gy, gm, gd];
  }

  // ─── Days in Jalali month ───────────────────────────
  function jMonthDays(jy, jm) {
    if (jm <= 6) return 31;
    if (jm <= 11) return 30;
    var leapMod = [1,5,9,13,17,22,26,30];
    return leapMod.indexOf(jy % 33) !== -1 ? 30 : 29;
  }

  // ─── Day of week (0=Sat … 6=Fri) ───────────────────
  function jDayOfWeek(jy, jm, jd) {
    var g = toGregorian(jy, jm, jd);
    var jsDay = new Date(g[0], g[1]-1, g[2]).getDay();
    return (jsDay + 1) % 7;
  }

  // ─── Helpers ────────────────────────────────────────
  function dateNum(d) { return d.y * 10000 + d.m * 100 + d.d; }
  function dateLt(a, b) { return dateNum(a) < dateNum(b); }
  function dateEq(a, b) { return a && b && dateNum(a) === dateNum(b); }
  function formatDate(d)   { return d ? d.y + '/' + pad(d.m) + '/' + pad(d.d) : ''; }
  function formatDateFa(d) { return d ? toFa(d.y) + '/' + toFa(pad(d.m)) + '/' + toFa(pad(d.d)) : ''; }
  function gregStr(d) {
    var g = toGregorian(d.y, d.m, d.d);
    return g[0] + '-' + pad(g[1]) + '-' + pad(g[2]);  // YYYY-MM-DD
  }

  // ════════════════════════════════════════════════════
  // WIDGET
  // ════════════════════════════════════════════════════
  function JalaliDatePicker(options) {
    this.options = Object.assign({
      range: true, onSelect: null, anchorEl: null, container: null,
      placeholder: 'انتخاب تاریخ', lang: 'fa',
    }, options || {});

    var today = toJalali(new Date().getFullYear(), new Date().getMonth()+1, new Date().getDate());
    this._state = {
      viewYear: today[0], viewMonth: today[1],
      startDate: null, endDate: null, hoverDate: null, selecting: 'start',
    };
    this._today = { y: today[0], m: today[1], d: today[2] };
    this._open = false;
    this._el = null;
    this._init();
  }

  JalaliDatePicker.prototype._init = function () {
    var self = this;
    this._el = document.createElement('div');
    this._el.className = 'jdp-wrapper';
    this._el.style.display = 'none';

    (this.options.container || document.body).appendChild(this._el);

    if (this.options.anchorEl) {
      this.options.anchorEl.addEventListener('click', function (e) {
        e.stopPropagation();
        self.toggle();
      });
    }

    document.addEventListener('click', function (e) {
      if (self._open && !self._el.contains(e.target)) self.close();
    });

    // ✅ Event Delegation — یک‌بار attach می‌شه و در برابر بازسازی DOM مقاومه
    this._el.addEventListener('click', this._onClick.bind(this));
    this._el.addEventListener('mouseover', this._onHover.bind(this));

    this._render();
  };

  // ─── Click handler (delegated) ──────────────────────
  JalaliDatePicker.prototype._onClick = function (e) {
    var s = this._state;

    // Navigation
    var nav = e.target.closest('[data-nav]');
    if (nav) {
      e.stopPropagation();
      if (nav.dataset.nav === 'prev') {
        if (s.viewMonth === 1) { s.viewYear--; s.viewMonth = 12; } else s.viewMonth--;
      } else {
        if (s.viewMonth === 12) { s.viewYear++; s.viewMonth = 1; } else s.viewMonth++;
      }
      this._render();
      return;
    }

    // Today
    if (e.target.closest('.jdp-btn-today')) {
      e.stopPropagation();
      var t = this._today;
      s.viewYear = t.y; s.viewMonth = t.m;
      s.startDate = { y: t.y, m: t.m, d: t.d };
      s.endDate = null; s.selecting = 'end';
      this._render();
      this._fire();
      return;
    }

    // Clear
    if (e.target.closest('.jdp-btn-clear')) {
      e.stopPropagation();
      s.startDate = null; s.endDate = null; s.selecting = 'start';
      this._render();
      this._fire();
      return;
    }

    // Apply
    if (e.target.closest('.jdp-btn-apply')) {
      e.stopPropagation();
      this.close();
      return;
    }

    // Day cell
    var day = e.target.closest('.jdp-day');
    if (day) {
      e.stopPropagation();
      var clicked = { y: +day.dataset.y, m: +day.dataset.m, d: +day.dataset.d };

      if (!this.options.range) {
        s.startDate = clicked; s.endDate = null;
      } else if (s.selecting === 'start' || !s.startDate) {
        s.startDate = clicked; s.endDate = null; s.selecting = 'end';
      } else {
        if (dateLt(clicked, s.startDate)) {
          s.endDate = s.startDate; s.startDate = clicked;
        } else {
          s.endDate = clicked;
        }
        s.selecting = 'start';
      }
      s.hoverDate = null;
      this._render();
      this._fire();
    }
  };

  // ─── Hover handler (delegated, class-only update) ──
  JalaliDatePicker.prototype._onHover = function (e) {
    var s = this._state;
    if (!this.options.range || !s.startDate || s.endDate) return;
    var day = e.target.closest('.jdp-day');
    if (!day) return;

    s.hoverDate = { y: +day.dataset.y, m: +day.dataset.m, d: +day.dataset.d };
    // فقط class ها رو آپدیت می‌کنیم — DOM بازسازی نمی‌شه
    var ns = dateNum(s.startDate), nh = dateNum(s.hoverDate);
    var lo = Math.min(ns, nh), hi = Math.max(ns, nh);

    this._el.querySelectorAll('.jdp-day').forEach(function (td) {
      var n = (+td.dataset.y) * 10000 + (+td.dataset.m) * 100 + (+td.dataset.d);
      td.classList.remove('jdp-hover-range');
      if (n > lo && n < hi) td.classList.add('jdp-hover-range');
    });
  };

  // ─── fire onSelect ──────────────────────────────────
  JalaliDatePicker.prototype._fire = function () {
    var s = this._state;
    if (this.options.onSelect) this.options.onSelect(s.startDate, s.endDate);
  };

  // ─── Render (only innerHTML, NO event re-binding) ──
  JalaliDatePicker.prototype._render = function () {
    var s = this._state;
    var jy = s.viewYear, jm = s.viewMonth;
    var totalDays = jMonthDays(jy, jm);
    var firstDow  = jDayOfWeek(jy, jm, 1);

    var cells = '';
    var cellIdx = 0;

    for (var e = 0; e < firstDow; e++) { cells += '<td class="jdp-empty"></td>'; cellIdx++; }

    for (var d = 1; d <= totalDays; d++) {
      var cur = { y: jy, m: jm, d: d };
      var cls = ['jdp-day'];

      if (dateEq(cur, this._today))   cls.push('jdp-today');
      if (dateEq(cur, s.startDate))   cls.push('jdp-sel-start');
      if (dateEq(cur, s.endDate))     cls.push('jdp-sel-end');

      if (s.startDate && s.endDate) {
        var n = dateNum(cur), ns = dateNum(s.startDate), ne = dateNum(s.endDate);
        if (n > ns && n < ne) cls.push('jdp-in-range');
      }

      cells += '<td class="' + cls.join(' ') + '" ' +
               'data-y="' + jy + '" data-m="' + jm + '" data-d="' + d + '">' +
               toFa(d) + '</td>';
      cellIdx++;
      if (cellIdx % 7 === 0 && d < totalDays) cells += '</tr><tr>';
    }

    var remaining = 7 - (cellIdx % 7);
    if (remaining < 7) for (var r = 0; r < remaining; r++) cells += '<td class="jdp-empty"></td>';

    var displayStr = '';
    if (s.startDate && s.endDate) displayStr = formatDateFa(s.startDate) + ' — ' + formatDateFa(s.endDate);
    else if (s.startDate)         displayStr = formatDateFa(s.startDate);

    this._el.innerHTML =
      '<div class="jdp-panel">' +
        '<div class="jdp-header">' +
          '<button type="button" class="jdp-nav" data-nav="prev"><i class="bi bi-chevron-right"></i></button>' +
          '<div class="jdp-month-year">' +
            '<span class="jdp-month-name">' + J_MONTHS[jm-1] + '</span>' +
            '<span class="jdp-year">' + toFa(jy) + '</span>' +
          '</div>' +
          '<button type="button" class="jdp-nav" data-nav="next"><i class="bi bi-chevron-right"></i></button>' +
        '</div>' +
        '<table class="jdp-table">' +
          '<thead><tr>' + J_DAYS_SHORT.map(function(x){return '<th>'+x+'</th>';}).join('') + '</tr></thead>' +
          '<tbody><tr>' + cells + '</tr></tbody>' +
        '</table>' +
        (this.options.range ?
          '<div class="jdp-range-display"><span>' + (displayStr || 'انتخاب بازه تاریخ') + '</span></div>' : '') +
        '<div class="jdp-footer">' +
          '<button type="button" class="jdp-btn jdp-btn-today">امروز</button>' +
          '<button type="button" class="jdp-btn jdp-btn-clear">پاک کردن</button>' +
          '<button type="button" class="jdp-btn jdp-btn-apply">تأیید</button>' +
        '</div>' +
      '</div>';
    // ⛔ دیگه _attachEvents صدا زده نمی‌شه — delegation کار رو انجام می‌ده
  };

  JalaliDatePicker.prototype.open = function () {
    this._open = true; this._el.style.display = 'block'; this._render();
  };
  JalaliDatePicker.prototype.close = function () {
    this._open = false; this._el.style.display = 'none';
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
      startGreg: s.startDate ? gregStr(s.startDate) : null,  // YYYY-MM-DD میلادی
      endGreg:   s.endDate   ? gregStr(s.endDate)   : null,
    };
  };

  JalaliDatePicker.prototype.clear = function () {
    this._state.startDate = null; this._state.endDate = null; this._state.selecting = 'start';
    this._render();
  };

  root.JalaliDatePicker = JalaliDatePicker;
  root.JalaliUtils = {
    toJalali: toJalali, toGregorian: toGregorian,
    format: formatDate, formatFa: formatDateFa, toFa: toFa,
    gregStr: gregStr,
  };

})(window);