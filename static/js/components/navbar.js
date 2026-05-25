// === static/js/components/navbar.js ===
// وابستگی: token.js, auth.js باید قبلاً لود شده باشن

(function () {

  // ─── Mobile Drawer ──────────────────────────────────
  const hamburger    = document.getElementById('navbar-hamburger');
  const drawer       = document.getElementById('mobile-drawer');
  const overlay      = document.getElementById('mobile-overlay');
  const drawerClose  = document.getElementById('mobile-drawer-close');

  function openDrawer() {
    drawer  && drawer.classList.add('open');
    overlay && overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }

  function closeDrawer() {
    drawer  && drawer.classList.remove('open');
    overlay && overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  hamburger   && hamburger.addEventListener('click', openDrawer);
  drawerClose && drawerClose.addEventListener('click', closeDrawer);
  overlay     && overlay.addEventListener('click', closeDrawer);

  // ─── Auth State → SignIn Menu ────────────────────────
  // جایگزین SignInMenu component — بر اساس وجود کوکی access
  const signinWrapper = document.getElementById('signin-menu-wrapper');

  function renderSigninMenu() {
    if (!signinWrapper) return;

    const isLoggedIn = !!getCookie('access');

    if (isLoggedIn) {
      // منوی کاربر لاگین‌شده
      signinWrapper.innerHTML = `
        <div class="user-menu">
          <button class="user-menu-trigger navbar-icon-btn" id="user-menu-trigger" aria-label="منوی کاربر">
            <i class="bi bi-person-circle"></i>
          </button>
          <div class="user-dropdown" id="user-dropdown" style="display:none;">
            <a href="/profile/" class="user-dropdown-item">
              <i class="bi bi-person"></i> پروفایل
            </a>
            <hr class="user-dropdown-divider" />
            <button class="user-dropdown-item user-dropdown-logout" id="logout-btn">
              <i class="bi bi-box-arrow-right"></i> خروج
            </button>
          </div>
        </div>
      `;

      // toggle dropdown
      const trigger  = document.getElementById('user-menu-trigger');
      const dropdown = document.getElementById('user-dropdown');

      trigger && trigger.addEventListener('click', function (e) {
        e.stopPropagation();
        dropdown.style.display =
          dropdown.style.display === 'none' ? 'block' : 'none';
      });

      // بستن با کلیک بیرون
      document.addEventListener('click', function () {
        if (dropdown) dropdown.style.display = 'none';
      });

      // logout
      const logoutBtn = document.getElementById('logout-btn');
      logoutBtn && logoutBtn.addEventListener('click', function () {
        logoutAction();
      });

    } else {
      // دکمه ورود
      signinWrapper.innerHTML = `
        <a href="/auth/login/" class="navbar-signin-btn">
          <i class="bi bi-person"></i> ورود
        </a>
      `;
    }
  }

  renderSigninMenu();

})();