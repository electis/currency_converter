### Основные возможности API:
* Опрос курса валют каждые 3 минуты
* Регистрация пользователей
* Проведение транзакций между пользователями с автоконвертацией
* Получение списка своих транзакций

### Запуск проекта:
* git clone https://github.com/electis/currency_converter.git
* Настройки переменных окружения в .env.prod файлах, порт в docker-compose.yml
* docker-compose -f docker-compose.yml up -d --build
* Создать суперпользователя (если нужно):\
docker-compose -f docker-compose.yml exec web python3 /usr/src/app/manage.py createsuperuser
* Сервис доступен по адресу http://localhost:8085

### API:
* Регистрация пользователя\
POST http://127.0.0.1:8085/api/registration/ \
{
  "email": "test@test.test", "password": "test", "currency": "BTC", "balance": 1
}

* Совершить транзакцию\
POST http://127.0.0.1:8085/api/transaction/ \
{
  "email": "test@test.test", "password": "test", "to": "andrey@electis.ru", "amount": "10"
}

* Получить список своих транзакций\
GET http://127.0.0.1:8085/api/transaction/ \
{
  "email": "test@test.test", "password": "test"
}
