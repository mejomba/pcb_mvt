// === static/js/pages/help.js ===
// وابستگی: api.js, sidebar.js

(function () {

  var layout    = document.getElementById('help-layout');
  var slug      = layout && layout.dataset.slug;
  var pageType  = layout && layout.dataset.pageType; // 'category' | 'post'
  var mainEl    = document.getElementById('help-main-content');

  // ─── Loading / Error helpers ────────────────────────
  function showLoading() {
    if (!mainEl) return;
    mainEl.innerHTML = `
      <div class="help-loading">
        <div class="spinner-ring"></div>
        <span>در حال بارگذاری...</span>
      </div>`;
  }

  function showError(msg) {
    if (!mainEl) return;
    mainEl.innerHTML = `
      <div class="help-empty">
        <i class="bi bi-exclamation-circle help-empty-icon"></i>
        <p>${msg || 'خطا در بارگذاری محتوا.'}</p>
      </div>`;
  }

  // ─── Breadcrumb ──────────────────────────────────────
  function breadcrumbHTML(crumbs) {
    if (!crumbs || !crumbs.length) return '';
    return `
      <nav class="breadcrumb" aria-label="مسیر">
        ${crumbs.map(function (c, i) {
          return `
            <span class="breadcrumb-item">
              <a href="#">${c}</a>
              ${i < crumbs.length - 1 ? '<span class="breadcrumb-sep">/</span>' : ''}
            </span>`;
        }).join('')}
      </nav>`;
  }

  // ─── Render: Category Page ───────────────────────────
  // جایگزین MainContent.tsx — نمایش لیست مقالات یک دسته
  function renderCategoryContent(content) {
    if (!mainEl) return;
    if (!content || !content.length) {
      mainEl.innerHTML = '<div class="help-empty"><p>محتوایی یافت نشد.</p></div>';
      return;
    }

    var categoryName = content[0].category_name || '';
    var breadcrumbs  = content[0].breadcrumb || [];

    var articlesHTML = content.map(function (article) {
      return `
        <div class="help-article-item">
          <a href="/help/post/${article.slug}/" class="help-article-link">
            ${article.title}
          </a>
        </div>`;
    }).join('');

    mainEl.innerHTML = `
      ${breadcrumbHTML(breadcrumbs)}
      <h1 class="help-page-title">${categoryName}</h1>
      <div class="help-articles-list">${articlesHTML}</div>
    `;
  }

  // ─── Render: Post Page ───────────────────────────────
  // جایگزین MainContentText.tsx — نمایش محتوای یک مقاله
  function renderPostContent(content) {
    if (!mainEl) return;
    if (!content) {
      mainEl.innerHTML = '<div class="help-empty"></div>';
      return;
    }

    var breadcrumbs = content.breadcrumb || [];

    mainEl.innerHTML = `
      ${breadcrumbHTML(breadcrumbs)}
      <h1 class="help-page-title">${content.title || ''}</h1>
      <div class="help-article-body">${content.guid_content || content.content || ''}</div>
    `;
  }

  // ─── Main: fetch + render ────────────────────────────
  async function init() {
    if (!slug) { showError('مسیر نامعتبر است.'); return; }

    showLoading();

    try {
      // هر دو درخواست را موازی ارسال می‌کنیم
      var menuPromise    = api.get('/blog/category/list/');
      var contentPromise = pageType === 'post'
        ? api.get('/blog/guid/' + slug + '/')
        : api.get('/blog/category/list/slug/' + slug + '/');

      var results = await Promise.all([menuPromise, contentPromise]);
      var menuData    = results[0] && results[0].results ? results[0].results : [];
      var contentData = results[1];

      if (pageType === 'main') {
        // محتوا از قبل در HTML هست — فقط sidebar رندر کن
        if (typeof renderHelpSidebar === 'function') {
          renderHelpSidebar('help-sidebar-container', menuData, '');
        }
        return; // بقیه کد رندر محتوا اجرا نشه
      }
      
      // ─── Sidebar
      if (typeof renderHelpSidebar === 'function') {
        renderHelpSidebar('help-sidebar-container', menuData, slug);
      }

      // ─── Main Content
      if (pageType === 'post') {
        renderPostContent(contentData);
      } else {
        // content ممکنه array یا single object باشه بسته به API
        var contentArr = Array.isArray(contentData)
          ? contentData
          : (contentData && contentData.results ? contentData.results : [contentData]);
        renderCategoryContent(contentArr);
      }

    } catch (err) {
      console.error('Help page error:', err);
      showError('خطا در بارگذاری. لطفاً دوباره تلاش کنید.');
    }
  }

  init();

})();