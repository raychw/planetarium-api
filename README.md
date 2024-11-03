# Planetarium API
> Made with Django REST framework

API service for managing planetarium: you can reserve tickets, create astronomy shows, show themes, planetarium domes...
everything written on DRF.

## Installing using GitHub
___
Install PostgresSQL, and create database

```shell
git clone https://github.com/raychw/planetarium-api.git
cd planetarium_api
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
set DB_HOST=<your db hostname>
set DB_NAME=<your db name>
set DB_USER=<your db username>
set DB_PASSWORD=<your db user password>
set SECRET_KEY=<your secret key>
python manage.py migrate
python manage.py runserver
```

This will correctly set up your database and allow you to run your server.

## Run with docker
___
Docker should be installed!

```shell
docker-compose build
docker-compose up
```

## Getting access
___
* Create user via /api/user/register/
* Get access token via /api/user/token/
* If you need an admin access, you can create a superuser by running the following command in the terminal:
```shell
python manage.py createsuperuser
```

## Features
___
* JWT authenticated
* Admin panel /admin/
* Documentation is located at /api/doc/swagger/
* Managing reservations and tickets
* Creating astronomy shows with different themes
* Creating planetarium domes
* Adding show sessions
* Filtering astronomy shows by title and themes
* Filtering show sessions by date
