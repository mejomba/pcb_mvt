## Base image
#FROM python:3.10-slim
#
## Set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#
## Set work directory
#WORKDIR /app
#
## Install dependencies
#COPY requirements.txt /app/
## ایجاد فایل پیکربندی pip برای استفاده از mirror دلخواه
#RUN mkdir -p /root/.pip && \
#    echo "[global]" > /root/.pip/pip.conf && \
#    echo "index-url = https://mirror.abrha.net/repository/pypi/simple" >> /root/.pip/pip.conf && \
#    echo "trusted-host = mirror.abrha.net" >> /root/.pip/pip.conf
#
#RUN pip install --no-cache-dir -r requirements.txt
#
## Copy project
#COPY . /app/
#
## پورت 8000 را برای Gunicorn باز کن
#EXPOSE 8000
#
## (اختیاری ولی پیشنهادی) یک اسکریپت entrypoint برای اجرای migrate ها بسازید
## CMD ["gunicorn", "your_project_name.wsgi:application", "--bind", "0.0.0.0:8000"]
## برای توسعه، می‌توانید از runserver استفاده کنید:
#CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]


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
COPY --chown=appuser:appuser entrypoint.sh /app/entrypoint.sh
ENTRYPOINT ["sh", "/app/entrypoint.sh"]