FROM python:3.11-slim

WORKDIR /app

COPY req.txt .
RUN pip install -r req.txt

COPY . .

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "Greanleaf.wsgi:application", "--bind", "0.0.0.0:8000"]