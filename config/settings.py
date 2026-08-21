import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent.parent


SECRET_KEY = 'SUA_SECRET_KEY'

DEBUG = True #faz o Django mostrar erros detalhados durante o desenvolvimento.

ALLOWED_HOSTS = []#determina quais endereços podem acessar o sistema quando ele for publicado.


INSTALLED_APPS = [
    'django.contrib.admin', #Fornece o painel administrativo do Django.
    'django.contrib.auth',#Fornece o sistema de:usuários, login,senha, permissões.
    'django.contrib.contenttypes',#Gerenciamento interno dos Models
    'django.contrib.sessions',#Mantém o usuário conectado
    'django.contrib.messages',#Mensagens como "Cadastro realizado com sucesso"
    'django.contrib.staticfiles',#CSS, JavaScript e imagens

    'app', #É a aplicação
]
#utilizamos o sistema de autenticação fornecido pelo próprio Django e criamos formulários, views e templates para adaptá-lo às necessidades do PigMoney.

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',#mantém a sessão do usuário.
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',#permite que o Django saiba quem está logado neste momento
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


ROOT_URLCONF = 'config.urls'#rota para a urls


TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',

        'DIRS': [
            BASE_DIR / 'app' / 'templates',
        ],

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


WSGI_APPLICATION = 'config.wsgi.application'

#conexao com o django ao postegreSQL
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'PigMoney',
        'USER': 'postgres',
        'PASSWORD': '123456',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_TZ = True


STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'app' / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/usuarios/login/'#se nao estiver logado vai para a tela de login 
LOGIN_REDIRECT_URL = '/financeiro/'#se ja tiver realizado o login vai para a tela principal
LOGOUT_REDIRECT_URL = '/usuarios/login/'#se desconectar vai para a tela de login novamente