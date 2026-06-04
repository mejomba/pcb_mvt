// === js/lib/blog.js ===
// وابستگی: api.js باید قبلاً لود شده باشه

const BLOG_PLACEHOLDER = '/static/images/placeholders/blog-cover.png';
// ↑ مسیر placeholder رو با آدرس واقعی در پروژه جنگو جایگزین کن

// ─── Get Blog Posts ──────────────────────────────────────────
// جایگزین: getBlogPosts در lib/api/blog.ts
async function getBlogPosts({ page = 1, pageSize = 10, tag = null } = {}) {
  let url = `/blog/posts/?page=${page}&page_size=${pageSize}`;
  if (tag) url += `&tag=${encodeURIComponent(tag)}`;

  try {
    const data = await api.get(url);
    // تصویر پیش‌فرض برای پست‌هایی که thumbnail ندارن
    data.results = data.results.map(post => ({
      ...post,
      thumbnail: post.thumbnail || BLOG_PLACEHOLDER,
    }));
    return data; // { count, next, previous, results[] }
  } catch (err) {
    console.error('Failed to load posts:', err.status ?? 'unknown');
    throw err;
  }
}

// ─── Get Post By Slug ─────────────────────────────────────────
// جایگزین: getPostBySlug در lib/api/blog.ts
async function getPostBySlug(slug) {
  try {
    const data = await api.get(`/blog/posts/${slug}/`);
    return data;
  } catch (err) {
    if (err.status === 404) return null;
    throw err;
  }
}