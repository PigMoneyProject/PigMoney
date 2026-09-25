
# Este arquivo configura como os Models aparecem
# no painel administrativo do Django (/admin/).
#
# O @admin.register(Model) registra a classe de admin
# para aquele Model específico, definindo quais campos
# aparecem na listagem, filtros e busca.


from django.contrib import admin
from .models import Categoria, Receita, Despesa, MetaFinanceira, PlanejamentoMensal


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    """
    Configura a exibição de Categorias no painel admin.

    O campo 'usuario' indica:
    - vazio (NULL) = categoria padrão (visível para todos)
    - preenchido = categoria personalizada daquele usuário
    """
    list_display = ['id_categoria', 'nome_categoria', 'descricao', 'usuario']
    search_fields = ['nome_categoria']
    # Filtro lateral para separar padrão vs personalizada.
    list_filter = ['usuario']


@admin.register(Receita)
class ReceitaAdmin(admin.ModelAdmin):
    """Configura a exibição de Receitas no painel admin."""
    list_display = ['id_receita', 'descricao', 'valor', 'data_receita', 'usuario', 'categoria']
    # Filtros laterais na página de listagem.
    list_filter = ['categoria', 'data_receita']
    search_fields = ['descricao']


@admin.register(Despesa)
class DespesaAdmin(admin.ModelAdmin):
    """Configura a exibição de Despesas no painel admin."""
    list_display = ['id_despesa', 'descricao', 'valor', 'data_despesa', 'usuario', 'categoria']
    list_filter = ['categoria', 'data_despesa']
    search_fields = ['descricao']


@admin.register(MetaFinanceira)
class MetaFinanceiraAdmin(admin.ModelAdmin):
    """Configura a exibição de Metas no painel admin."""
    list_display = ['id_meta', 'nome_meta', 'valor_objetivo', 'valor_atual', 'prazo', 'usuario']
    list_filter = ['prazo', 'usuario']
    search_fields = ['nome_meta']


@admin.register(PlanejamentoMensal)
class PlanejamentoMensalAdmin(admin.ModelAdmin):
    """Configura a exibição do Planejamento Mensal no painel admin."""
    list_display = ['id_planejamento', 'mes', 'ano', 'limite_gastos', 'usuario']
    list_filter = ['mes', 'ano']
    search_fields = ['usuario__username']
