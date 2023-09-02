
![foodgram workflow](https://github.com/FilippVasichev/foodgram-project-react/actions/workflows/main.yml/badge.svg)

## **Описание проекта Foodgram:** 

Foodgram - REST API проект написанный на DRF

«Фудграм» — сайт, на котором пользователи могут публиковать рецепты,
добавлять чужие рецепты в избранное и подписываться на публикации других
авторов. Пользователям сайта также доступен сервис «Список покупок».
Он позволит создавать список продуктов, которые нужно купить для
приготовления выбранных блюд.

## Как запустить проект на внутреннем интерфейсе: 

 

**Клонировать репозиторий с GitHub и перейти в него в командной строке:** 

``` 
git clone git@github.com:FilippVasichev/infra_sprint1.git 
```
**Шаг 1: Запуск бэкенда проекта:** 

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


## Технологии: 

+ Python 3.9
+ Django: 3.2.3
+ Django REST framework: 3.12.4
+ djoser: 2.2.0

# Автор 

+ FilippVasichev
+ https://github.com/FilippVasichev 


