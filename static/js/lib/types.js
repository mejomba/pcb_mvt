// === static/js/lib/types.js ===
// این فایل فقط برای مستندسازی JSDoc هست
// نیازی به import نداره — برای IDE support و خوانایی کد استفاده می‌شه
// ⚠️  با دیدن API‌های واقعی آپدیت خواهد شد

/**
 * @typedef {Object} ApiOption
 * @property {number}  id
 * @property {number}  attribute
 * @property {string}  value
 * @property {string}  display_name
 * @property {boolean} is_default
 * @property {number}  display_order
 * @property {string}  file_url
 */

/**
 * @typedef {Object} Guid
 * @property {number} id
 * @property {string} slug
 * @property {string} guid_content
 */

/**
 * @typedef {Object} ApiAttribute
 * @property {number}              id
 * @property {number}              group
 * @property {string}              name
 * @property {string}              display_name
 * @property {'radio_button'|'text_input'} control_type
 * @property {number}              display_order
 * @property {ApiOption[]}         options
 * @property {Guid}                guid
 */

/**
 * @typedef {Object} ApiGroup
 * @property {number}         id
 * @property {string}         name
 * @property {string}         display_name
 * @property {number}         display_order
 * @property {ApiAttribute[]} attributes
 */

/**
 * @typedef {Object} ApiResponse
 * @property {number}     count
 * @property {null}       next
 * @property {null}       previous
 * @property {ApiGroup[]} results
 */

/**
 * @typedef {Object} Selection
 * @property {number} id
 * @property {number} attribute
 * @property {string} attribute_name
 * @property {number} selected_option
 * @property {string} selected_option_name
 * @property {string} value
 */

/**
 * @typedef {Object} Order
 * @property {number}   id
 * @property {number}   user
 * @property {string|null} user_name
 * @property {number}   quantity
 * @property {'pending'|'processing'|'shipped'|'delivered'|'cancelled'} status
 * @property {string}   created_at
 * @property {string}   updated_at
 * @property {string}   file
 * @property {string}   quotation
 * @property {string[]} payments_urls
 * @property {Selection[]} selections
 */

/**
 * @typedef {Object} OrdersApiResponse
 * @property {number}   count
 * @property {string|null} next
 * @property {string|null} previous
 * @property {Order[]}  results
 */

/**
 * @typedef {Object} HelpMenuItem
 * @property {string}          id
 * @property {string}          title
 * @property {string}          slug
 * @property {HelpMenuItem[]}  [child]
 */

/**
 * @typedef {Object} HelpPageContent
 * @property {{ title: string, path: string }[]} breadcrumbs
 * @property {string}                             title
 * @property {{ title: string, path: string }[]} articles
 */

/**
 * @typedef {Object} HelpPageContentList
 * @property {number}   id
 * @property {string}   title
 * @property {string}   slug
 * @property {string}   category_name
 * @property {string[]} breadcrumb
 */

/**
 * @typedef {Object} User
 * @property {number} id
 */