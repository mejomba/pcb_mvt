$(document).ready(function() {

  // ========== 1. توابع کمکی ==========
  function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie !== '') {
      var cookies = document.cookie.split(';');
      for (var i = 0; i < cookies.length; i++) {
        var cookie = $.trim(cookies[i]);
        if (cookie.substring(0, name.length + 1) === (name + '=')) {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  function getAccessToken() {
    return getCookie('access');
  }

  function escapeHtml(str) {
    return $('<div>').text(str).html();
  }

  // ========== 2. متغیرهای اصلی ==========
  var formData = {};       // { attribute_name: value }
  var groupsData = [];     // اطلاعات کامل API

  var $app = $('#app');

  // ========== 3. ساخت UI اولیه ==========
  $app.html(`
    <main class="p-3 p-sm-4 p-lg-5">
      <div class="container bg-white rounded shadow-sm py-4 px-3" style="max-width: 56rem;">
        <div class="form-group">
          <label for="gerberFile" class="font-weight-bold">آپلود فایل Gerber</label>
          <input type="file" class="form-control-file" id="gerberFile" name="file">
          <small class="form-text text-muted">فایل‌های فشرده با فرمت zip, rar</small>
        </div>
        <div id="attributes-container"></div>
        <div class="mt-4 text-center">
          <button id="submitOrderBtn" type="button" class="btn btn-primary px-5 py-2">ثبت سفارش</button>
        </div>
        <div id="submitMessage" class="text-center mt-3 font-weight-medium"></div>
        <div class="mt-4 p-3 bg-gray-200 rounded">
          <h5>Current Form State:</h5>
          <pre id="formDataDebug" class="small"></pre>
        </div>
      </div>
    </main>
  `);

  var $container = $('#attributes-container');
  var $debug = $('#formDataDebug');
  var $submitBtn = $('#submitOrderBtn');
  var $msg = $('#submitMessage');
  debugger

  // ========== 4. دریافت داده‌ها از API ==========
  $.ajax({
    url: apiGroupsUrl,
    method: 'GET',
    headers: {
      'Authorization': 'Bearer ' + getAccessToken()
    },
    success: function(response) {
      groupsData = response.results || response;
      buildForm(groupsData);
      syncFormDataFromDOM();  // همگام‌سازی مقادیر اولیه
      updateDebug();
      initGuidPopovers();     // فعال‌سازی popoverها با کلیک
    },
    error: function() {
      $container.html('<div class="alert alert-danger">خطا در دریافت اطلاعات. لطفاً دوباره تلاش کنید.</div>');
    }
  });

  // ========== 5. ساخت پویای فرم ==========
  function buildForm(groups) {
    groups.forEach(function(group) {
      if (group.name === "main") {
        var groupHtml = '<div class="space-y-4">';
        group.attributes.forEach(function(attr) {
          groupHtml += buildAttributeField(attr);
        });
        groupHtml += '</div>';
        $container.append(groupHtml);
      } else {
        var accordionId = 'collapse_' + group.id;
        var header = `
          <div class="border-top border-gray-200">
            <button class="btn btn-link d-flex justify-content-between align-items-center w-100 py-3 text-decoration-none text-md font-weight-bold text-gray-800 bg-light px-2" 
                    type="button" data-toggle="collapse" data-target="#${accordionId}" aria-expanded="true">
              <span>${group.display_name}</span>
              <i class="bi bi-chevron-down rotate-icon"></i>
            </button>
          </div>`;
        var body = `
          <div id="${accordionId}" class="collapse show">
            <div class="pb-4 px-2">
              <div class="divide-y divide-gray-200">
                ${group.attributes.map(attr => buildAttributeField(attr)).join('')}
              </div>
            </div>
          </div>`;
        $container.append(header + body);
      }
    });

    // چرخش آیکون accordion
    $('[data-toggle="collapse"]').on('click', function() {
      $(this).find('.bi-chevron-down').toggleClass('rotate');
    });
  }

  function buildRadioGroup(name, options, selectedValue) {
    var html = '<div class="d-flex flex-wrap align-items-end gap-2">';
    options.forEach(function(opt) {
      var checked = (opt.value === selectedValue) ? 'checked' : '';
      var imgTag = opt.file_url ? '<img src="' + opt.file_url + '" alt="' + opt.display_name + '" width="60" class="mb-1">' : '';
      html += '<div class="custom-radio-card">' +
              '<input type="radio" id="' + name + '_' + opt.id + '" name="' + name + '" value="' + opt.value + '" ' + checked + ' class="sr-only" data-radio-group>' +
              '<label for="' + name + '_' + opt.id + '" class="radio-label border rounded-sm px-3 py-1 text-sm font-medium position-relative d-flex flex-column align-items-center justify-content-center">' +
              imgTag +
              opt.display_name +
              '<i class="bi bi-check-lg check-icon"></i>' +
              '</label></div>';
    });
    html += '</div>';
    return html;
  }

  function buildAttributeField(attr) {
    // ساخت کنترل
    var controlHtml = '';
    if (attr.control_type === 'radio_button') {
      controlHtml = buildRadioGroup(attr.name, attr.options, formData[attr.name] || '');
    } else if (attr.control_type === 'text_input') {
      controlHtml = '<div class="d-flex align-items-center gap-2">' +
                    buildRadioGroup(attr.name, attr.options, formData[attr.name] || '') +
                    '<input type="text" name="' + attr.name + '_text" class="form-control form-control-sm w-auto text-center" ' +
                    'value="' + (formData[attr.name] || '') + '" style="width: 6rem;">' +
                    '</div>';
    }

    // Tooltip فقط اگر محتوا وجود داشته باشد
    var guidHtml = '';
    if (attr.guid && attr.guid.guid_content) {
      guidHtml = '<span class="guid-icon" data-attribute-id="' + attr.id + '">' +
                 '<i class="bi bi-info-circle text-primary"></i></span>';
    }

    // ساختار FormField
    return '<div class="form-row py-3">' +
           '<div class="col-md-3 d-flex justify-content-between align-items-center">' +
           '<label class="text-muted font-weight-medium mb-0">' + attr.display_name + '</label>' + guidHtml +
           '</div>' +
           '<div class="col-md-9 d-flex flex-wrap align-items-center gap-2">' + controlHtml + '</div>' +
           '</div>';
  }

  // ========== 6. همگام‌سازی formData ==========
  function syncFormDataFromDOM() {
    // خواندن مقادیر اولیه از radioهای checked
    $('input[type="radio"][data-radio-group]:checked').each(function() {
      formData[this.name] = this.value;
    });
    // خواندن text inputهای پیش‌فرض
    $('input[type="text"][name$="_text"]').each(function() {
      var attrName = this.name.replace('_text', '');
      formData[attrName] = this.value;
    });
  }

  // آپدیت مستقیم در اثر تغییر کاربر
  $(document).on('change', 'input[type="radio"][data-radio-group]', function() {
    formData[this.name] = this.value;
    updateDebug();
  });

  $(document).on('input', 'input[type="text"][name$="_text"]', function() {
    var attrName = this.name.replace('_text', '');
    formData[attrName] = this.value;
    updateDebug();
  });

  function updateDebug() {
    $debug.text(JSON.stringify(formData, null, 2));
  }

  // ========== 7. فعال‌سازی popoverهای راهنما (کلیک) ==========
  function initGuidPopovers() {
    $('.guid-icon').each(function() {
      var $icon = $(this);
      var attrId = $icon.data('attribute-id');

      // پیدا کردن attribute مربوطه در groupsData
      var attr = null;
      groupsData.some(function(group) {
        return group.attributes.some(function(attribute) {
          if (attribute.id == attrId) {
            attr = attribute;
            return true;
          }
          return false;
        });
      });

      if (!attr || !attr.guid) return;

      var content = attr.guid.guid_content || '';
      if (attr.guid.slug) {
        content += '<br><a href="/help/post/' + attr.guid.slug + '/" target="_blank" class="btn btn-sm btn-primary mt-1">show more</a>';
      }

      $icon.popover({
        content: content,
        html: true,
        placement: 'top',
        trigger: 'click',          // باز شدن با کلیک، بسته شدن با کلیک بیرون
        container: 'body'
      });
    });
  }

  // ========== 8. ثبت سفارش ==========
  $submitBtn.on('click', function() {
    $submitBtn.prop('disabled', true).text('در حال ارسال...');
    $msg.text('');

    var selections = [];
    groupsData.forEach(function(group) {
      group.attributes.forEach(function(attr) {
        var selectedValue = formData[attr.name] || '';
        var selectedOption = attr.options.find(function(opt) { return opt.value === selectedValue; });
        selections.push({
          attribute: attr.id,
          selected_option: selectedOption ? selectedOption.id : null,
          value: selectedValue
        });
      });
    });

    var formDataToSend = new FormData();
    formDataToSend.append('quantity', 1);
    formDataToSend.append('status', 'pending');
    formDataToSend.append('selections', JSON.stringify(selections));

    var fileInput = document.getElementById('gerberFile');
    if (fileInput && fileInput.files.length > 0) {
      formDataToSend.append('file', fileInput.files[0]);
    }

    $.ajax({
      url: apiOrderUrl,
      method: 'POST',
      data: formDataToSend,
      processData: false,
      contentType: false,
      headers: {
        'Authorization': 'Bearer ' + getAccessToken()
      },
      success: function(response) {
        $msg.html('✅ فرم با موفقیت ثبت شد!').removeClass('text-danger').addClass('text-success');
      },
      error: function(jqXHR) {
        var err = 'خطا در ثبت فرم';
        if (jqXHR.responseJSON) {
          if (jqXHR.responseJSON.detail) err = jqXHR.responseJSON.detail;
          else if (jqXHR.responseJSON.message) err = jqXHR.responseJSON.message;
        }
        $msg.text('❌ ' + err).removeClass('text-success').addClass('text-danger');
        if (jqXHR.status === 401) {
          window.location.href = '/api/v1/auth/login/';
        }
      },
      complete: function() {
        $submitBtn.prop('disabled', false).text('ثبت سفارش');
      }
    });
  });

});