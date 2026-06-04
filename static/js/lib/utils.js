// === js/lib/utils.js ===

/**
 * عدد را با فرمت locale نمایش می‌دهد
 * @param {number} num
 * @param {string} locale
 * @returns {string}
 */
function formatNumber(num, locale = 'fa-IR') {
  // باگ اصلی: num == 0 مقدار falsy بود و بدون فرمت برمی‌گشت
  if (num === null || num === undefined) return '';
  return Number(num).toLocaleString(locale);
}