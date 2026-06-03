// === static/js/components/help/sidebar.js ===

(function () {

  function debounce(fn, delay) {
    let timer;
    return function (...args) {
      clearTimeout(timer);
      timer = setTimeout(() => fn.apply(this, args), delay);
    };
  }

  // ─── پیدا کردن آیتم‌های active و والدینشون ──────────
  function findActiveIds(items, targetSlug, parents, result) {
    for (var i = 0; i < items.length; i++) {
      var item = items[i];
      if (item.slug === targetSlug) {
        parents.forEach(function (p) { result.add(String(p)); });
        result.add(String(item.id));
        return true;
      }
      if (item.child && item.child.length > 0) {
        if (findActiveIds(item.child, targetSlug, parents.concat([item.id]), result)) {
          return true;
        }
      }
    }
    return false;
  }

  // ─── ساخت درخت منو (بازگشتی) ─────────────────────────
  function buildMenuTree(items, level, activePath, openItems) {
    var paddingRight = (level * 16 + 16) + 'px';

    var lis = items.map(function (item) {
      var isOpen     = openItems.has(String(item.id));
      var isActive   = activePath === item.slug;
      var hasChildren = item.child && item.child.length > 0;

      var itemClass = 'menu-item' + (isActive ? ' menu-item-active' : '');
      var href      = hasChildren ? 'javascript:void(0)' : '/api/v1/pcb/help/' + item.slug + '/';
      var chevron   = hasChildren
        ? `<span class="menu-chevron${isOpen ? ' open' : ''}" aria-hidden="true">
             <i class="bi bi-chevron-right"></i>
           </span>`
        : '';

      var childrenHTML = (isOpen && hasChildren)
        ? buildMenuTree(item.child, level + 1, activePath, openItems)
        : (hasChildren
          ? `<div class="menu-children" style="display:none;">${buildMenuTree(item.child, level + 1, activePath, openItems)}</div>`
          : '');

      // اگه hasChildren هست ولی بسته‌ست، کودکان پنهان render می‌کنیم
      var childWrapper = '';
      if (hasChildren) {
        var childContent = buildMenuTree(item.child, level + 1, activePath, openItems);
        childWrapper = `<div class="menu-children" style="${isOpen ? '' : 'display:none;'}">${childContent}</div>`;
      }

      return `
        <li>
          <div class="${itemClass}"
               style="padding-right: ${paddingRight}"
               data-item-id="${item.id}"
               data-has-children="${hasChildren}">
            <a href="${href}" class="menu-item-link"
               ${hasChildren ? 'data-toggle="true"' : ''}>
              ${item.title}
            </a>
            ${chevron}
          </div>
          ${childWrapper}
        </li>
      `;
    }).join('');

    return `<ul class="menu-list">${lis}</ul>`;
  }

  // ─── Render Sidebar ───────────────────────────────────
  function renderHelpSidebar(containerId, menuItems, activePath) {
    var container = document.getElementById(containerId);
    if (!container) return;

    // پیدا کردن آیتم‌های باید باز باشن
    var openItems = new Set();
    findActiveIds(menuItems, activePath, [], openItems);

    container.innerHTML = `
      <div class="sidebar-wrapper">

        <!-- نوار collapse -->
        <div class="sidebar-toggle-strip" id="sidebar-toggle-strip" title="باز/بستن منو">
          <i class="bi bi-chevron-right" id="sidebar-toggle-icon"></i>
        </div>

        <aside class="help-sidebar sidebar-scroll" id="help-sidebar">
          <div class="sidebar-content" id="sidebar-content">
            <h2 class="sidebar-title">مرکز راهنما</h2>

            <div class="sidebar-search">
              <i class="bi bi-search sidebar-search-icon"></i>
              <input
                type="text"
                placeholder="جستجو..."
                class="sidebar-search-input"
                id="sidebar-search-input"
              />
            </div>

            <nav id="sidebar-menu-nav">
              ${buildMenuTree(menuItems, 0, activePath, openItems)}
            </nav>
          </div>
        </aside>

      </div>
    `;

    _attachSidebarEvents(container, openItems);
  }

  // ─── رویدادهای Sidebar ────────────────────────────────
  function _attachSidebarEvents(container, openItems) {
    var sidebar     = container.querySelector('#help-sidebar');
    var content     = container.querySelector('#sidebar-content');
    var toggleStrip = container.querySelector('#sidebar-toggle-strip');
    var toggleIcon  = container.querySelector('#sidebar-toggle-icon');
    var collapsed   = false;

    // Collapse / Expand
    toggleStrip.addEventListener('click', function () {
      collapsed = !collapsed;
      sidebar.classList.toggle('collapsed', collapsed);
      content.style.opacity        = collapsed ? '0' : '1';
      content.style.pointerEvents  = collapsed ? 'none' : '';
      toggleIcon.className = collapsed
        ? 'bi bi-chevron-right'
        : 'bi bi-chevron-left';
    });

    // Toggle tree items با event delegation
    container.addEventListener('click', function (e) {
      var link = e.target.closest('[data-toggle="true"]');
      if (!link) return;
      e.preventDefault();

      var menuItemDiv = link.closest('.menu-item[data-has-children="true"]');
      if (!menuItemDiv) return;

      var itemId     = menuItemDiv.dataset.itemId;
      var chevron    = menuItemDiv.querySelector('.menu-chevron');
      var childrenEl = menuItemDiv.nextElementSibling; // div.menu-children

      if (openItems.has(itemId)) {
        openItems.delete(itemId);
        if (chevron)    chevron.classList.remove('open');
        if (childrenEl) childrenEl.style.display = 'none';
      } else {
        openItems.add(itemId);
        if (chevron)    chevron.classList.add('open');
        if (childrenEl) childrenEl.style.display = 'block';
      }
    });

    // Sidebar search — فیلتر لینک‌ها
    var searchInput = container.querySelector('#sidebar-search-input');
    if (searchInput) {
      searchInput.addEventListener('input', debounce(function () {
        var term = this.value.trim().toLowerCase();
        container.querySelectorAll('.menu-list li').forEach(function (li) {
          var link = li.querySelector('.menu-item-link');
          var text = link ? link.textContent.toLowerCase() : '';
          li.style.display = (!term || text.includes(term)) ? '' : 'none';
        });
      }, 300));
    }
  }

  // ─── Public API ──────────────────────────────────────
  window.renderHelpSidebar = renderHelpSidebar;

})();