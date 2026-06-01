// === static/js/components/fullscreen-slider.js ===
// جایگزین: FullScreenSlider.tsx (Swiper حذف شد — vanilla JS)

(function () {

  var IMAGES = [
    { src: '/static/images/s1.png', alt: 'Image 1' },
    { src: '/static/images/s2.png', alt: 'Image 2' },
    { src: '/static/images/s3.png', alt: 'Image 3' },
  ];

  var AUTOPLAY_DELAY = 4000;

  var currentIndex = 0;
  var autoplayTimer = null;
  var slides = [];
  var dots   = [];

  // ─── Go To Slide ──────────────────────────────────
  function goTo(index) {
    slides[currentIndex].classList.remove('slider-active');
    dots[currentIndex].classList.remove('dot-active');

    currentIndex = ((index % IMAGES.length) + IMAGES.length) % IMAGES.length;

    slides[currentIndex].classList.add('slider-active');
    dots[currentIndex].classList.add('dot-active');
  }

  // ─── Autoplay ─────────────────────────────────────
  function startAutoplay() {
    stopAutoplay();
    autoplayTimer = setInterval(function () {
      goTo(currentIndex + 1);
    }, AUTOPLAY_DELAY);
  }

  function stopAutoplay() {
    if (autoplayTimer) clearInterval(autoplayTimer);
  }

  // ─── Build Slider HTML ─────────────────────────────
  function buildSlider(container) {
    var slidesHTML = IMAGES.map(function (img, i) {
      return `
        <div class="slider-slide ${i === 0 ? 'slider-active' : ''}">
          <div class="slider-image-wrapper">
            <img src="${img.src}" alt="${img.alt}" class="slider-img" loading="${i === 0 ? 'eager' : 'lazy'}" />
          </div>
        </div>`;
    }).join('');

    var dotsHTML = IMAGES.map(function (_, i) {
      return `<button class="slider-dot ${i === 0 ? 'dot-active' : ''}"
                      data-index="${i}"
                      aria-label="اسلاید ${i + 1}"></button>`;
    }).join('');

    container.innerHTML = `
      <div class="slider-inner">
        <div class="slider-track">${slidesHTML}</div>

        <!-- Prev -->
        <button class="slider-nav-btn slider-prev" id="slider-prev" aria-label="قبلی">
          <i class="bi bi-chevron-right"></i>
        </button>

        <!-- Next -->
        <button class="slider-nav-btn slider-next" id="slider-next" aria-label="بعدی">
          <i class="bi bi-chevron-left"></i>
        </button>

        <!-- Pagination Dots -->
        <div class="slider-pagination">${dotsHTML}</div>
      </div>
    `;

    // Cache elements
    slides = Array.from(container.querySelectorAll('.slider-slide'));
    dots   = Array.from(container.querySelectorAll('.slider-dot'));

    // Events — navigation
    var prevBtn = container.querySelector('#slider-prev');
    var nextBtn = container.querySelector('#slider-next');

    prevBtn && prevBtn.addEventListener('click', function () {
      goTo(currentIndex - 1);
      startAutoplay(); // ریست تایمر
    });

    nextBtn && nextBtn.addEventListener('click', function () {
      goTo(currentIndex + 1);
      startAutoplay();
    });

    // Events — dots
    dots.forEach(function (dot) {
      dot.addEventListener('click', function () {
        goTo(parseInt(this.dataset.index, 10));
        startAutoplay();
      });
    });

    // Pause on hover
    container.addEventListener('mouseenter', stopAutoplay);
    container.addEventListener('mouseleave', startAutoplay);

    // Keyboard navigation
    document.addEventListener('keydown', function (e) {
      if (e.key === 'ArrowLeft')  { goTo(currentIndex + 1); startAutoplay(); }
      if (e.key === 'ArrowRight') { goTo(currentIndex - 1); startAutoplay(); }
    });

    startAutoplay();
  }

  // ─── Public Init ──────────────────────────────────
  window.initFullScreenSlider = function (containerId) {
    var el = document.getElementById(containerId);
    if (el) buildSlider(el);
  };

})();