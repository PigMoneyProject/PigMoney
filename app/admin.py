from django.contrib import admin
from .models import Categoria, Receita, Despesa


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['id_categoria', 'nome_categoria', 'descricao']
    search_fields = ['nome_categoria']


@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    list_display = ['id_receita', 'descricao', 'valor', 'data_receita', 'usuario', 'categoria']
    list_filter = ['categoria', 'data_receita']
    search_fields = ['descricao']


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    list_display = ['id_despesa', 'descricao', 'valor', 'data_despesa', 'usuario', 'categoria']
    list_filter = ['categoria', 'data_despesa']
    search_fields = ['descricao']
