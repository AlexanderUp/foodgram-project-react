FROM python:3.11-slim
COPY data/. ./data
WORKDIR /app/app
COPY requirements.txt requirements.txt
RUN pip3 install -U pip
RUN pip3 install -r requirements.txt --no-cache-dir
COPY backend/foodgram/. .
CMD ["gunicorn", "--bind", "0:8000", "foodgram.wsgi:application"]