FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip3 install -U pip
RUN pip3 install -r requirements.txt --no-cache-dir
COPY backend/foodgram/. .
COPY data/. ./data
CMD ["gunicorn", "--bind", "0:8000", "foodgram.wsgi:application"]