from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from django.shortcuts import render

from app import views as app_views


def home(request):
    return render(request, 'home.html')


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),

    # Usuarios
    path(
        'usuarios/cadastro/',
        app_views.cadastro,
        name='cadastro'
    ),
    path(
        'usuarios/login/',
        auth_views.LoginView.as_view(
            template_name='usuarios/login.html'
        ),
        name='login'
    ),
    path(
        'usuarios/logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
    path(
        'usuarios/perfil/',
        app_views.perfil,
        name='perfil'
    ),
    path(
        'usuarios/alterar-senha/',
        app_views.alterar_senha,
        name='alterar_senha'
    ),

    # Administrativo
    path(
        'administrativo/',
        app_views.administrativo_index,
        name='administrativo_index'
    ),

    # Financeiro
    path(
        'financeiro/',
        app_views.index,
        name='financeiro_index'
    ),

    # Receitas
    path(
        'receitas/',
        app_views.receita_listar,
        name='receita_listar'
    ),

    path(
        'receitas/cadastrar/',
        app_views.receita_cadastrar,
        name='receita_cadastrar'
    ),

    path(
        'receitas/editar/<int:id>/',
        app_views.receita_editar,
        name='receita_editar'
    ),

    path(
        'receitas/excluir/<int:id>/',
        app_views.receita_excluir,
        name='receita_excluir'
    ),

    # Despesas
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

    # Categorias
    path(
        'categorias/',
        app_views.categoria_listar,
        name='categoria_listar'
    ),
]