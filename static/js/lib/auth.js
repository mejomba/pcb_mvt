// === js/lib/auth.js ===
// وابستگی‌ها: api.js, token.js باید قبلاً لود شده باشن

// ─── Validation ───────────────────────────────────────────────
function validatePhone(phone) {
  return /^09\d{9}$/.test(phone);
}

// ─── Django Error Parser ──────────────────────────────────────
// منطق اصلی از actions/auth.ts حفظ شده
function parseDjangoError(errorData) {
  if (!errorData) return 'خطای ناشناخته‌ای رخ داد.';

  if (errorData.detail) return errorData.detail;

  if (typeof errorData === 'object' && !Array.isArray(errorData)) {
    const firstKey = Object.keys(errorData)[0];
    const firstError = errorData[firstKey];
    if (Array.isArray(firstError))      return firstError[0];
    if (typeof firstError === 'string') return firstError;
  }

  return 'در پردازش درخواست خطایی رخ داد.';
}

// ─── Send OTP ────────────────────────────────────────────────
// جایگزین: sendOtpAction در actions/auth.ts
async function sendOtpAction(phone) {
  if (!validatePhone(phone)) {
    return { error: 'شماره موبایل معتبر نیست.' };
  }

  try {
    // اول phone-check، بعد otp/send (ترتیب اصلی حفظ شد)
    const phoneCheckData = await api.post('/api/v1/auth/phone-check/', { phone, method: 'otp' });
    await api.post('/api/v1/auth/otp/send/', { phone });

    return { success: true, next_step: phoneCheckData.next_step };

  } catch (err) {
    if (err.data)   return { error: parseDjangoError(err.data) };
    if (err.status === 0) return { error: 'ارتباط با سرور برقرار نشد.' };
    return { error: 'خطایی رخ داد.' };
  }
}

// ─── Verify OTP ──────────────────────────────────────────────
// جایگزین: verifyOtpAction در actions/auth.ts
async function verifyOtpAction(phone, code, next_step) {
  const endpoint =
    next_step === 'register' ? '/api/v1/auth/otp/verify' : '/api/v1/auth/otp/verify/';

  try {
    const data = await api.post(endpoint, { phone, code });

    if (data.access && data.refresh) {
      // توکن‌ها در کوکی معمولی (قابل دسترس از مرورگر) ذخیره می‌شن
      saveTokens(data.access, data.refresh);
    }

    return { success: true };

  } catch (err) {
    if (err.data)   return { error: parseDjangoError(err.data) };
    if (err.status === 0) return { error: 'ارتباط با سرور برقرار نشد. لطفاً دوباره تلاش کنید.' };
    return { error: err.message || 'خطای ناشناخته‌ای رخ داد.' };
  }
}

// ─── Password Login ──────────────────────────────────────────
// جایگزین: passwordLoginAction در actions/auth.ts
async function passwordLoginAction(phone, password) {
  try {
    const data = await api.post('/api/v1/auth/login/', { phone, password });

    if (data.access && data.refresh) {
      saveTokens(data.access, data.refresh);
    }

    return { success: true };

  } catch (err) {
    if (err.data)   return { error: parseDjangoError(err.data) };
    if (err.status === 0) return { error: 'ارتباط با سرور برقرار نشد. لطفاً دوباره تلاش کنید.' };
    return { error: err.message || 'خطای ناشناخته‌ای رخ داد.' };
  }
}

// ─── Logout ──────────────────────────────────────────────────
// جایگزین: logout در actions/auth.ts
async function logoutAction() {
  try {
    // به بک‌اند اطلاع بده (اختیاری — اگه endpoint داری)
    await api.post('/auth/logout/', {});
  } catch (_) {
    // حتی اگه بک‌اند خطا داد، کوکی‌ها رو پاک می‌کنیم
  } finally {
    clearTokens();
    window.location.href = '/';
  }
}

// ─── Phone Check (مستقل) ─────────────────────────────────────
// جایگزین: phoneCheck در lib/api/auth.ts
async function phoneCheck(phone, method) {
  return api.post('/auth/phone-check/', { phone, method });
}