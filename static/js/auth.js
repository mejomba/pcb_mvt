// main.js
function initCountdownTimer(options) {
  // options: {
  //   container: '#timer-container',   // عنصر حاوی تایمر
  //   startSeconds: 120,               // ثانیه شروع
  //   resendUrl: '/auth/resend-otp/',  // آدرس ارسال مجدد
  //   resendData: { phone: '09xx' },   // داده‌های اضافی برای POST
  // }

  var $container = $(options.container);
  var secondsLeft = options.startSeconds;
  var timerInterval;

  function updateDisplay() {
    var min = Math.floor(secondsLeft / 60);
    var sec = (secondsLeft % 60).toString().padStart(2, '0');
    var html = 'ارسال مجدد کد تا ' + min + ':' + sec + ' ثانیه دیگر';
    if (secondsLeft <= 0) {
      clearInterval(timerInterval);
      html = '<button type="button" class="btn btn-link text-indigo-600 p-0 resend-btn">ارسال مجدد کد</button>';
    }
    $container.html(html);
  }

  function startTimer() {
    clearInterval(timerInterval);
    secondsLeft = options.startSeconds;
    updateDisplay();
    if (secondsLeft > 0) {
      timerInterval = setInterval(function() {
        secondsLeft--;
        updateDisplay();
      }, 1000);
    }
  }

  startTimer();

  // کلیک روی دکمه ارسال مجدد (با delegation)
  $container.on('click', '.resend-btn', function(e) {
    e.preventDefault();
    $.ajax({
      url: options.resendUrl,
      method: 'POST',
      data: options.resendData,
      headers: { 'X-CSRFToken': getCsrfToken() } // اگر جنگو CSRF فعال دارد
    }).done(function() {
      // شروع دوباره تایمر
      startTimer();
    }).fail(function() {
      alert('خطا در ارسال مجدد کد');
    });
  });

  // تابع کمکی برای دریافت CSRF token (اگر نیاز داری)
  function getCsrfToken() {
    return $('input[name=csrfmiddlewaretoken]').val();
  }
}