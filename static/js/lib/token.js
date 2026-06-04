// === js/lib/token.js ===
// توجه: api.js باید قبل از این فایل لود شده باشد (getCookie, setCookie)

const TOKEN_CONFIG = {
  accessKey:  'access',
  refreshKey: 'refresh',
  days: 1,
};

function saveTokens(access, refresh) {
  setCookie(TOKEN_CONFIG.accessKey,  access,  TOKEN_CONFIG.days);
  if (refresh) {
    setCookie(TOKEN_CONFIG.refreshKey, refresh, 7); // refresh عمر بیشتری داره
  }
}

function getAccessToken() {
  return getCookie(TOKEN_CONFIG.accessKey);
}

function getRefreshToken() {
  return getCookie(TOKEN_CONFIG.refreshKey);
}

function clearTokens() {
  const past = 'Thu, 01 Jan 1970 00:00:00 UTC';
  document.cookie = `${TOKEN_CONFIG.accessKey}=; expires=${past}; path=/`;
  document.cookie = `${TOKEN_CONFIG.refreshKey}=; expires=${past}; path=/`;
}