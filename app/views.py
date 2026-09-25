# ==========================================
# VIEWS DO PIGMONEY
# ==========================================
# Uma View é uma função Python que recebe uma requisição HTTP
# do navegador, processa os dados necessários e retorna uma
# resposta (geralmente uma página HTML ou um redirecionamento).
#
# Fluxo típico:
#   URL → View → Form/Model → Banco de Dados → Template HTML
#
# Parâmetros importantes:
#   - request: objeto que representa tudo o que o navegador enviou
#     (dados do formulário, usuário logado, método HTTP, etc.)
#   - request.method: indica se a requisição é GET (abrir página)
#     ou POST (enviar formulário)
#   - request.user: o usuário autenticado no momento (disponível
#     automaticamente pelo Django)
#
# Funções principais do Django utilizadas:
#   - render(): abre um template HTML e retorna como resposta
#   - redirect(): redireciona o navegador para outra URL
#   - get_object_or_404(): busca um registro no banco e retorna
#     erro 404 (não encontrado) se não existir
# ==========================================

from django.shortcuts import render, redirect, get_object_or_404

# Decoretors (decoradores) são utilizados antes das views para
# adicionar comportamento extra. Exemplos:
#   @login_required → exige que o usuário esteja logado
#   @user_passes_test → verifica uma regra de permissão customizada
from django.contrib.auth.decorators import login_required, user_passes_test

# Sum é utilizado pelo ORM do Django para somar valores no banco.
# aggregate retorna um resultado agregado sobre vários registros.
from django.db.models import Sum

# Função login() do Django: autentica o usuário e cria a sessão.
from django.contrib.auth import login

# Formulário nativo do Django para alteração de senha.
from django.contrib.auth.forms import PasswordChangeForm

# Mantém a sessão ativa após alterar a senha (evita deslogar o usuário).
from django.contrib.auth import update_session_auth_hash

# Sistema de mensagens do Django (sucesso, erro, etc.).
from django.contrib import messages

# Models do nosso projeto (estrutura dos dados no banco).
from .models import Receita, Despesa, Categoria, MetaFinanceira, PlanejamentoMensal

# Forms do nosso projeto (formulários para criar/editar dados).
from .forms import (
    ReceitaForm,
    DespesaForm,
    CadastroForm,
    PerfilForm,
    CategoriaForm,
    MetaFinanceiraForm,
    PlanejamentoMensalForm,
)

# date: fornece a data de hoje (date.today()) para filtrar por período.
from datetime import date

# json: converte listas/dicionários Python em texto JSON.
# Utilizamos para enviar os dados dos gráficos ao JavaScript (Chart.js).
import json

# Lista com os nomes dos meses em português.
# O índice 0 é deixado vazio porque os meses vão de 1 (Janeiro) a 12 (Dezembro).
MESES_PT = [
    '', 'Janeiro', 'Fevereiro', 'Marco', 'Abril', 'Maio', 'Junho',
    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro'
]

# Q permite criar consultas com OR (|) no Django ORM.
# Sem Q, só seria possível filtrar com AND.
from django.db.models import Q

# models é necessário para acessar ProtectedError na exclusão de categorias.
from django.db import models


# ==========================================
# DASHBOARD FINANCEIRO
# ==========================================

@login_required  # Somente usuários logados podem acessar esta página.
def index(request):
    """
    Dashboard financeiro principal do usuário logado.

    Exibe de forma organizada:
    - Saldo atual (receitas - despesas)
    - Total e quantidade de receitas
    - Total e quantidade de despesas
    - Movimentações recentes
    - Metas financeiras
    - Planejamento mensal do mês atual
    - Dados para os gráficos (Chart.js)

    IMPORTANTE: todos os dados são filtrados por request.user,
    então cada usuário vê APENAS os próprios registros.
    """

    # ── RECEITAS ──
    # Filtra somente as receitas do usuário autenticado.
    # NÃO usar .all(), pois somaria dados de todos os usuários.
    receitas_usuario = Receita.objects.filter(usuario=request.user)

    # aggregate(Sum('valor')) soma o campo 'valor' de todos os registros encontrados.
    # O resultado é um dicionário: {'total': Decimal('3000.00')} ou {'total': None}.
    # O "or 0" garante que, se o usuário não tiver receitas, o valor seja 0 em vez de None.
    total_receitas = receitas_usuario.aggregate(
        total=Sum('valor')
    )['total'] or 0

    # count() conta quantos registros existem na consulta.
    # Usamos para mostrar "quantidade de receitas cadastradas".
    quantidade_receitas = receitas_usuario.count()

    # ── DESPESAS ──
    # Mesma lógica: filtra despesas apenas do usuário logado.
    despesas_usuario = Despesa.objects.filter(usuario=request.user)

    total_despesas = despesas_usuario.aggregate(
        total=Sum('valor')
    )['total'] or 0

    quantidade_despesas = despesas_usuario.count()

    # ── SALDO ──
    # Cálculo simples: receitas menos despesas.
    # Pode resultar em valor positivo, zero ou negativo.
    saldo = total_receitas - total_despesas

    # ── MOVIMENTAÇÕES RECENTES ──
    # Combina receitas e despesas em uma única lista para exibir
    # na seção "Movimentações recentes" do Dashboard.
    movimentacoes = montar_movimentacoes(receitas_usuario, despesas_usuario)
    # [:8] pega somente as 8 movimentações mais recentes.
    movimentacoes_recentes = movimentacoes[:8]

    # ── PERÍODO ATUAL (MÊS) ──
    # data.today() retorna a data de hoje (ex: 2026-09-25).
    hoje = date.today()

    # Despesas do mês atual: usadas para comparar com o limite planejado.
    despesas_mes = despesas_usuario.filter(
        data_despesa__year=hoje.year,
        data_despesa__month=hoje.month
    )

    # ── METAS (para exibir no Dashboard) ──
    metas = MetaFinanceira.objects.filter(usuario=request.user)

    # ── PLANEJAMENTO MENSAL DO MÊS ATUAL ──
    planejamento_atual = PlanejamentoMensal.objects.filter(
        usuario=request.user,
        mes=hoje.month,
        ano=hoje.year
    ).first()  # .first() retorna o registro ou None (se não existir).

    # Dados do planejamento para o template (ou 0 se não houver).
    dados_planejamento = calcular_planejamento(planejamento_atual, despesas_mes)

    # ── DADOS DOS GRÁFICOS (Chart.js) ──
    # Chamamos funções auxiliares que preparam as listas de dados.
    # json.dumps() converte a lista Python em texto JSON para o JavaScript ler.
    dados_graficos = preparar_dados_graficos(request.user)

    # Contexto: dicionário enviado ao template com os valores calculados.
    contexto = {
        'total_receitas': total_receitas,
        'total_despesas': total_despesas,
        'quantidade_receitas': quantidade_receitas,
        'quantidade_despesas': quantidade_despesas,
        'saldo': saldo,
        'movimentacoes_recentes': movimentacoes_recentes,
        'metas': metas,
        'dados_planejamento': dados_planejamento,
        'grafico_meses': dados_graficos['meses'],
        'grafico_receitas': dados_graficos['receitas'],
        'grafico_despesas': dados_graficos['despesas'],
        'grafico_saldo_acumulado': dados_graficos['saldo_acumulado'],
        'grafico_categorias_rotulos': dados_graficos['categorias_rotulos'],
        'grafico_categorias_valores': dados_graficos['categorias_valores'],
    }

    return render(request, 'financeiro/index.html', contexto)


def montar_movimentacoes(receitas, despesas):
    """
    Função auxiliar que combina receitas e despesas em UMA lista.

    Cada item da lista é um dicionário com os campos comuns:
    tipo, descricao, categoria, data e valor.

    Retorno: lista ordenada da mais recente para a mais antiga.
    """
    movimentacoes = []

    # Percorre cada receita e cria um dicionário padronizado.
    for receita in receitas:
        movimentacoes.append({
            'tipo': 'Receita',
            'descricao': receita.descricao,
            'categoria': receita.categoria.nome_categoria,
            'data': receita.data_receita,
            'valor': receita.valor,
        })

    # Mesma lógica para despesas.
    for despesa in despesas:
        movimentacoes.append({
            'tipo': 'Despesa',
            'descricao': despesa.descricao,
            'categoria': despesa.categoria.nome_categoria,
            'data': despesa.data_despesa,
            'valor': despesa.valor,
        })

    # Ordena pela chave 'data' em ordem decrescente (mais recente primeiro).
    # reverse=True inverte a ordenação natural (que seria crescente).
    movimentacoes.sort(key=lambda m: m['data'], reverse=True)

    return movimentacoes


def calcular_planejamento(planejamento, despesas_mes):
    """
    Função auxiliar que calcula os valores do planejamento mensal.

    Recebe:
    - planejamento: objeto PlanejamentoMensal (ou None)
    - despesas_mes: queryset de despesas do mês selecionado

    Retorna um dicionário com limite, gasto, restante e percentual.
    """
    # Se não existe planejamento, o limite é 0 (não definido).
    limite = planejamento.limite_gastos if planejamento else 0

    total_gasto = despesas_mes.aggregate(
        total=Sum('valor')
    )['total'] or 0

    # Restante = limite menos o que já se gastou no mês.
    restante = limite - total_gasto

    # Percentual do limite que já foi utilizado.
    # Proteção contra divisão por zero (limite = 0).
    # round(..., 1) limita a 1 casa decimal para não exibir
    # dízimas longas (ex: 62.6666...).
    if limite > 0:
        percentual_utilizado = round(
            (total_gasto / limite) * 100, 1
        )
    else:
        percentual_utilizado = 0

    return {
        'limite': limite,
        'total_gasto': total_gasto,
        'restante': restante,
        'percentual_utilizado': percentual_utilizado,
    }


def preparar_dados_graficos(usuario):
    """
    Função auxiliar que prepara os dados reais para os gráficos.

    Retorna um dicionário com listas JSON já serializadas:
    - meses: rótulos dos últimos 6 meses (ex: "Set/2026")
    - receitas: total de receitas por mês
    - despesas: total de despesas por mês
    - saldo_acumulado: saldo acumulado mês a mês
    - categorias_rotulos / categorias_valores: despesas por categoria

    IMPORTANTE: todos os dados são filtrados pelo usuário logado
    e vêm do banco de dados (nada de valores fictícios).
    """
    hoje = date.today()

    # ── DESPESAS POR CATEGORIA (gráfico de pizza) ──
    # Agrupa as despesas do usuário por categoria e soma os valores.
    # Usamos o ORM values() + annotate() para agrupar no banco de dados.
    despesas_por_categoria = (
        Despesa.objects
        .filter(usuario=usuario)
        .values('categoria__nome_categoria')  # Agrupa pelo nome da categoria.
        .annotate(total=Sum('valor'))          # Soma os valores de cada grupo.
    )

    # Separamos em duas listas: rótulos (nomes) e valores (totais).
    categorias_rotulos = []
    categorias_valores = []

    for item in despesas_por_categoria:
        categorias_rotulos.append(item['categoria__nome_categoria'])
        # float() converte Decimal para número "comum" (necessário p/ JSON).
        categorias_valores.append(float(item['total']))

    # ── EVOLUÇÃO NOS ÚLTIMOS 6 MESES ──
    # Montamos uma lista com os (mês, ano) dos últimos 6 meses,
    # começando do mais antigo até o atual, para exibir nos eixos.
    meses_lista = []
    for i in range(5, -1, -1):  # 5, 4, 3, 2, 1, 0
        # Para calcular o mês anterior, subtraímos meses de hoje.
        # Total de meses desde o ano 1: (ano * 12) + mes - 1.
        indice = (hoje.year * 12) + (hoje.month - 1) - i
        ano = indice // 12
        mes = (indice % 12) + 1
        meses_lista.append((mes, ano))

    meses_rotulos = []
    receitas_meses = []
    despesas_meses = []
    saldo_acumulado = []
    saldo_soma = 0

    # Para cada mês dos últimos 6, calculamos receitas e despesas.
    for mes, ano in meses_lista:
        # MESES_PT[mes] retorna o nome do mês em português (ex: 'Setembro').
        # [:3] mantém apenas as 3 primeiras letras (ex: 'Set').
        meses_rotulos.append(f'{MESES_PT[mes][:3]}/{ano}')

        total_rec = Receita.objects.filter(
            usuario=usuario, data_receita__month=mes, data_receita__year=ano
        ).aggregate(total=Sum('valor'))['total'] or 0

        total_des = Despesa.objects.filter(
            usuario=usuario, data_despesa__month=mes, data_despesa__year=ano
        ).aggregate(total=Sum('valor'))['total'] or 0

        receitas_meses.append(float(total_rec))
        despesas_meses.append(float(total_des))

        # Saldo acumulado: soma o saldo de cada mês ao anterior.
        # Exemplo: saldo dos meses 1+2, depois 1+2+3, e assim por diante.
        saldo_soma += float(total_rec - total_des)
        saldo_acumulado.append(saldo_soma)

    # json.dumps() transforma as listas Python em texto JSON.
    # No template, usamos |safe para o navegador interpretar como código.
    return {
        'meses': json.dumps(meses_rotulos),
        'receitas': json.dumps(receitas_meses),
        'despesas': json.dumps(despesas_meses),
        'saldo_acumulado': json.dumps(saldo_acumulado),
        'categorias_rotulos': json.dumps(categorias_rotulos),
        'categorias_valores': json.dumps(categorias_valores),
    }


# ==========================================
# USUÁRIOS: CADASTRO
# ==========================================

def cadastro(request):
    """
    View de cadastro de novo usuário.

    Fluxo:
    1. Se o usuário já está logado, redireciona para o dashboard.
    2. Se o método for POST (formulário enviado):
       - Preenche o CadastroForm com os dados recebidos.
       - Se válidos, cria o usuário no banco e faz login automático.
    3. Se o método for GET (abrir a página):
       - Exibe o formulário vazio para preenchimento.
    """
    # Usuário já autenticado não precisa se cadastrar novamente.
    if request.user.is_authenticated:
        return redirect('financeiro_index')

    if request.method == 'POST':
        # request.POST contém todos os campos enviados no formulário.
        form = CadastroForm(request.POST)
        if form.is_valid():  # Valida: senhas iguais, e-mail válido, username único, etc.
            user = form.save()          # Salva o novo usuário no banco (senha em hash).
            login(request, user)        # Autentica o usuário automaticamente.
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('financeiro_index')
    else:
        # GET: exibe o formulário de cadastro vazio.
        form = CadastroForm()

    return render(request, 'usuarios/cadastro.html', {'form': form})


# ==========================================
# USUÁRIOS: PERFIL
# ==========================================

@login_required
def perfil(request):
    """
    Exibe e permite editar os dados do perfil do usuário logado.

    instance=request.user faz com que o formulário seja preenchido
    automaticamente com os dados atuais do usuário.
    """
    if request.method == 'POST':
        # instance=request.user: diz ao formulário para editar ESTE usuário.
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()  # Salva as alterações no banco de dados.
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
    else:
        # GET: exibe o formulário com os dados preenchidos.
        form = PerfilForm(instance=request.user)

    return render(request, 'usuarios/index.html', {'form': form})


# ==========================================
# USUÁRIOS: ALTERAÇÃO DE SENHA
# ==========================================

@login_required
def alterar_senha(request):
    """
    Permite ao usuário alterar sua senha.

    PasswordChangeForm pede: senha atual + nova senha + confirmação.
    update_session_auth_hash() mantém o usuário logado após a mudança.
    Sem essa função, o Django encerraria a sessão automaticamente.
    """
    if request.method == 'POST':
        # PasswordChangeForm precisa do usuário atual para verificar a senha antiga.
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()  # Salva a nova senha (armazenada em hash).
            # Atualiza a sessão para não deslogar o usuário.
            update_session_auth_hash(request, user)
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('perfil')
    else:
        form = PasswordChangeForm(request.user)

    return render(request, 'usuarios/alterar_senha.html', {'form': form})


# ==========================================
# ÁREA ADMINISTRATIVA (PERMISSÕES)
# ==========================================

def is_staff(user):
    """
    Função de verificação de permissão.
    Retorna True apenas se o usuário estiver autenticado
    E possuir is_staff=True (flag de administrador).

    is_staff é um campo nativo do model User do Django.
    Usuários comuns têm is_staff=False por padrão.
    """
    return user.is_authenticated and user.is_staff


@login_required  # Primeiro: precisa estar logado.
@user_passes_test(is_staff, login_url='/financeiro/')  # Segundo: precisa ser administrador.
def administrativo_index(request):
    """Área exclusiva para administradores do sistema."""
    return render(request, 'administrativo/index.html')


# ==========================================
# CRUD DE RECEITAS
# ==========================================
# CRUD = Create (criar), Read (ler), Update (atualizar), Delete (excluir)
#
# Todas as views de receitas filtram por usuario=request.user,
# garantindo que cada usuário só veja e gerencie suas próprias receitas.
# Isso é essencial para a segurança dos dados.

@login_required
def receita_listar(request):
    """
    Lista todas as receitas do usuário logado.

    Receita.objects.filter(usuario=request.user) busca no banco
    apenas as receitas onde o campo "usuario" é igual ao usuário
    autenticado. Isso evita que um usuário veja receitas de outros.
    """
    receitas = Receita.objects.filter(usuario=request.user)
    return render(request, 'financeiro/receitas/listar.html', {'receitas': receitas})


@login_required
def receita_cadastrar(request):
    """
    Cadastra uma nova receita.

    Fluxo:
    1. O formulário ReceitaForm contém: valor, descrição, data, categoria.
    2. commit=False cria o objeto SEM salvar no banco ainda.
    3. Definimos receita.usuario = request.user para associar ao logado.
    4. receita.save() salva finalmente no banco.
    """
    if request.method == 'POST':
        form = ReceitaForm(request.POST, usuario=request.user)
        if form.is_valid():
            # commit=False: cria o objeto mas NÃO salva no banco ainda.
            # Precisamos disso para atribuir o usuário antes de salvar.
            receita = form.save(commit=False)
            receita.usuario = request.user  # Associa a receita ao usuário logado.
            receita.save()                  # Agora salva no banco de dados.
            messages.success(request, 'Receita cadastrada com sucesso!')
            return redirect('receita_listar')
    else:
        form = ReceitaForm(usuario=request.user)

    return render(request, 'financeiro/receitas/cadastrar.html', {'form': form})


@login_required
def receita_editar(request, id):
    """
    Edita uma receita existente.

    get_object_or_404(Receita, id_receita=id, usuario=request.user):
    - Busca a receita pelo ID e pelo usuário logado.
    - Se não encontrar ou não pertencer ao usuário, retorna erro 404.
    - Isso garante que um usuário não possa editar receitas de outro.
    """
    receita = get_object_or_404(Receita, id_receita=id, usuario=request.user)

    if request.method == 'POST':
        # instance=receita: preenche o formulário com os dados atuais.
        form = ReceitaForm(request.POST, instance=receita, usuario=request.user)
        if form.is_valid():
            form.save()  # Salva as alterações no banco.
            messages.success(request, 'Receita atualizada com sucesso!')
            return redirect('receita_listar')
    else:
        form = ReceitaForm(instance=receita, usuario=request.user)

    return render(request, 'financeiro/receitas/editar.html', {
        'form': form,
        'receita': receita,
    })


@login_required
def receita_excluir(request, id):
    """
    Exclui uma receita após confirmação do usuário.

    No GET: exibe a página de confirmação com os dados da receita.
    No POST: confirma a exclusão e redireciona para a listagem.
    """
    receita = get_object_or_404(Receita, id_receita=id, usuario=request.user)

    if request.method == 'POST':
        receita.delete()  # Remove a receita do banco de dados.
        messages.success(request, 'Receita excluida com sucesso!')
        return redirect('receita_listar')

    return render(request, 'financeiro/receitas/excluir.html', {'receita': receita})


# ==========================================
# CRUD DE DESPESAS
# ==========================================
# A estrutura é idêntica às receitas. Cada despesa também
# pertence exclusivamente ao usuário autenticado.

@login_required
def despesa_listar(request):
    """Lista todas as despesas do usuário logado."""
    despesas = Despesa.objects.filter(usuario=request.user)
    return render(request, 'financeiro/despesas/listar.html', {'despesas': despesas})


@login_required
def despesa_cadastrar(request):
    """Cadastra uma nova despesa associada ao usuário logado."""
    if request.method == 'POST':
        form = DespesaForm(request.POST, usuario=request.user)
        if form.is_valid():
            despesa = form.save(commit=False)
            despesa.usuario = request.user
            despesa.save()
            messages.success(request, 'Despesa cadastrada com sucesso!')
            return redirect('despesa_listar')
    else:
        form = DespesaForm(usuario=request.user)

    return render(request, 'financeiro/despesas/cadastrar.html', {'form': form})


@login_required
def despesa_editar(request, id):
    """Edita uma despesa existente do usuário logado."""
    despesa = get_object_or_404(Despesa, id_despesa=id, usuario=request.user)

    if request.method == 'POST':
        form = DespesaForm(request.POST, instance=despesa, usuario=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Despesa atualizada com sucesso!')
            return redirect('despesa_listar')
    else:
        form = DespesaForm(instance=despesa, usuario=request.user)

    return render(request, 'financeiro/despesas/editar.html', {
        'form': form,
        'despesa': despesa,
    })


@login_required
def despesa_excluir(request, id):
    """Exclui uma despesa após confirmação."""
    despesa = get_object_or_404(Despesa, id_despesa=id, usuario=request.user)

    if request.method == 'POST':
        despesa.delete()
        messages.success(request, 'Despesa excluida com sucesso!')
        return redirect('despesa_listar')

    return render(request, 'financeiro/despesas/excluir.html', {'despesa': despesa})


# ==========================================
# CRUD DE CATEGORIAS
# ==========================================
# Categorias possuem dois tipos:
#   - PADRÃO: usuario=NULL, visível para todos, não editável por comuns.
#   - PERSONALIZADA: pertence a um usuário específico.
#
# A listagem mostra categorias padrão + personalizadas do usuário logado.
# Cadastro, edição e exclusão só afetam categorias pessoais.

@login_required
def categoria_listar(request):
    """
    Lista categorias padrão (usuario=NULL) e as personalizadas
    do usuário logado.

    Utiliza Q do Django para criar um filtro com OR:
      Q(usuario__isnull=True) → categorias padrão
      Q(usuario=request.user) → categorias pessoais do logado

    Sem Q, o Django só permite filtros com AND, que não serve aqui.
    """
    categorias = Categoria.objects.filter(
        Q(usuario__isnull=True) | Q(usuario=request.user)
    )

    # Separa em duas listas para exibir visualmente distintas.
    categorias_padrao = categorias.filter(usuario__isnull=True)
    categorias_pessoais = categorias.filter(usuario=request.user)

    return render(request, 'financeiro/categorias/listar.html', {
        'categorias_padrao': categorias_padrao,
        'categorias_pessoais': categorias_pessoais,
    })


@login_required
def categoria_cadastrar(request):
    """
    Cadastra uma nova categoria personalizada.

    commit=False permite definir o usuario ANTES de salvar.
    Isso garante que a categoria seja associada ao usuário logado.
    O campo 'usuario' não aparece no formulário (CategoriaForm).
    """
    if request.method == 'POST':
        form = CategoriaForm(request.POST, usuario=request.user)
        if form.is_valid():
            categoria = form.save(commit=False)
            categoria.usuario = request.user
            categoria.save()
            messages.success(request, 'Categoria cadastrada com sucesso!')
            return redirect('categoria_listar')
    else:
        form = CategoriaForm(usuario=request.user)

    return render(request, 'financeiro/categorias/cadastrar.html', {'form': form})


@login_required
def categoria_editar(request, id):
    """
    Edita uma categoria personalizada do usuário logado.

    get_object_or_404 com usuario=request.user garante que:
    - o usuário não edite categorias padrão (usuario=NULL)
    - o usuário não edite categorias de outros usuários
    Se o ID não pertencer ao usuário, retorna 404.
    """
    categoria = get_object_or_404(
        Categoria,
        id_categoria=id,
        usuario=request.user
    )

    if request.method == 'POST':
        form = CategoriaForm(request.POST, instance=categoria, usuario=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoria atualizada com sucesso!')
            return redirect('categoria_listar')
    else:
        form = CategoriaForm(instance=categoria, usuario=request.user)

    return render(request, 'financeiro/categorias/editar.html', {
        'form': form,
        'categoria': categoria,
    })


@login_required
def categoria_excluir(request, id):
    """
    Exclui uma categoria personalizada do usuário logado.

    Segurança:
    - Só permite excluir categorias do próprio usuário.
    - Categorias padrão não podem ser excluídas.

    PROTECT no model: se a categoria estiver sendo usada
    em receitas ou despesas, o banco impede a exclusão.
    Capturamos essa exceção e mostramos mensagem amigável.
    """
    categoria = get_object_or_404(
        Categoria,
        id_categoria=id,
        usuario=request.user
    )

    if request.method == 'POST':
        try:
            categoria.delete()
            messages.success(request, 'Categoria excluida com sucesso!')
        except models.ProtectedError:
            messages.error(
                request,
                'Nao e possivel excluir esta categoria porque ela '
                'esta sendo utilizada em uma receita ou despesa.'
            )
        return redirect('categoria_listar')

    return render(request, 'financeiro/categorias/excluir.html', {
        'categoria': categoria,
    })


# ==========================================
# CRUD DE METAS FINANCEIRAS
# ==========================================
# Mesmo padrão de segurança dos demais CRUDs:
# toda view filtra por usuario=request.user. Assim, um usuário
# nunca consegue ver, editar ou excluir uma meta de outro usuário,
# mesmo que digite o ID correto na URL.

@login_required
def meta_listar(request):
    """
    Lista todas as metas financeiras do usuário logado.
    """
    metas = MetaFinanceira.objects.filter(usuario=request.user)
    return render(request, 'financeiro/metas/listar.html', {'metas': metas})


@login_required
def meta_cadastrar(request):
    """
    Cadastra uma nova meta financeira.

    commit=False cria o objeto sem salvar, permitindo que
    definamos meta.usuario = request.user antes do save().
    """
    if request.method == 'POST':
        form = MetaFinanceiraForm(request.POST)
        if form.is_valid():
            meta = form.save(commit=False)
            meta.usuario = request.user  # Associa a meta ao usuário logado.
            meta.save()
            messages.success(request, 'Meta criada com sucesso!')
            return redirect('meta_listar')
    else:
        form = MetaFinanceiraForm()

    return render(request, 'financeiro/metas/cadastrar.html', {'form': form})


@login_required
def meta_editar(request, id):
    """
    Edita uma meta existente.

    get_object_or_404(MetaFinanceira, id_meta=id, usuario=request.user):
    busca a meta pelo ID E pelo usuário logado. Se a meta pertencer
    a outro usuário, retorna 404 (não encontrado).
    """
    meta = get_object_or_404(
        MetaFinanceira,
        id_meta=id,
        usuario=request.user
    )

    if request.method == 'POST':
        form = MetaFinanceiraForm(request.POST, instance=meta)
        if form.is_valid():
            form.save()
            messages.success(request, 'Meta atualizada com sucesso!')
            return redirect('meta_listar')
    else:
        form = MetaFinanceiraForm(instance=meta)

    return render(request, 'financeiro/metas/editar.html', {
        'form': form,
        'meta': meta,
    })


@login_required
def meta_excluir(request, id):
    """
    Exclui uma meta após confirmação do usuário.
    """
    meta = get_object_or_404(
        MetaFinanceira,
        id_meta=id,
        usuario=request.user
    )

    if request.method == 'POST':
        meta.delete()
        messages.success(request, 'Meta excluida com sucesso!')
        return redirect('meta_listar')

    return render(request, 'financeiro/metas/excluir.html', {'meta': meta})


# ==========================================
# PLANEJAMENTO MENSAL
# ==========================================

@login_required
def planejamento(request):
    """
    Página de planejamento financeiro mensal.

    O usuário define um limite de gastos para o mês e o sistema
    compara esse limite com o total de despesas do mês selecionado.

    Fluxo:
    1. Lê o mês/ano escolhido (GET) ou usa o mês atual.
    2. Busca (ou cria) o planejamento do usuário para aquele mês.
    3. Calcula: limite, total gasto, restante e percentual utilizado.
    """
    hoje = date.today()

    # ── MÊS SELECIONADO ──
    # O formulário de filtro envia 'mes_ano' no formato "YYYY-MM".
    # Se vier vazio (primeira visita), usamos o mês atual.
    mes_ano = request.GET.get('mes_ano', '')

    if mes_ano:
        anos_mes = mes_ano.split('-')
        ano = int(anos_mes[0])
        mes = int(anos_mes[1])
    else:
        ano = hoje.year
        mes = hoje.month

    # Converte o número do mês para o nome (ex: 9 -> 'Setembro').
    nome_mes = MESES_PT[mes]
    # Meses em português: lista com nome de cada mês para o seletor.
    meses_lista = [{'numero': n, 'nome': MESES_PT[n]}
                   for n in range(1, 13)]

    # ── BUSCA O PLANEJAMENTO EXISTENTE ──
    # .first() retorna o registro ou None. Quando não existe,
    # o formulário aparece vazio para o usuário definir o limite.
    planejamento_existente = PlanejamentoMensal.objects.filter(
        usuario=request.user,
        mes=mes,
        ano=ano
    ).first()

    # ── FORMULARIO (POST) ──
    # instance=planejamento_existente: se já existe, edita; senão, cria novo.
    if request.method == 'POST':
        form = PlanejamentoMensalForm(
            request.POST,
            instance=planejamento_existente
        )
        if form.is_valid():
            planejamento_salvo = form.save(commit=False)
            planejamento_salvo.usuario = request.user
            planejamento_salvo.mes = mes
            planejamento_salvo.ano = ano
            planejamento_salvo.save()
            messages.success(request, 'Planejamento salvo com sucesso!')
            return redirect('planejamento')
    else:
        form = PlanejamentoMensalForm(instance=planejamento_existente)

    # ── DESPESAS DO MÊS SELECIONADO ──
    # Filtra despesas do usuário logado dentro do mês/ano escolhido.
    despesas_mes = Despesa.objects.filter(
        usuario=request.user,
        data_despesa__year=ano,
        data_despesa__month=mes
    )

    # Cálculos do planejamento (limite vs gasto).
    dados = calcular_planejamento(planejamento_existente, despesas_mes)

    return render(request, 'financeiro/planejamento/index.html', {
        'form': form,
        'dados': dados,
        'nome_mes': nome_mes,
        'mes': mes,
        'ano': ano,
        'meses_lista': meses_lista,
    })


# ==========================================
# HISTORICO FINANCEIRO
# ==========================================

@login_required
def historico(request):
    """
    Página de histórico financeiro.

    Exibe TODAS as movimentações (receitas e despesas) do usuário,
    da mais recente para a mais antiga, com filtros opcionais:
    - Período (data inicial e final)
    - Tipo (Receita ou Despesa)
    - Categoria

    Todos os filtros consideram apenas usuário=request.user.
    """
    # ── FILTROS VINDOS DA URL (GET) ──
    # request.GET.get() lê os parâmetros enviados pelo formulário.
    tipo = request.GET.get('tipo', '')
    categoria_id = request.GET.get('categoria', '')
    data_inicio = request.GET.get('data_inicio', '')
    data_fim = request.GET.get('data_fim', '')

    # ── CONSULTAS BASE (sempre filtradas pelo usuário) ──
    receitas = Receita.objects.filter(usuario=request.user)
    despesas = Despesa.objects.filter(usuario=request.user)

    # ── APLICA FILTROS ──
    # Filtro por categoria (se o usuário escolheu uma).
    if categoria_id:
        receitas = receitas.filter(categoria_id=categoria_id)
        despesas = despesas.filter(categoria_id=categoria_id)

    # Filtro por período: colunas ">=" (maior ou igual) e "<=" (menor ou igual).
    if data_inicio:
        receitas = receitas.filter(data_receita__gte=data_inicio)
        despesas = despesas.filter(data_despesa__gte=data_inicio)

    if data_fim:
        receitas = receitas.filter(data_receita__lte=data_fim)
        despesas = despesas.filter(data_despesa__lte=data_fim)

    # Combina receitas e despesas em uma única lista ordenada.
    movimentacoes = montar_movimentacoes(receitas, despesas)

    # Filtro por tipo: mantém apenas itens do tipo escolhido.
    if tipo == 'Receita':
        movimentacoes = [m for m in movimentacoes if m['tipo'] == 'Receita']
    elif tipo == 'Despesa':
        movimentacoes = [m for m in movimentacoes if m['tipo'] == 'Despesa']

    # Categorias disponíveis para o filtro (padrão + pessoais do usuário).
    categorias = Categoria.objects.filter(
        Q(usuario__isnull=True) | Q(usuario=request.user)
    )

    return render(request, 'financeiro/historico.html', {
        'movimentacoes': movimentacoes,
        'categorias': categorias,
        # Enviamos os filtros atuais de volta ao template para que
        # os campos do formulário mantenham os valores escolhidos.
        'filtro_tipo': tipo,
        'filtro_categoria': categoria_id,
        'filtro_data_inicio': data_inicio,
        'filtro_data_fim': data_fim,
    })
