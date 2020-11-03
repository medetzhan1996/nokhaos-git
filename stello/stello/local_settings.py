import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '*+rikz(@$^dg8)1bs)*liyqzo4fpa(0_=n@c6*xt4yw1y4o_mo'

DEBUG = True

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'stello',
        'USER': 'postgres',
        'PASSWORD': 'dostar1996',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

STATIC_DIR = os.path.join(BASE_DIR, 'static')
STATICFILES_DIRS = [STATIC_DIR]