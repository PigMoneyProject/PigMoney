# ==========================================
# TEMPLATE TAGS PERSONALIZADOS DO PIGMONEY
# ==========================================
# Template tags são funções que podemos chamar dentro
# dos templates HTML. O Django já oferece filtros prontos
# (como |date e |floatformat), mas a formatação de moeda
# no padrão brasileiro (R$ 1.250,00) não existe por
# padrão, então criamos a nossa própria.
#
# Para usar em um template:
#   1. Carregue o arquivo: {% load pigmoney_extras %}
#   2. Aplique o filtro:   {{ valor|moeda }}
# ==========================================

from decimal import Decimal, InvalidOperation

from django import template

# register é o registro oficial de tags/filtros do Django.
# Toda tag customizada precisa ser registrada nele.
register = template.Library()


@register.filter(name='moeda')
def moeda(valor):
    """
    Formata um valor numérico no padrão brasileiro de moeda.

    Exemplos:
      1250      -> "R$ 1.250,00"
      800.50    -> "R$ 800,50"
      -150      -> "- R$ 150,00"
      None      -> "R$ 0,00"

    Como funciona:
      - Decimal() garante precisão exata (nunca usar float
        com dinheiro, pois 0.1 + 0.2 != 0.3 em float).
      - O formato ',.2f' coloca separador de milhar (,)
        e 2 casas decimais: "1,250.00" (padrão americano).
      - As substituições trocam os separadores para o
        padrão brasileiro: "1.250,00".
        O 'T' é apenas um marcador temporário para não
        confundir o ponto com a vírgula na troca.
    """
    try:
        # Tenta converter para Decimal (aceita int, float, str, Decimal).
        valor = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        # Se vier vazio ou inválido, assume zero em vez de quebrar.
        valor = Decimal('0')

    if valor < 0:
        # Valores negativos: "- R$ 150,00" (mais legível em relatórios).
        return f"- R$ {abs(valor):,.2f}".replace(',', 'T').replace('.', ',').replace('T', '.')

    return f"R$ {valor:,.2f}".replace(',', 'T').replace('.', ',').replace('T', '.')


@register.filter(name='porcentagem')
def porcentagem(valor, casas=1):
    """
    Formata um número como porcentagem com vírgula decimal.

    Exemplo: 37.5 -> "37,5%"

    O parâmetro "casas" define as casas decimais (padrão: 1).
    """
    try:
        valor = Decimal(str(valor))
    except (InvalidOperation, TypeError, ValueError):
        valor = Decimal('0')

    # quantiza fixa o número de casas decimais (ex: 37.50 -> 37.5).
    valor = valor.quantize(Decimal('0.' + '0' * (int(casas) - 1) + '1'))
    # Substitui o ponto decimal pela vírgula do padrão pt-BR.
    return f'{valor}%'.replace('.', ',')


@register.filter(name='index')
def index(lista, i):
    """
    Retorna o item da posição "i" de uma lista.

    O Django não permite acessar listas por índice diretamente
    no template (ex: lista[0]), então usamos este filtro:

      {{ minha_lista|index:0 }}

    No relatório, ele permite cruzar listas paralelas
    (meses, receitas, despesas) que vêm da mesma consulta.
    """
    try:
        return lista[int(i)]
    except (IndexError, TypeError, ValueError):
        # Índice inválido: retorna vazio em vez de quebrar.
        return None
