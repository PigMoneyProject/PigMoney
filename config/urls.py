# ==========================================
# MAPA DE ROTAS (URLs) DO PIGMONEY
# ==========================================
# Este arquivo funciona como um mapa de endereços.
# Quando o usuário acessa uma URL no navegador,
# o Django verifica este arquivo para descobrir
# qual função (View) deve processar aquela requisição.
#
# Cada "path()" associa:
#   - um endereço (URL)
#   - uma função que vai executar (View)
#   - um nome único para referenciar nos templates
#
# O parâmetro "name" permite usar {% url 'nome' %}
# nos templates, em vez de digitar o endereço inteiro.
# Exemplo: {% url 'login' %} gera /usuarios/login/
# ==========================================

from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views  # Views nativas do Django para login e logout
from django.shortcuts import render

from app import views as app_views  # Nosso arquivo views.py do aplicativo "app"


def home(request):
    """Exibe a página inicial do PigMoney (pública)."""
    return render(request, 'home.html')


def saiba_mais(request):
    """Exibe a página 'Saiba Mais' que apresenta o projeto (pública)."""
    return render(request, 'saiba_mais.html')


urlpatterns = [
    # Painel administrativo do Django (acesso restrito a superusuários).
    path('admin/', admin.site.urls),

    # ── Páginas públicas ─────────────────────────────
    # Página inicial (raiz do site).
    path('', home, name='home'),

    # Página de apresentação do projeto (visitantes).
    path('saiba-mais/', saiba_mais, name='saiba_mais'),

    # ── Usuários ─────────────────────────────────────
    # Cadastro de novo usuário. A view cadastro está no views.py.
    path(
        'usuarios/cadastro/',
        app_views.cadastro,
        name='cadastro'
    ),

    # Login: usa a view nativa do Django (LoginView).
    # O parâmetro template_name indica qual HTML usar para o formulário.
    path(
        'usuarios/login/',
        auth_views.LoginView.as_view(
            template_name='usuarios/login.html'
        ),
        name='login'
    ),

    # Logout: usa a view nativa do Django (LogoutView).
    # Após logout, o usuário é redirecionado para LOGOUT_REDIRECT_URL.
    path(
        'usuarios/logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),

    # Perfil do usuário: exibe e permite editar dados pessoais.
    path(
        'usuarios/perfil/',
        app_views.perfil,
        name='perfil'
    ),

    # Alteração de senha: usa o PasswordChangeForm do Django.
    path(
        'usuarios/alterar-senha/',
        app_views.alterar_senha,
        name='alterar_senha'
    ),

    # ── Área administrativa ──────────────────────────
    # Acesso restrito a usuários com is_staff=True.
    path(
        'administrativo/',
        app_views.administrativo_index,
        name='administrativo_index'
    ),

    # ── Dashboard financeiro ─────────────────────────
    # Página principal do usuário logado (exige autenticação).
    path(
        'financeiro/',
        app_views.index,
        name='financeiro_index'
    ),

    # ── Receitas ─────────────────────────────────────
    # Listagem de receitas do usuário logado.
    path(
        'receitas/',
        app_views.receita_listar,
        name='receita_listar'
    ),

    # Formulário para cadastrar uma nova receita.
    path(
        'receitas/cadastrar/',
        app_views.receita_cadastrar,
        name='receita_cadastrar'
    ),

    # Editar uma receita específica pelo seu ID.
    # <int:id> captura um número inteiro da URL e passa como parâmetro "id" à view.
    path(
        'receitas/editar/<int:id>/',
        app_views.receita_editar,
        name='receita_editar'
    ),

    # Confirmar exclusão de uma receita específica.
    path(
        'receitas/excluir/<int:id>/',
        app_views.receita_excluir,
        name='receita_excluir'
    ),

    # ── Despesas ─────────────────────────────────────
    # A estrutura é idêntica às receitas, mas para despesas.
    path(
        'despesas/',
        app_views.despesa_listar,
        name='despesa_listar'
    ),

    path(
        'despesas/cadastrar/',
        app_views.despesa_cadastrar,
        name='despesa_cadastrar'
    ),

    path(
        'despesas/editar/<int:id>/',
        app_views.despesa_editar,
        name='despesa_editar'
    ),

    path(
        'despesas/excluir/<int:id>/',
        app_views.despesa_excluir,
        name='despesa_excluir'
    ),

    # ── Categorias ───────────────────────────────────
    # Lista categorias padrão + personalizadas do usuário logado.
    path(
        'categorias/',
        app_views.categoria_listar,
        name='categoria_listar'
    ),

    # Formulário para cadastrar uma nova categoria personalizada.
    path(
        'categorias/cadastrar/',
        app_views.categoria_cadastrar,
        name='categoria_cadastrar'
    ),

    # Editar uma categoria pessoal do usuário logado.
    path(
        'categorias/editar/<int:id>/',
        app_views.categoria_editar,
        name='categoria_editar'
    ),

    # Confirmar exclusão de uma categoria pessoal.
    path(
        'categorias/excluir/<int:id>/',
        app_views.categoria_excluir,
        name='categoria_excluir'
    ),
]
