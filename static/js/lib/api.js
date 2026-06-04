// === js/lib/api.js — نسخه نهایی ===
const API_BASE = 'http://globalpcb.ir'; // آدرس بک‌اند جنگو

// ─── Cookie Helpers ───────────────────────────────────────────
function getCookie(name) {
  const match = document.cookie.match(
    new RegExp('(^| )' + name + '=([^;]+)')
  );
  return match ? decodeURIComponent(match[2]) : null;
}

function setCookie(name, value, days = 1) {
  const expires = new Date(Date.now() + days * 864e5).toUTCString();
  document.cookie = `${name}=${encodeURIComponent(value)}; expires=${expires}; path=/`;
}

// ─── Token Refresh Queue ──────────────────────────────────────
let isRefreshing = false;
let failedQueue = [];

function processQueue(error) {
  failedQueue.forEach(({ resolve, reject }) =>
    error ? reject(error) : resolve()
  );
  failedQueue = [];
}

// ─── Core Request ─────────────────────────────────────────────
async function apiRequest(url, options = {}) {
  debugger
  const accessToken = typeof getAccessToken === 'function'
    ? getAccessToken()
    : getCookie('access');

  const csrfToken = getCookie('csrftoken');
  const method    = (options.method || 'GET').toUpperCase();
  const isFormData = options.body instanceof FormData;

  const headers = { ...(options.headers || {}) };

  // FormData: مرورگر خودش Content-Type رو با boundary ست می‌کنه
  if (!isFormData) {
    headers['Content-Type'] = headers['Content-Type'] || 'application/json';
  }

  if (accessToken) {
    headers['Authorization'] = `Bearer ${accessToken}`;
  }

  if (csrfToken && ['POST', 'PUT', 'PATCH', 'DELETE'].includes(method)) {
    headers['X-CSRFToken'] = csrfToken;
  }

  let response;
  try {
    response = await fetch(API_BASE + url, {
      method,
      headers,
      credentials: 'include',
      // FormData مستقیم پاس می‌شه، بقیه JSON
      body: options.body instanceof FormData
        ? options.body
        : options.body !== undefined
          ? JSON.stringify(options.body)
          : undefined,
    });
  } catch (networkErr) {
    console.error('Network error:', networkErr);
    throw { status: 0, message: 'خطای شبکه' };
  }

  // ─── 401: تلاش برای refresh ───────────────────────────────
  if (response.status === 401 && !options._retry) {
    if (isRefreshing) {
      return new Promise((resolve, reject) => {
        failedQueue.push({ resolve, reject });
      }).then(() => apiRequest(url, { ...options, _retry: true }));
    }

    isRefreshing = true;
    options._retry = true;

    try {
      const refreshToken = getCookie('refresh');
      console.log('Attempting token refresh...');

      const refreshRes = await fetch(`${API_BASE}/auth/token/refresh/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ refresh: refreshToken }),
      });

      if (!refreshRes.ok) throw new Error('Refresh failed');

      const refreshData = await refreshRes.json();
      if (refreshData.access) {
        setCookie('access', refreshData.access);
        console.log('Token refreshed successfully');
      }

      processQueue(null);
      return apiRequest(url, { ...options, _retry: true });

    } catch (err) {
      processQueue(err);
      console.error('Refresh token failed, redirecting to login...');
      window.location.href = '/api/v1/auth/template/otp/';
      throw err;

    } finally {
      isRefreshing = false;
    }
  }

  // ─── خطاهای دیگه ─────────────────────────────────────────
  if (!response.ok) {
    let errData = {};
    try { errData = await response.json(); } catch (_) {}
    throw { status: response.status, data: errData };
  }

  // ─── پاسخ موفق ───────────────────────────────────────────
  const text = await response.text();
  return text ? JSON.parse(text) : null;
}

// ─── Shorthand Methods ────────────────────────────────────────
const api = {
  get:    (url, options = {})        => apiRequest(url, { ...options, method: 'GET' }),
  post:   (url, body, options = {})  => apiRequest(url, { ...options, method: 'POST',   body }),
  put:    (url, body, options = {})  => apiRequest(url, { ...options, method: 'PUT',    body }),
  patch:  (url, body, options = {})  => apiRequest(url, { ...options, method: 'PATCH',  body }),
  delete: (url, options = {})        => apiRequest(url, { ...options, method: 'DELETE' }),

  // ─── آپلود فایل ─────────────────────────────────────────
  // جایگزین: app/api/orders/payment/upload/route.ts
  // formData یه شیء FormData هست که مستقیم از مرورگر ساخته می‌شه
  upload: (url, formData, options = {}) =>
    apiRequest(url, { ...options, method: 'POST', body: formData }),
};