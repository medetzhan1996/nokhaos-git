import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = '*+rsa(@$^dg8)1bs)*asdsadpa(0_=n@c6*xtasdoiumo'

DEBUG = False

ALLOWED_HOSTS = ['127.0.0.1', '195.210.47.233', 'medic-port.kz']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'stello',
        'USER': 'medet',
        'PASSWORD': 'dostar1996',
        'HOST': 'localhost',
        'PORT': '5432'
    }
}

# STATIC_DIR = os.path.join(BASE_DIR, 'static')
# STATICFILES_DIRS = [STATIC_DIR]
STATIC_ROOT =  os.path.join(BASE_DIR, 'static')
