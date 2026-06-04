# ====== Dockerfile ======
FROM python:3.10-slim

# Environment
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System dependencies برای psycopg2 و سایر بسته‌ها
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

## pip mirror (ابرها)
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "index-url = https://package-mirror.liara.ir/repository/pypi/simple" >> /root/.pip/pip.conf && \
    echo "trusted-host = package-mirror.liara.ir" >> /root/.pip/pip.conf

# نصب وابستگی‌ها (لایه جداگانه برای کش بهتر)
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# کپی پروژه
COPY . /app/

# ساخت کاربر non-root و انتقال مالکیت
#RUN useradd -m -u 1000 appuser && \
#    mkdir -p /app/static /app/media && \
#    chown -R appuser:appuser /app
#USER appuser

EXPOSE 8000

# entrypoint برای migrate + collectstatic + gunicorn
#COPY --chown=appuser:appuser entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["sh", "/app/entrypoint.sh"]