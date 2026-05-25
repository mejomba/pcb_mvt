/**
 * داده‌های ورودی نمونه:
 * {
 *   title: string,
 *   price: string,
 *   buildTime: string,
 *   items: string[],
 *   image: string,
 *   isFeatured: boolean
 * }
 */
function createPcbCard(data) {
  // ویژگی‌های شرطی
  const featuredClass = data.isFeatured ? 'border-warning featured-card' : '';
  const buttonClass = data.isFeatured ? 'btn-warning' : 'btn-primary';
  const badgeHtml = data.isFeatured
    ? '<span class="badge badge-warning position-absolute" style="top: 0.5rem; right: 0.5rem;">Limited Time Offer</span>'
    : '';

  // ساخت لیست ویژگی‌ها
  let itemsHtml = '';
  $.each(data.items, function (i, item) {
    itemsHtml += `<li>${item}</li>`;
  });

  // ساخت کارت با jQuery (امن‌تر و راحت‌تر برای binding بعدی)
  const $card = $(`
    <div class="card mb-3 shadow-sm position-relative ${featuredClass}">
      <img src="${data.image}" class="card-img-top" alt="${data.title}" style="height: 8rem; object-fit: cover;">
      <div class="card-body">
        <h5 class="card-title">${data.title}</h5>
        <p class="card-text small text-muted">
          From <span class="text-warning font-weight-bold">${data.price}</span> /5pcs | Build Time: ${data.buildTime}
        </p>
        <ul class="pl-3 small text-muted" style="list-style-type: disc;">
          ${itemsHtml}
        </ul>
      </div>
      <div class="card-footer bg-white border-top-0 d-flex justify-content-between align-items-center">
        <button class="btn btn-sm ${buttonClass}">Quote Now</button>
        <a href="#" class="text-muted small">Learn More &gt;</a>
      </div>
      ${badgeHtml}
    </div>
  `);

  // می‌توانی event listenerها را همین‌جا اضافه کنی
  $card.find('.btn').on('click', function () {
    // رویداد کلیک دکمه Quote Now
    console.log('Quote requested for:', data.title);
  });

  $card.find('a').on('click', function (e) {
    e.preventDefault();
    console.log('Learn more about:', data.title);
  });

  return $card;
}
