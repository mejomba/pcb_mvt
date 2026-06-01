// === static/js/components/navbar.js ===

(function () {

  // ─── Search API endpoint ─────────────────────────
  // ⚠️ آدرس API جستجو رو اینجا تنظیم کن
  var SEARCH_API = '/search/';   // مثال: '/blog/posts/?search='

  var MENU_ITEMS = [
    { href: '/profile/',  icon: 'bi-clipboard-check', label: 'Order History' },
    { href: '/projects/', icon: 'bi-folder',           label: 'My Projects'   },
    { href: '/parts/',    icon: 'bi-gear',             label: 'Parts Manager' },
    { href: '/messages/', icon: 'bi-envelope',         label: 'My Messages'   },
    { href: '/coupons/',  icon: 'bi-ticket',           label: 'My Coupons'    },
    { href: '/account/',  icon: 'bi-person',           label: 'My Account'    },
  ];

  // ─── Debounce ─────────────────────────────────────
  function debounce(fn, ms) {
    var t;
    return function () {
      var ctx = this, args = arguments;
      clearTimeout(t);
      t = setTimeout(function () { fn.apply(ctx, args); }, ms);
    };
  }

  // ════════════════════════════════════════════════
  // SEARCH
  // ════════════════════════════════════════════════
  var searchOverlay = document.getElementById('search-overlay');
  var searchInput   = document.getElementById('search-input');
  var searchResults = document.getElementById('search-results');
  var openBtn       = document.getElementById('search-open-btn');
  var closeBtn      = document.getElementById('search-close-btn');

  function openSearch() {
    if (!searchOverlay) return;
    searchOverlay.style.display = 'flex';
    setTimeout(function () { searchInput && searchInput.focus(); }, 50);
  }

  function closeSearch() {
    if (!searchOverlay) return;
    searchOverlay.style.display = 'none';
    if (searchInput)  searchInput.value  = '';
    if (searchResults) {
      searchResults.innerHTML  = '';
      searchResults.style.display = 'none';
    }
  }

  openBtn  && openBtn.addEventListener('click',  openSearch);
  closeBtn && closeBtn.addEventListener('click',  closeSearch);

  // بستن با Escape
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeSearch();
  });

  // بستن با کلیک روی overlay
  searchOverlay && searchOverlay.addEventListener('click', function (e) {
    if (e.target === searchOverlay) closeSearch();
  });

  // ─── Live Search ──────────────────────────────────
  function renderResults(items) {
    if (!searchResults) return;

    if (!items || items.length === 0) {
      searchResults.innerHTML = '<div class="pcb-search-empty">نتیجه‌ای یافت نشد.</div>';
      searchResults.style.display = 'block';
      return;
    }

    var html = items.map(function (item) {
      // سازگار با ساختارهای مختلف API
      var title    = item.title    || item.name        || item.label  || '—';
      var subtitle = item.excerpt  || item.description || item.category_name || '';
      var url      = item.url      || item.slug
                       ? (item.slug ? '/blog/posts/' + item.slug + '/' : '#')
                       : '#';
      var icon     = item.type === 'product' ? 'bi-cpu' : 'bi-file-text';

      return `
        <a href="${url}" class="pcb-search-result-item">
          <div class="pcb-search-result-icon">
            <i class="bi ${icon}"></i>
          </div>
          <div>
            <div class="pcb-search-result-title">${title}</div>
            ${subtitle ? `<div class="pcb-search-result-subtitle">${subtitle}</div>` : ''}
          </div>
        </a>`;
    }).join('');

    searchResults.innerHTML     = html;
    searchResults.style.display = 'block';
  }

  function showSearchLoading() {
    if (!searchResults) return;
    searchResults.innerHTML     = '<div class="pcb-search-loading"><i class="bi bi-arrow-repeat"></i> در حال جستجو...</div>';
    searchResults.style.display = 'block';
  }

  var doSearch = debounce(async function (term) {
    if (!term || term.length < 2) {
      if (searchResults) searchResults.style.display = 'none';
      return;
    }

    showSearchLoading();

    try {
      var data = await api.get(SEARCH_API + '?q=' + encodeURIComponent(term));
      // پشتیبانی از پاسخ paginated و ساده
      var items = data.results || data || [];
      renderResults(Array.isArray(items) ? items : []);
    } catch (err) {
      if (searchResults) {
        searchResults.innerHTML     = '<div class="pcb-search-empty">خطا در جستجو. دوباره تلاش کنید.</div>';
        searchResults.style.display = 'block';
      }
      console.error('Search error:', err);
    }
  }, 350);

  searchInput && searchInput.addEventListener('input', function () {
    doSearch(this.value.trim());
  });

  // ════════════════════════════════════════════════
  // MOBILE DRAWER
  // ════════════════════════════════════════════════
  var drawer      = document.getElementById('mobile-drawer');
  var overlay     = document.getElementById('mobile-overlay');
  var mobileToggle= document.getElementById('mobile-toggle');
  var mobileClose = document.getElementById('mobile-close-btn');

  function openDrawer()  {
    drawer  && drawer.classList.add('open');
    overlay && overlay.classList.add('open');
    document.body.style.overflow = 'hidden';
  }
  function closeDrawer() {
    drawer  && drawer.classList.remove('open');
    overlay && overlay.classList.remove('open');
    document.body.style.overflow = '';
  }

  mobileToggle && mobileToggle.addEventListener('click', openDrawer);
  mobileClose  && mobileClose.addEventListener('click',  closeDrawer);
  overlay      && overlay.addEventListener('click',      closeDrawer);

  // ════════════════════════════════════════════════
  // SIGN IN MENU
  // ════════════════════════════════════════════════
  var signinWrapper = document.getElementById('signin-menu-wrapper');

  function menuListHTML(loggedIn) {
    return MENU_ITEMS.map(function (item) {
      if (loggedIn) {
        return `
          <a href="${item.href}" class="pcb-signin-item">
            <i class="bi ${item.icon}"></i>
            <span>${item.label}</span>
          </a>`;
      }
      return `
        <div class="pcb-signin-item pcb-signin-item-disabled">
          <i class="bi ${item.icon}"></i>
          <span>${item.label}</span>
        </div>`;
    }).join('');
  }

  function renderSigninMenu() {
    if (!signinWrapper) return;

    var isLoggedIn = !!getCookie('access');

    if (isLoggedIn) {
      signinWrapper.innerHTML = `
        <div class="pcb-signin-group">
          <button type="button" class="pcb-signin-trigger" id="signin-trigger">
            <i class="bi bi-person-circle me-1"></i>Profile
            <i class="bi bi-chevron-down" style="font-size:.7rem;margin-right:.15rem;"></i>
          </button>
          <div class="pcb-signin-dropdown" id="signin-dropdown">
            <div class="pcb-signin-dropdown-inner">
              <button type="button" class="pcb-signin-logout-btn" id="navbar-logout-btn">
                <i class="bi bi-box-arrow-right me-1"></i>Logout
              </button>
              <hr class="pcb-signin-divider" />
              ${menuListHTML(true)}
            </div>
          </div>
        </div>`;

      document.getElementById('navbar-logout-btn').addEventListener('click', logoutAction);

    } else {
      signinWrapper.innerHTML = `
        <div class="pcb-signin-group">
          <button type="button" class="pcb-signin-trigger" id="signin-trigger">
            Sign In
            <i class="bi bi-chevron-down" style="font-size:.7rem;margin-right:.15rem;"></i>
          </button>
          <div class="pcb-signin-dropdown" id="signin-dropdown">
            <div class="pcb-signin-dropdown-inner">
              <a href="/api/v1/auth/template/otp/" class="pcb-signin-login-btn">Sign In</a>
              <p class="pcb-new-customer">
                New Customer? <a href="/api/v1/auth/template/otp/">Start Here</a>
              </p>
              <div class="pcb-signin-blur-wrapper">
                <div class="pcb-signin-blur-overlay"></div>
                ${menuListHTML(false)}
              </div>
            </div>
          </div>
        </div>`;
    }

    // Toggle dropdown
    var trigger  = document.getElementById('signin-trigger');
    var dropdown = document.getElementById('signin-dropdown');

    trigger && trigger.addEventListener('click', function (e) {
      e.stopPropagation();
      dropdown && dropdown.classList.toggle('open');
    });

    document.addEventListener('click', function () {
      dropdown && dropdown.classList.remove('open');
    });
  }

  // ─── Init ─────────────────────────────────────────
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', renderSigninMenu);
  } else {
    renderSigninMenu();
  }

})();