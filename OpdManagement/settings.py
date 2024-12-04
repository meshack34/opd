from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent

# Static and Media Configuration
STATIC_URL = '/static/'
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static')]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security
SECRET_KEY = 'django-insecure-ak*rhka_)b2=o&v51j24o#ytx4geojgb4=hlycg8&@r&8-qv$+'
DEBUG = True  # Change to False in production
ALLOWED_HOSTS = ["*"]

# Applications
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    
    # Third-Party Apps
    'rest_framework',
    'crispy_forms',
    'crispy_bootstrap4',
    'mathfilters',
    'import_export',
    # 'admin_searchable_dropdown',
    # 'debug_toolbar',
    
    # Custom Apps
    'usermanagementapp',
    'testapp',
    'ramapp',
    'IPDapp',
]

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_session_timeout.middleware.SessionTimeoutMiddleware',
    'testapp.middleware.MiddlewareExecutionStart',
]

ROOT_URLCONF = 'OpdManagement.urls'

# Templates
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
                'testapp.context_processors.users_and_projects',
            ],
        },
    },
]

# WSGI Application
WSGI_APPLICATION = 'OpdManagement.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Password Validators
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# Localization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Africa/Nairobi'
USE_I18N = True
USE_TZ = True

# Authentication Redirects
LOGIN_REDIRECT_URL = '/user_login'
LOGOUT_REDIRECT_URL = '/user_login'

# Crispy Forms
CRISPY_TEMPLATE_PACK = 'bootstrap4'

# Default Primary Key Field Type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Session Timeout
SESSION_EXPIRE_SECONDS = 86400
SESSION_EXPIRE_AFTER_LAST_ACTIVITY = True
SESSION_EXPIRE_AFTER_LAST_ACTIVITY_GRACE_PERIOD = 1440
SESSION_TIMEOUT_REDIRECT = '/user_login'

RAZORPAY_API_KEY='rzp_test_8ocxy7Ig5NRf9z'
RAZORPAY_API_SECRET_KEY='N0kHcCLagthKdQXP4PDf4EfH'
#Email Configurations
EMAIL_HOST='smtp.gmail.com'
EMAIL_PORT=587
EMAIL_HOST_USER= 'gohilaljcet@gmail.com'
EMAIL_HOST_PASSWORD= 'mtbfybqkckfuskxu'
EMAIL_USE_TLS=True