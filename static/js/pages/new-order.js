// === static/js/pages/new-order.js ===
// وابستگی: api.js, token.js
// پیاده‌سازی Accordion, FormField, RadioGroup به صورت inline

(function () {

  // ─── State ───────────────────────────────────────────
  var groups   = [];
  var formData = {};   // { attr_name: value }
  var gerberFile = null;

  // ─── DOM Refs ────────────────────────────────────────
  var loadingEl     = document.getElementById('new-order-loading');
  var errorEl       = document.getElementById('new-order-error');
  var errorMsgEl    = document.getElementById('new-order-error-msg');
  var formContainer = document.getElementById('new-order-form-container');
  var mainFields    = document.getElementById('main-group-fields');
  var accordionEl   = document.getElementById('accordion-groups');
  var submitBtn     = document.getElementById('submit-order-btn');
  var submitMsgEl   = document.getElementById('submit-message');
  var fileInput     = document.getElementById('gerber-file-input');
  var fileNameEl    = document.getElementById('file-name-display');
  var fileTextEl    = document.getElementById('file-upload-text');

  // ─── Helpers ─────────────────────────────────────────
  function showLoading(show) {
    if (loadingEl) loadingEl.style.display = show ? 'flex' : 'none';
  }

  function showError(msg) {
    showLoading(false);
    if (errorEl)    errorEl.style.display    = 'flex';
    if (errorMsgEl) errorMsgEl.textContent   = msg || 'خطا در دریافت اطلاعات.';
  }

  function showForm() {
    showLoading(false);
    if (formContainer) formContainer.style.display = 'block';
  }

  // ─── Initialize Form Data (مقادیر پیش‌فرض) ─────────
  function initializeFormData(grps) {
    var state = {};
    grps.forEach(function (group) {
      group.attributes.forEach(function (attr) {
        var defaultOpt = attr.options.find(function (o) { return o.is_default; });
        if (defaultOpt) state[attr.name] = defaultOpt.value;
      });
    });
    return state;
  }

  // ─── RadioGroup ───────────────────────────────────────
  // جایگزین RadioGroup.tsx
  function createRadioGroup(attr) {
    var wrapper = document.createElement('div');
    wrapper.className = 'radio-group';

    attr.options.forEach(function (opt) {
      var btn = document.createElement('button');
      btn.type      = 'button';
      btn.className = 'radio-btn' + (formData[attr.name] === opt.value ? ' selected' : '');
      btn.textContent   = opt.display_name;
      btn.dataset.value = opt.value;

      btn.addEventListener('click', function () {
        formData[attr.name] = opt.value;
        // آپدیت ظاهر همه دکمه‌های این گروه
        wrapper.querySelectorAll('.radio-btn').forEach(function (b) {
          b.classList.remove('selected');
        });
        this.classList.add('selected');
        // اگه text_input داره، value رو sync کن
        var textInput = wrapper.nextElementSibling;
        if (textInput && textInput.classList.contains('form-text-input')) {
          textInput.value = opt.value;
        }
      });

      wrapper.appendChild(btn);
    });

    return wrapper;
  }

  // ─── FormField ────────────────────────────────────────
  // جایگزین FormField.tsx — شامل label + tooltip + control
  function createFormField(attr) {
  var row = document.createElement('div');
  row.className = 'form-field-row';

  // ─── Label + GUID tooltip ──────────────────────────
  var labelCol = document.createElement('div');
  labelCol.className = 'form-field-label-col';

  var labelEl = document.createElement('label');
  labelEl.className   = 'form-field-label';
  labelEl.textContent = attr.display_name;
  labelCol.appendChild(labelEl);

  if (attr.guid && attr.guid.guid_content) {
    var tooltipWrapper = document.createElement('div');
    tooltipWrapper.className = 'guid-tooltip-wrapper';

    var tooltipBtn = document.createElement('button');
    tooltipBtn.type      = 'button';
    tooltipBtn.className  = 'guid-tooltip-btn';
    tooltipBtn.innerHTML  = '<i class="bi bi-question-circle"></i>';

    var tooltipBox = document.createElement('div');
    tooltipBox.className   = 'guid-tooltip-box';
    tooltipBox.style.display = 'none';

    // ✅ محتوای HTML — parse می‌شه به‌جای نمایش خام
    // ⚠️ مطمئن شو بک‌اند guid_content رو sanitize کرده (مثلاً با bleach در جنگو)
    var tooltipContent = document.createElement('div');
    tooltipContent.className = 'guid-tooltip-content';
    tooltipContent.innerHTML = attr.guid.guid_content;
    tooltipBox.appendChild(tooltipContent);

    // ✅ دکمه «نمایش بیشتر» → صفحه جزئیات مقاله
    if (attr.guid.slug) {
      var showMore = document.createElement('a');
      showMore.className = 'guid-tooltip-more';
      showMore.href      = '/api/v1/pcb/help/post/' + attr.guid.slug + '/';
      showMore.target     = '_blank';
      showMore.rel        = 'noopener';
      showMore.innerHTML  = 'نمایش بیشتر <i class="bi bi-box-arrow-up-left"></i>';
      tooltipBox.appendChild(showMore);
    }

    // toggle — جلوگیری از بسته شدن وقتی داخل tooltip کلیک می‌شه
    tooltipBtn.addEventListener('click', function (e) {
      e.stopPropagation();
      var isVisible = tooltipBox.style.display !== 'none';
      // بقیه tooltip ها رو ببند
      document.querySelectorAll('.guid-tooltip-box').forEach(function (b) {
        b.style.display = 'none';
      });
      tooltipBox.style.display = isVisible ? 'none' : 'block';
    });

    // کلیک داخل خود tooltip باعث بسته شدن نشه (مثلاً انتخاب متن)
    tooltipBox.addEventListener('click', function (e) {
      e.stopPropagation();
    });

    // کلیک بیرون → بستن
    document.addEventListener('click', function () {
      tooltipBox.style.display = 'none';
    });

    tooltipWrapper.appendChild(tooltipBtn);
    tooltipWrapper.appendChild(tooltipBox);
    labelCol.appendChild(tooltipWrapper);
  }

  // ─── Control column ─────────────────────────────────
  var controlCol = document.createElement('div');
  controlCol.className = 'form-field-control-col';

  var radioGroup = createRadioGroup(attr);
  controlCol.appendChild(radioGroup);

  if (attr.control_type === 'text_input') {
    var textInput = document.createElement('input');
    textInput.type      = 'text';
    textInput.className  = 'form-text-input';
    textInput.value      = formData[attr.name] || '';
    textInput.addEventListener('input', function () {
      formData[attr.name] = this.value;
      radioGroup.querySelectorAll('.radio-btn').forEach(function (b) {
        b.classList.remove('selected');
      });
    });
    controlCol.appendChild(textInput);
  }

  row.appendChild(labelCol);
  row.appendChild(controlCol);
  return row;
}

  // ─── Accordion ───────────────────────────────────────
  // جایگزین Accordion.tsx — collapsible section
  function createAccordion(group) {
    var wrapper = document.createElement('div');
    wrapper.className = 'accordion-item';

    var header = document.createElement('button');
    header.type      = 'button';
    header.className = 'accordion-header';
    header.innerHTML = `
      <span class="accordion-title">${group.display_name}</span>
      <i class="bi bi-chevron-down accordion-icon"></i>
    `;

    var body = document.createElement('div');
    body.className    = 'accordion-body';
    body.style.display = 'block'; // پیش‌فرض: باز

    var divider = document.createElement('div');
    divider.className = 'accordion-fields';
    group.attributes.forEach(function (attr) {
      divider.appendChild(createFormField(attr));
    });
    body.appendChild(divider);

    var isOpen = true;
    header.addEventListener('click', function () {
      isOpen = !isOpen;
      body.style.display = isOpen ? 'block' : 'none';
      var icon = this.querySelector('.accordion-icon');
      icon.className = isOpen
        ? 'bi bi-chevron-up accordion-icon'
        : 'bi bi-chevron-down accordion-icon';
    });

    wrapper.appendChild(header);
    wrapper.appendChild(body);
    return wrapper;
  }

  // ─── Render Full Form ────────────────────────────────
  function renderForm() {
    var mainGroup      = groups.find(function (g) { return g.name === 'main'; });
    var accordionGroups = groups.filter(function (g) { return g.name !== 'main'; });

    // Main group
    if (mainFields) {
      mainFields.innerHTML = '';
      if (mainGroup) {
        mainGroup.attributes.forEach(function (attr) {
          mainFields.appendChild(createFormField(attr));
        });
      }
    }

    // Accordion groups
    if (accordionEl) {
      accordionEl.innerHTML = '';
      accordionGroups.forEach(function (group) {
        accordionEl.appendChild(createAccordion(group));
      });
    }
  }

  // ─── File Input ──────────────────────────────────────
  if (fileInput) {
    fileInput.addEventListener('change', function () {
      gerberFile = this.files[0] || null;
      if (gerberFile && fileNameEl) {
        fileNameEl.textContent = gerberFile.name;
        if (fileTextEl) fileTextEl.textContent = 'فایل انتخاب شد:';
      } else {
        if (fileNameEl) fileNameEl.textContent = '';
        if (fileTextEl) fileTextEl.textContent = 'آپلود فایل Gerber';
      }
    });
  }

  // ─── Build Submit Payload ────────────────────────────
  function buildPayload() {
    var selections = [];
    groups.forEach(function (group) {
      group.attributes.forEach(function (attr) {
        var selectedValue  = formData[attr.name];
        var selectedOption = attr.options.find(function (o) { return o.value === selectedValue; });
        selections.push({
          attribute:       attr.id,
          selected_option: selectedOption ? selectedOption.id : null,
          value:           selectedValue || null,
        });
      });
    });
    return {
      quantity:   1,
      status:     'pending',
      selections: selections,
    };
  }

  // ─── Submit ──────────────────────────────────────────
  function showSubmitMessage(success, text) {
    if (!submitMsgEl) return;
    submitMsgEl.textContent  = text;
    submitMsgEl.className    = 'submit-message ' + (success ? 'submit-success' : 'submit-error');
    submitMsgEl.style.display = 'block';
  }

  if (submitBtn) {
    submitBtn.addEventListener('click', async function () {
      submitBtn.disabled    = true;
      submitBtn.textContent = 'در حال ارسال...';
      if (submitMsgEl) submitMsgEl.style.display = 'none';

      try {
        var payload  = buildPayload();
        var formDataObj = new FormData();
        formDataObj.append('quantity',   String(payload.quantity));
        formDataObj.append('status',     payload.status);
        formDataObj.append('selections', JSON.stringify(payload.selections));

        if (gerberFile) {
          formDataObj.append('file', gerberFile);
        }

        // ارسال multipart/form-data مستقیم به Django
        var result = await api.upload('/api/v1/pcb/orders/', formDataObj);
        showSubmitMessage(true, '✅ سفارش با موفقیت ثبت شد!');
        setTimeout(function () {
          window.location.href = '/api/v1/auth/template/profile/';
        }, 1500);

      } catch (err) {
        var msg = (err.data && (err.data.detail || JSON.stringify(err.data))) || 'خطا در ارسال فرم';
        showSubmitMessage(false, '❌ ' + msg);
        console.error('Submit error:', err);

      } finally {
        submitBtn.disabled    = false;
        submitBtn.textContent = 'ثبت سفارش';
      }
    });
  }

  // ─── Fetch & Init ────────────────────────────────────
  async function init() {
    showLoading(true);
    try {
      var response = await api.get(apiGroupsUrl);
      groups   = (response && response.results) ? response.results : [];
      formData = initializeFormData(groups);
      renderForm();
      showForm();
    } catch (err) {
      showError('خطا در دریافت اطلاعات. لطفاً دوباره تلاش کنید.');
      console.error('Fetch groups error:', err);
    }
  }

  init();

})();