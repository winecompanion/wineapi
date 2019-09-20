# wineapi
RESTful API for enotouristic events' management


[![Build Status](https://travis-ci.org/eliasjuanpablo/wineapi.svg?branch=master)](https://travis-ci.org/eliasjuanpablo/wineapi)

## Running the development server

Clone the repo

``` $ git clone https://github.com/eliasjuanpablo/wineapi```

Create a virtualenv (make sure you have python3.5+ and python-venv installed)

``` $ python3 -m venv venv```

Activate it

``` $ source venv/bin/activate```

Install dependencies

``` $ pip install -r requirements.txt ```

Run migrations

``` $ python manage.py migrate```


Run development server

``` $ python manage.py runserver```

winecompanion.heroku.com
