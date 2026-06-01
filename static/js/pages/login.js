// === static/js/pages/login.js ===
// وابستگی‌ها: api.js, token.js, auth.js باید قبلاً در base.html لود شده باشن

(function () {

  // ─── URL Param Helper ──────────────────────────────
  function getParam(name) {
    return new URLSearchParams(window.location.search).get(name);
  }

  const mode  = getParam('mode') || 'otp';
  const step  = getParam('step');
  const phone = getParam('phone');

  // ─── Tab Highlighting ──────────────────────────────
  const tabOtp      = document.getElementById('tab-otp');
  const tabPassword = document.getElementById('tab-password');

  if (mode === 'password') {
    tabPassword && tabPassword.classList.add('active');
  } else {
    tabOtp && tabOtp.classList.add('active');
  }

  // ─── Section Visibility ────────────────────────────
  function showSection(id) {
    ['phone-section', 'otp-section', 'password-section'].forEach(function (s) {
      const el = document.getElementById(s);
      if (el) el.style.display = (s === id) ? 'block' : 'none';
    });
  }

  if (mode === 'password') {
    showSection('password-section');
  } else if (step && phone) {
    showSection('otp-section');
    // مقادیر hidden رو از URL پر کن
    const hiddenPhone = document.getElementById('otp-phone-hidden');
    const hiddenStep  = document.getElementById('otp-step-hidden');
    if (hiddenPhone) hiddenPhone.value = phone;
    if (hiddenStep)  hiddenStep.value  = step;
  } else {
    showSection('phone-section');
  }

  // ─── Error Helpers ─────────────────────────────────
  function showError(formId, message) {
    const el = document.getElementById(formId + '-error');
    if (!el) return;
    el.textContent = message;
    el.style.display = 'block';
  }

  function hideError(formId) {
    const el = document.getElementById(formId + '-error');
    if (el) el.style.display = 'none';
  }

  function setInputError(input, hasError) {
    if (!input) return;
    input.classList.toggle('input-error', hasError);
  }

  function setLoading(btn, loading, originalText) {
    btn.disabled = loading;
    btn.textContent = loading ? 'لطفاً صبر کنید...' : originalText;
  }

  // ─── ① Phone Form ──────────────────────────────────
  const phoneForm = document.getElementById('phone-form');
  if (phoneForm) {
    phoneForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      hideError('phone-form');

      const phoneInput = phoneForm.querySelector('[name="phone"]');
      const submitBtn  = document.getElementById('phone-submit-btn');
      const phoneVal   = phoneInput.value.trim();

      setInputError(phoneInput, false);
      setLoading(submitBtn, true, 'دریافت کد');

      const result = await sendOtpAction(phoneVal);

      setLoading(submitBtn, false, 'دریافت کد');

      if (result.error) {
        showError('phone-form', result.error);
        setInputError(phoneInput, true);
        return;
      }

      // موفق → ریدایرکت به مرحله OTP
      const params = new URLSearchParams({
        mode: 'otp',
        phone: phoneVal,
        step: result.next_step,
      });
      window.location.href = '/api/v1/auth/template/otp/verify/?' + params.toString();
    });
  }

  // ─── ② OTP Form ────────────────────────────────────
  const otpForm = document.getElementById('otp-form');
  if (otpForm) {

    // تایمر شمارش معکوس
    let timerSeconds = 120;
    let timerInterval = null;
    const timerText = document.getElementById('otp-timer-text');
    const secondsEl = document.getElementById('otp-seconds');
    const resendBtn = document.getElementById('otp-resend-btn');

    function startTimer() {
      timerSeconds = 120;
      if (secondsEl)  secondsEl.textContent = timerSeconds;
      if (timerText)  timerText.style.display = 'inline';
      if (resendBtn)  resendBtn.style.display = 'none';

      clearInterval(timerInterval);
      timerInterval = setInterval(function () {
        timerSeconds--;
        if (secondsEl) secondsEl.textContent = timerSeconds;
        if (timerSeconds <= 0) {
          clearInterval(timerInterval);
          if (timerText) timerText.style.display = 'none';
          if (resendBtn) resendBtn.style.display = 'inline';
        }
      }, 1000);
    }

    startTimer();

    // ارسال مجدد کد
    if (resendBtn) {
      resendBtn.addEventListener('click', async function () {
        const currentPhone = document.getElementById('otp-phone-hidden')?.value || phone;
        try {
          await api.post('/api/v1/auth/resend-otp/', { phone: currentPhone });
          startTimer();
        } catch (err) {
          showError('otp-form', 'خطا در ارسال مجدد کد. لطفاً دوباره تلاش کنید.');
        }
      });
    }

    // submit فرم OTP
    otpForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      hideError('otp-form');

      const codeInput  = document.getElementById('otp-code-input');
      const submitBtn  = document.getElementById('otp-submit-btn');
      const phoneVal   = document.getElementById('otp-phone-hidden')?.value || phone;
      const nextStep   = document.getElementById('otp-step-hidden')?.value  || step;
      const code       = codeInput.value.trim();

      setInputError(codeInput, false);
      setLoading(submitBtn, true, 'تأیید');

      const result = await verifyOtpAction(phoneVal, code, nextStep);

      setLoading(submitBtn, false, 'تأیید');

      if (result.error) {
        showError('otp-form', result.error);
        setInputError(codeInput, true);
        return;
      }

      // موفق → پروفایل
      const nextUrl = getParam('next') || '/profile/';
      window.location.href = nextUrl;
    });
  }

  // ─── ③ Password Form ───────────────────────────────
  const passwordForm = document.getElementById('password-form');
  if (passwordForm) {
    passwordForm.addEventListener('submit', async function (e) {
      e.preventDefault();
      hideError('password-form');

      const phoneInput = document.getElementById('pwd-phone');
      const pwdInput   = document.getElementById('pwd-password');
      const submitBtn  = document.getElementById('password-submit-btn');

      setInputError(phoneInput, false);
      setInputError(pwdInput, false);
      setLoading(submitBtn, true, 'ورود');

      const result = await passwordLoginAction(
        phoneInput.value.trim(),
        pwdInput.value
      );

      setLoading(submitBtn, false, 'ورود');

      if (result.error) {
        showError('password-form', result.error);
        setInputError(phoneInput, true);
        return;
      }

      // موفق → next param یا پروفایل
      const nextUrl = getParam('next') || '/profile/';
      window.location.href = nextUrl;
    });
  }

})();