// auth-guard.js — در صفحاتی که نیاز به لاگین دارن include میشه
(function () {
  function getCookie(name) {
    const match = document.cookie.match(
      new RegExp("(^| )" + name + "=([^;]+)")
    );
    return match ? decodeURIComponent(match[2]) : null;
  }

  if (!getCookie("access")) {
    const next = encodeURIComponent(window.location.pathname);
    window.location.href = "/api/v1/auth/template/otp?next=" + next;
  }
})();