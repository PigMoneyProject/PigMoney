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

# Função login() do Django: autentica o usuário e cria a sessão.
from django.contrib.auth import login

# Formulário nativo do Django para alteração de senha.
from django.contrib.auth.forms import PasswordChangeForm

# Mantém a sessão ativa após alterar a senha (evita deslogar o usuário).
from django.contrib.auth import update_session_auth_hash

# Sistema de mensagens do Django (sucesso, erro, etc.).
from django.contrib import messages

# Models do nosso projeto (estrutura dos dados no banco).
from .models import Receita, Despesa, Categoria

# Forms do nosso projeto (formulários para criar/editar dados).
from .forms import ReceitaForm, DespesaForm, CadastroForm, PerfilForm, CategoriaForm

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
    """Exibe o painel principal do usuário (dashboard financeiro)."""
    return render(request, 'financeiro/index.html')


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
