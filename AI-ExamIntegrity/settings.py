# AI-ExamIntegrity/settings.py

import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))



SECRET_KEY = 'your-secret-key-here'
DEBUG = True
ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'channels',
    'integrity_app',
    'accounts',
    'proctor',
    'student',
    'alert',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'AI-ExamIntegrity.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'AI-ExamIntegrity.wsgi.application'
ASGI_APPLICATION = 'AI-ExamIntegrity.asgi.application'

# Channel layers using an in-memory backend (suitable for development)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',
    },
}

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Riyadh'
USE_TZ = True

USE_I18N = True
USE_L10N = True


STATIC_URL = '/static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),  # Global static folder (if needed)
]
# Ensure Django collects all static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Media files (for saving uploaded files, such as your audio recordings)
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
LOGIN_URL = '/accounts/login/'  # Adjust based on your login route

EMAIL_HOST = "smtp.gmail.com"
EMAIL_PORT = 465
EMAIL_USE_SSL = True
# EMAIL_USE_TLS = True  # Instead of EMAIL_USE_SSL
# EMAIL_PORT = 587
# EMAIL_USE_SSL = False
load_dotenv()

EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD")


AUTH_USER_MODEL = 'accounts.CustomUser'