from django.contrib.messages import constants as message_constants
from pathlib import Path
import os
import dj_database_url # Importante para o banco na nuvem

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# --- CONFIGURAÇÃO DE AMBIENTE (LOCAL VS NUVEM) ---
# Verifica se estamos rodando no Render através da variável de ambiente
ON_RENDER = 'RENDER' in os.environ

# SECURITY WARNING: keep the secret key used in production secret!
# Na nuvem, tenta pegar da variável de ambiente, senão usa a chave padrão (apenas para build)
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-xu4^66$qjsm86acg5()+&t5g&)9ulpey@8%cvyv3e-_p9%q@aa')

# settings.py
LICENSE_SECRET_KEY = 'TEST-e913c0fd-99a3-423d-ad0b-89629b170b28'

# SECURITY WARNING: don't run with debug turned on in production!
# Se estiver no Render, Debug é False (Segurança). Se não, é True (Desenvolvimento)
DEBUG = not ON_RENDER

# Configuração de Hosts Permitidos
ALLOWED_HOSTS = ['*'] 
if ON_RENDER:
    # No Render, pegamos o nome do host automaticamente
    RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
    if RENDER_EXTERNAL_HOSTNAME:
        ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)

# Application definition
INSTALLED_APPS = [
    # 'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Apps do Projeto
    'configuracoes',
    'analytics',
    'licencas',
    'empresas',
    'clientes',
    'estoque',
    'usuarios',
    'caixa',
    'comanda',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware', # Adicionado para servir arquivos estáticos rápido
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # Adicione seu middleware global aqui
    'provendas.middleware.AuthMiddleware',
]

ROOT_URLCONF = 'provendas.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],  # Adiciona a pasta de templates
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'configuracoes.context_processors.configuracoes',
                'configuracoes.context_processors.license_days_remaining',
            ],
        },
    },
]

WSGI_APPLICATION = 'provendas.wsgi.application'

# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

# Configuração padrão (SQLite local)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
        }
    }
}

# Se estiver no Render, sobrescreve com o PostgreSQL
if ON_RENDER:
    DATABASES['default'] = dj_database_url.config(
        default=os.environ.get('DATABASE_URL'),
        conn_max_age=600, # Mantém a conexão aberta por 10min para performance (fluidez)
        ssl_require=True  # Segurança exigida pelo Render
    )

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'pt-BR'

TIME_ZONE = 'America/Porto_Velho'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = '/static/' # Precisa da barra inicial
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')

# Configuração WhiteNoise para Alta Performance (Fluidez no carregamento de CSS/JS)
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Arquivos de midia!
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'

# Sistema de mensagem
MESSAGE_STORAGE = 'django.contrib.messages.storage.session.SessionStorage'

# Opcional: Configurações de nível de mensagens
MESSAGE_TAGS = {
    message_constants.DEBUG: 'debug',
    message_constants.INFO: 'info',
    message_constants.SUCCESS: 'success',
    message_constants.WARNING: 'warning',
    message_constants.ERROR: 'error',
}