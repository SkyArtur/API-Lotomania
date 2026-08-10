FROM python:3.14-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN SECRET_KEY=collectstatic-build-step python manage.py collectstatic --noinput

RUN useradd --no-create-home --shell /usr/sbin/nologin django \
    && chown -R django:django /app
ENV HOME=/app
USER django

EXPOSE 8080

CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8080"]
