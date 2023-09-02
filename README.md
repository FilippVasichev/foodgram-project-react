
![foodgram workflow](https://github.com/FilippVasichev/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## **Описание проекта Foodgram:** 

Foodgram - REST API проект написанный на DRF

«Фудграм» — сайт, на котором пользователи могут публиковать рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других
авторов. Пользователям сайта также доступен сервис «Список покупок».
Он позволит создавать список продуктов, которые нужно купить для
приготовления выбранных блюд.

<details>
  <summary>Запуск бэкенда проекта</summary>

**Установить виртуальное окружение venv:** 

``` 
python -m venv venv 
``` 

**Aктивировать виртуальное окружение venv:** 
``` 
source venv/bin/activate 
``` 

**Установить зависимости из файла requirements.txt:**
``` 
pip install -r requirements.txt 
``` 

**Создать секретный ключ приложения:**
```
Создать файл .env в корневой папке проекта
Сгенерировать секретный ключ с помощью команды:

python -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())'

Заполнить файл env по шаблону:
    SQLITE=True (Если необходимо работать с postgres - удалите данную запись)
    DEBUG=True
    
    SECRET_KEY = <ваш секретный ключ>
    ALLOWED_HOSTS=<IP сервера>, <Домен сервера>
    POSTGRES_USER=django_user
    POSTGRES_PASSWORD=django_password
    POSTGRES_DB=django_db
    
    DB_HOST=db
    DB_PORT=5432
```


**Выполнить миграции:**
``` 
python manage.py migrate 
``` 

**Запустить проект:** 
``` 
python manage.py runserver 
```


#### После выполнения вышеперечисленных инструкций бэкенд проекта будет доступен по адресу http://127.0.0.1:8000/
</details>

<details>
  <summary>Запуск на удаленном сервере</summary>

#### 1. Создать директорию foodgram/ в домашней директории сервера.
#### 2. В корне папки foodgram/ поместить файл .env, заполнить его по шаблону
```
  SECRET_KEY = <ваш секретный ключ>
  ALLOWED_HOSTS=<IP сервера>, <Домен сервера>
  POSTGRES_USER=django_user
  POSTGRES_PASSWORD=django_password
  POSTGRES_DB=django_db
  
  DB_HOST=db
  DB_PORT=5432
```
#### 3. Установить Nginx и настроить конфигурацию так, чтобы все запросы шли в контейнеры на порт 8000.
```bazaar
    sudo apt install nginx -y 
    sudo nano etc/nginx/sites-enabled/default
```
 - Пример конфигурации nginx
  ```
    server {
        server_name <Ваш IP> <Домен вашего сайта>;
        server_tokens off;
        client_max_body_size 20M;
    
        location / {
            proxy_set_header Host $http_host;
            proxy_pass http://127.0.0.1:8000;
    }
```
> При необходимости настройте SSL-соединение

#### 4. Установить docker и docker-compose
```bazaar
    sudo apt update
    sudo apt install curl
    curl -fSL https://get.docker.com -o get-docker.sh
    sudo sh ./get-docker.sh
    sudo apt-get install docker-compose-plugin  
```
#### 5. Форкнуть данный репозиторий и добавить в Secrets GitHub Actions переменные окружения
```bazaar
    DOCKER_USERNAME=<имя пользователя DockerHub>
    DOCKER_PASSWORD=<пароль от DockerHub>
    
    USER=<username для подключения к удаленному серверу>
    HOST=<ip сервера>
    PASSPHRASE=<пароль для сервера, если он установлен>
    SSH_KEY=<ваш приватный SSH-ключ>
    
    TELEGRAM_TO=<айди вашего телеграмм аккаунта>
    TELEGRAM_TOKEN=<токен вашего телеграмм бота>
```
#### 6. Запустить workflow проекта выполнив команды:
```bazaar
  git add .
  git commit -m ''
  git push
```
#### 7. После этого выпонятся следующие workflow jobs:

- backend_test: запускает линтер бекенда
- build_backend_and_push_to_docker_hub: сборка и размещение образа бэкенда проекта на DockerHub.
- build_frontend_and_push_to_docker_hub: сборка и размещение образа фронтенда проекта на DockerHub.
- build_nginx_and_push_to_docker_hub: сборка и размещение образа nginx проекта на DockerHub.
- deploy: автоматический деплой на боевой сервер и запуск проекта.
- send_message: отправка уведомления об успешном деплое в персональный чат.
</details>


## Технологии: 

+ Python 3.9
+ Django: 3.2.3
+ Django REST framework: 3.12.4
+ djoser: 2.2.0

# Автор 

+ FilippVasichev

+ ![GitHub](https://img.shields.io/badge/GitHub-FilippVasichev-brightgreen)
+ ![Gmail](https://img.shields.io/badge/Gmail-aciktrasher@gmail.com-red)
+ ![Telegram](https://img.shields.io/badge/Telegram-@zionweeds-blue)


