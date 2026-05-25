// === static/js/pages/logout.js ===
// وابستگی: auth.js, token.js باید قبلاً لود شده باشن
// توجه: logout/page.tsx از localStorage استفاده می‌کرد — ما کوکی رو پاک می‌کنیم

(function () {
  // کمی تأخیر تا کاربر پیام "در حال خروج" رو ببینه
  setTimeout(function () {
    logoutAction();  // از auth.js — کوکی پاک + ریدایرکت به /
  }, 800);
})();