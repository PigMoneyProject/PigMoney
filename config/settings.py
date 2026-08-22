# ==========================================
# CONFIGURAÇÕES DO PROJETO PIGMONEY
# ==========================================
# Este arquivo é o coração da configuração do Django.
# Ele define tudo que o projeto precisa para funcionar:
# banco de dados, aplicativos instalados, templates,
# idioma, autenticação e redirecionamentos.
# ==========================================

import os
from pathlib import Path


# Caminho absoluto da pasta raiz do projeto.
# O BASE_DIR é utilizado em várias configurações para
# encontrar pastas como templates e arquivos estáticos.
BASE_DIR = Path(__file__).resolve().parent.parent


# Chave secreta utilizada pelo Django para assinar cookies,
# gerar tokens CSRF e outras funções de segurança.
# Em produção, NUNCA deve ficar exposta no código.
SECRET_KEY = 'SUA_SECRET_KEY'


# Quando DEBUG=True, o Django mostra páginas de erro detalhadas.
# Em produção, deve ser False para não expor informações sensíveis.
DEBUG = True


# Lista de endereços/IPs autorizados a acessar o sistema.
# Quando vazio, apenas localhost é permitido (desenvolvimento).
ALLOWED_HOSTS = []


# ==========================================
# APLICATIVOS INSTALADOS
# ==========================================
# Lista de todos os módulos que o Django carrega.
# Os apps do "django.contrib" são fornecidos pelo próprio Django.
INSTALLED_APPS = [
    'django.contrib.admin',          # Painel administrativo (/admin/)
    'django.contrib.auth',           # Sistema de autenticação: usuários, login, senhas, permissões
    'django.contrib.contenttypes',   # Gerencia os tipos de conteúdo dos Models internamente
    'django.contrib.sessions',       # Mantém o usuário conectado entre requisições (sessão)
    'django.contrib.messages',       # Sistema de mensagens (ex: "Cadastro realizado com sucesso!")
    'django.contrib.staticfiles',    # Gerencia arquivos estáticos (CSS, JavaScript, imagens)

    'app',                           # Nosso aplicativo principal do PigMoney
]


# ==========================================
# MIDDLEWARES
# ==========================================
# São camadas de processamento que cada requisição HTTP
# passa antes de chegar à View. Cada middleware tem uma
# função específica na cadeia de processamento.
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',        # Cria e mantém a sessão do usuário
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',                  # Protege contra ataques CSRF
    'django.contrib.auth.middleware.AuthenticationMiddleware',     # Identifica quem está logado em cada requisição
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


# Indica qual arquivo contém a lista de URLs do projeto.
ROOT_URLCONF = 'config.urls'


# ==========================================
# TEMPLATES
# ==========================================
# Configura onde o Django procura os arquivos HTML (templates).
# DIRS: pastas adicionais de templates (fora dos apps).
# APP_DIRS: permite que cada app tenha sua pasta "templates/".
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
                'django.contrib.auth.context_processors.auth',    # Torna "user" disponível em todos os templates
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]


# Ponto de entrada WSGI para servidores de produção (Apache, Nginx).
WSGI_APPLICATION = 'config.wsgi.application'


# ==========================================
# BANCO DE DADOS (PostgreSQL)
# ==========================================
# Configura a conexão com o banco de dados PostgreSQL.
# O Django utiliza um ORM (Object-Relational Mapping) para
# traduzir os Models Python em tabelas do banco de dados.
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'PigMoney',         # Nome do banco de dados no PostgreSQL
        'USER': 'postgres',         # Usuário do banco
        'PASSWORD': '123456',       # Senha do banco
        'HOST': 'localhost',        # Servidor (local durante desenvolvimento)
        'PORT': '5432',             # Porta padrão do PostgreSQL
    }
}


# ==========================================
# VALIDADORES DE SENHA
# ==========================================
# Regras que o Django aplica automaticamente quando
# o usuário cria ou altera a senha. Protege contas
# contra senhas fracas, curtas ou repetitivas.
AUTH_PASSWORD_VALIDATORS = [
    {
        # Impede que a senha seja muito parecida com dados pessoais
        # (nome de usuário, nome completo, e-mail).
        'NAME':
        'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        # Exige um número mínimo de caracteres na senha.
        'NAME':
        'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        # Impede senhas muito comuns (ex: "123456", "password").
        'NAME':
        'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        # Impede senhas formadas apenas por números.
        'NAME':
        'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Idioma padrão do sistema (afeta mensagens do Django).
LANGUAGE_CODE = 'pt-br'

# Fuso horário utilizado pelo projeto.
TIME_ZONE = 'America/Sao_Paulo'

# Ativa o sistema de internacionalização do Django.
USE_I18N = True

# Utiliza timezone-aware datetimes (recomendado).
USE_TZ = True


# ==========================================
# ARQUIVOS ESTÁTICOS
# ==========================================
# STATIC_URL: URL base para acessar arquivos estáticos no navegador.
# STATICFILES_DIRS: pastas adicionais onde o Django procura arquivos estáticos.
# STATIC_ROOT: pasta destino quando executamos "collectstatic" (produção).
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    BASE_DIR / 'app' / 'static',
]

STATIC_ROOT = BASE_DIR / 'staticfiles'


# Tipo de campo autoincremental padrão para novos Models.
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==========================================
# CONFIGURAÇÕES DE AUTENTICAÇÃO
# ==========================================
# Define para onde o Django redireciona o usuário
# dependendo da situação de login/logout.

# URL exibida quando um usuário tenta acessar uma página
# que exige login (protegida por @login_required).
LOGIN_URL = '/usuarios/login/'

# URL para onde o usuário vai após realizar login com sucesso.
LOGIN_REDIRECT_URL = '/financeiro/'

# URL para onde o usuário vai após realizar logout.
LOGOUT_REDIRECT_URL = '/usuarios/login/'
