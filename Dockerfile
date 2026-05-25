# Base image
FROM python:3.10-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set work directory
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
# ایجاد فایل پیکربندی pip برای استفاده از mirror دلخواه
RUN mkdir -p /root/.pip && \
    echo "[global]" > /root/.pip/pip.conf && \
    echo "index-url = https://mirror.abrha.net/repository/pypi/simple" >> /root/.pip/pip.conf && \
    echo "trusted-host = mirror.abrha.net" >> /root/.pip/pip.conf

RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# پورت 8000 را برای Gunicorn باز کن
EXPOSE 8000

# (اختیاری ولی پیشنهادی) یک اسکریپت entrypoint برای اجرای migrate ها بسازید
# CMD ["gunicorn", "your_project_name.wsgi:application", "--bind", "0.0.0.0:8000"]
# برای توسعه، می‌توانید از runserver استفاده کنید:
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]