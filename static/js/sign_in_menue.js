$(document).ready(function() {

  // ========== مدیریت وضعیت لاگین (مانند قبل) ==========
  function checkLoginStatus() {
    return document.cookie.indexOf('access=') !== -1;
  }

  function updateMenuUI() {
    var loggedIn = checkLoginStatus();
    var $btn = $('#userMenuButton');
    var $guestMenu = $('#guest-menu');
    var $userMenu = $('#user-menu');

    if (loggedIn) {
      $btn.html('Profile <i class="bi bi-chevron-down ml-1 small"></i>');
      $guestMenu.hide();
      $userMenu.show();
    } else {
      $btn.html('Sign in <i class="bi bi-chevron-down ml-1 small"></i>');
      $guestMenu.show();
      $userMenu.hide();
    }
  }

  updateMenuUI();

  // کلیک Logout
  $('#logout-btn').on('click', function() {
    $.ajax({
      url: '/api/v1/auth/logout/',
      method: 'POST',
      dataType: 'json'
    }).done(function() {
      document.cookie = 'access=; Max-Age=0; path=/';
      updateMenuUI();
      window.location.href = '/';
    }).fail(function() {
      alert('Logout failed. Please try again.');
    });
  });

  // ========== جستجو (اختیاری) ==========
  $('#search-toggle').on('click', function(e) {
    e.preventDefault();
    // می‌توانی یک مودال یا اینپوت جستجو باز کنی، یا ریدایرکت کنی
    window.location.href = '/search';
  });

  // ========== به‌روزرسانی نشانگر سبد خرید (در صورت نیاز داینامیک) ==========
  function updateCartCount(count) {
    $('.bi-cart + .badge').text(count);
  }
  // می‌توانی با AJAX تعداد آیتم‌های سبد را بگیری
  // $.getJSON('/api/cart-count', function(data) { updateCartCount(data.count); });

});