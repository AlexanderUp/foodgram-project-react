FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -U pip
RUN pip3 install -r requirements.txt --no-cache-dir
COPY backend/foodgram/. .
RUN python3 manage.py collectstatic --no-input
RUN python3 manage.py migrate
RUN python3 manage.py populate_db
CMD ["gunicorn", "--bind", "0:8000", "foodgram.wsgi:application"]