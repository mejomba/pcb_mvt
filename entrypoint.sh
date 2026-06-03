#!/bin/sh
# ====== entrypoint.sh ======
set -e

echo "⏳ منتظر دیتابیس..."
# (healthcheck در compose این کار رو می‌کنه، این یه لایه اضافه‌ست)

echo "🔄 اجرای migration ها..."
python manage.py migrate --noinput

echo "📦 جمع‌آوری فایل‌های static..."
python manage.py collectstatic --noinput

echo "🚀 اجرای Gunicorn..."
exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -