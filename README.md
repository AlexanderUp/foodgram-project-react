![Foodgram workflow status](https://github.com/AlexanderUp/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

# Foodgram API

API приложения Foodgram.
Позволяет создовать различные рецепты, добавлять рецепты в избранное,
подписываться на других авторов, скачивать список продуктов, необходимый
для приготовления блюд, добавленных в избранное.

# Запуск приложения

- Клонируем репозиторий

```git clone https://github.com/AlexanderUp/foodgram-project-react.git```

- Переходим в папку проекта

```cd foodgram-project-react```

- Создаем виртуальное окружение и активируем его

``` python3 -m venv venv```

```source venv/bin/activate```

- Устанавливаем зависимости

``` python3 -m pip install -r requirements.txt```

- Создаем и применяем миграции

```cd backend/foodgram```

```python3 manage.py makemigrations```

```python3 manage.py migrate```

- Создаем суперпользователя

```python3 manage.py createsuperuser```

- Наполянем БД тегами и ингредиентами

```python3 manage.py populate_db```

- Запускаем сервер в режиме отладки

```python3 manage.py runserver```

# Доступные эндпойнты

Документация API доступна по адресу:

```http://127.0.0.1:8000/swagger/```

# Использованные технологии
Python 3.11.1
Django 4.1.7
DRF 3.14

# Автор
Уперенко Александр, студент когорты 44.
