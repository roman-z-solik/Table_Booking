# Restaurant Table Booking System

Django веб-приложение для онлайн-бронирования столиков в ресторане. Система позволяет пользователям просматривать доступные столики, бронировать их на выбранные дату и время, управлять своими бронированиями и оставлять отзывы.

## Технологии
![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)        
![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)  
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![HTML5](https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white)
![CSS3](https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-563D7C?style=for-the-badge&logo=bootstrap&logoColor=white)
![Coverage](https://img.shields.io/badge/coverage-84%25-brightgreen?style=for-the-badge)

## Использование
Открыть проект в 
![Pycharm](https://img.shields.io/badge/PyCharm-000000.svg?&style=for-the-badge&logo=PyCharm&logoColor=white)  

### Приложение booking

`booking/models.py`:

Класс Table - модель столика с полями: номер, вместимость, VIP-статус, активность и описание.  
Класс Booking - модель бронирования с полями: пользователь, столик, дата, время начала/окончания, количество гостей и специальные пожелания.  
Класс Page - модель страниц сайта (О нас, Галерея, Меню, Команда).  
Класс Feedback - модель отзывов посетителей.

`booking/views.py`:

Функция home - главная страница с отображением статуса столиков.  
Функция booking_create - создание нового бронирования с проверкой доступности столика.  
Функция booking_list - список бронирований пользователя.  
Функция booking_edit - редактирование существующего бронирования.  
Функция booking_cancel - отмена бронирования.  
Функция page_detail - отображение страниц сайта.  
Функция feedback - обработка формы обратной связи.

`booking/forms.py`:

Класс BookingForm - форма бронирования с динамическим выбором количества гостей в зависимости от вместимости столика.  
Класс BookingEditForm - форма редактирования бронирования.  
Класс FeedbackForm - форма обратной связи с автозаполнением для аутентифицированных пользователей.

`booking/urls.py`:

Маршруты приложения: главная страница, страницы сайта, бронирования, обратная связь, API для получения вместимости столика.

### Приложение users

`users/models.py`:

Класс CustomUser - кастомная модель пользователя с email как основным идентификатором, дополнительными полями телефона и подтверждения email.

`users/views.py`:

Функция register - регистрация нового пользователя с отправкой приветственного email.  
Функция user_login - аутентификация пользователя.  
Функция user_logout - выход из системы.  
Функция profile - просмотр профиля пользователя.  
Функция profile_edit - редактирование профиля.  
Функция profile_delete - удаление аккаунта.

`users/forms.py`:

Класс CustomUserCreationForm - форма регистрации пользователя.  
Класс CustomAuthenticationForm - форма входа в систему.  
Класс CustomUserChangeForm - форма редактирования профиля.

## API Endpoints

### Бронирования
- `GET /` - главная страница с доступностью столиков
- `GET /about/` - страница "О нас"
- `GET /gallery/` - галерея ресторана
- `GET /menu/` - меню ресторана
- `GET /team/` - команда ресторана
- `GET /feedback/` - форма обратной связи
- `GET /booking/create/` - форма создания бронирования (требует аутентификации)
- `GET /booking/list/` - список бронирований пользователя (требует аутентификации)
- `GET /booking/edit/<int:booking_id>/` - редактирование бронирования (требует аутентификации)
- `GET /booking/cancel/<int:booking_id>/` - отмена бронирования (требует аутентификации)

### API
- `GET /tables/<int:table_id>/capacity/` - получение вместимости столика (JSON API)

### Пользователи
- `GET /users/register/` - регистрация нового пользователя
- `GET /users/login/` - вход в систему
- `GET /users/logout/` - выход из системы
- `GET /users/profile/` - профиль пользователя (требует аутентификации)
- `GET /users/profile/edit/` - редактирование профиля (требует аутентификации)
- `GET /users/profile/delete/` - удаление аккаунта (требует аутентификации)

## Функциональность

### Система бронирования
- Реальное время: отображение занятости столиков на текущий день
- Валидация: проверка доступности столика на выбранные дату и время
- Авторасчет: автоматический расчет времени окончания по продолжительности
- Ограничения: выбор количества гостей ограничен вместимостью столика

### Управление бронированиями
- Просмотр: история всех бронирований пользователя
- Редактирование: изменение даты, времени, столика и количества гостей
- Отмена: удаление бронирования с подтверждением
- Уведомления: отправка email при создании, изменении и отмене бронирования

### Пользовательская система
- Аутентификация: вход по email с кастомной моделью пользователя
- Регистрация: создание аккаунта с отправкой приветственного email
- Профиль: просмотр и редактирование личной информации
- Безопасность: подтверждение пароля при удалении аккаунта

### Контент сайта
- Страницы: динамическое управление страницами через админку
- Галерея: загрузка и отображение фотографий ресторана
- Меню: управление позициями меню с категориями и ценами
- Команда: информация о сотрудниках ресторана

### Обратная связь
- Форма: отправка сообщений от посетителей
- Автозаполнение: автоматическое заполнение данных для зарегистрированных пользователей
- Уведомление: подтверждение отправки сообщения

-----------------------------------
В проекте присутствует файл
### requirements.txt  
Файл с зависимостями pip для проекта. Для установки зависимостей следует в терминале (возможно в терминале PyCharm) ввести команду:
```bash
pip install -r requirements.txt
```

## Настройка окружения

### Создайте файл .env на основе .env.example:

### Заполните файл .env следующими настройками:

**Django:**
- `SECRET_KEY` - секретный ключ Django проекта
- `DEBUG` - режим отладки (True/False)
- `ALLOWED_HOSTS` - разрешенные хосты через запятую

**База данных PostgreSQL:**
- `DB_NAME` - имя базы данных
- `DB_USER` - пользователь базы данных
- `DB_PASSWORD` - пароль пользователя
- `DB_HOST` - хост базы данных
- `DB_PORT` - порт базы данных

**Настройки ресторана:**
- `OPEN_TIME` - время открытия ресторана (например: 10:00)
- `CLOSE_TIME` - время закрытия ресторана (например: 23:00)
- `MIN_BOOKING_HOURS` - минимальное время бронирования (в часах)
- `MAX_BOOKING_HOURS` - максимальное время бронирования (в часах)
- `CONTACT_PHONE` - контактный телефон ресторана
- `CONTACT_EMAIL` - контактный email ресторана
- `ADDRESS` - адрес ресторана
- `RESTAURANT_NAME` - название ресторана
- `RESTAURANT_DESCRIPTION` - описание ресторана

**Настройки email:**
- `EMAIL_HOST` - SMTP сервер для отправки email
- `EMAIL_PORT` - порт SMTP сервера
- `EMAIL_USE_TLS` - использование TLS (True/False)
- `EMAIL_HOST_USER` - email пользователя
- `EMAIL_HOST_PASSWORD` - пароль приложения (не пароль от email)

**Информация о ресторане:**
- `MAX_TABLE_CAPACITY` - максимальная вместимость столика (целое число)
- `TABLE_CAPACITIES` - доступные вместимости столиков (формат: 2:2 guests, 4:4 guests)
- `BOOKING_STATUSES` - статусы бронирований (free, active, reserved, cancelled)

**Правила ресторана:**
- `BOOKING_RULES` - правила бронирования (формат: Booking for 1-4 hours|Cancellation 2 hours before the visit)
- `MAX_BOOKING_DAYS_AHEAD` - количество дней для бронирования вперед (пример: 30)

## Запуск приложения  
### Выполнение миграций  
```bash
python manage.py migrate
```
### Создание суперпользователя
```bash
python manage.py createsuperuser
```
### Сбор статических файлов
```bash
python manage.py collectstatic --noinput
```
### Запуск сервера разработки
```bash
python manage.py runserver
```
### Запуск тестов
```bash
python manage.py test
```

## Запуск через Docker
### Предварительные требования
Установленный Docker
Установленный Docker Compose

### Шаги для запуска
Клонируйте репозиторий:
```bash
git clone <repository-url>
cd <project-directory>
```
Создайте файл .env:
```bash
cp .env.example .env
```
Отредактируйте .env файл с вашими настройками.  
Запустите контейнеры:
```bash
docker-compose up -d
```
Выполните миграции:
```bash
docker-compose exec web python manage.py migrate
```
Создайте суперпользователя:
```bash
docker-compose exec web python manage.py createsuperuser
```

## Требования
Для установки и запуска проекта, необходимы:

![Python](https://img.shields.io/badge/Python-FFD43B?style=for-the-badge&logo=python&logoColor=blue)  
Python - интерпретатор Python версии 3.8+

![PyCharm](https://img.shields.io/badge/PyCharm-000000.svg?&style=for-the-badge&logo=PyCharm&logoColor=white)  
PyCharm - среда разработки (рекомендуется)

![Django](https://img.shields.io/badge/Django-092E20?style=for-the-badge&logo=django&logoColor=green)  
Django - веб-фреймворк для Python

![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)  
PostgreSQL - система управления базами данных

## Тестирование
Проект включает полный набор тестов с покрытием 84%  
Для запуска всех тестов:
```bash
python manage.py test
```
Для проверки покрытия кода:
```bash
coverage run manage.py test
coverage report
coverage html
```
Команда проекта
[Roman Z](https://github.com/roman-z-solik)