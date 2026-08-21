#As Views recebem as requisições, executam a lógica necessária, 
#acessam Models e Forms e depois retornam uma página ou um redirecionamento.
from django.shortcuts import render, redirect, get_object_or_404 #Abre um template HTML, manda o usuário para outra página, procura um registro e retorna erro 404 se não existir;
from django.contrib.auth.decorators import login_required, user_passes_test #exige que o usuário esteja logado,verifica alguma regra de permissão;
from django.contrib.auth import login #autentica o usuário;
from django.contrib.auth.forms import PasswordChangeForm #formulário pronto do Django para trocar senha;
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from .models import Receita, Despesa, Categoria
from .forms import ReceitaForm, DespesaForm, CadastroForm, PerfilForm


@login_required #significa que somente usuários logados conseguem acessar financeiro.
def index(request):
    return render(request, 'financeiro/index.html')


# ── Usuarios ────────────────────────────────────────────

def cadastro(request):#Essa função cria uma nova conta.
    if request.user.is_authenticated:
        return redirect('financeiro_index')
    if request.method == 'POST': #O usuário enviou o formulário.
        form = CadastroForm(request.POST)#pega os dados preenchidos.
        if form.is_valid():#O Django verifica os dados e cria o usuário.
            user = form.save()
            login(request, user)
            messages.success(request, 'Cadastro realizado com sucesso!')
            return redirect('financeiro_index')
    else:
        form = CadastroForm()
    return render(request, 'usuarios/cadastro.html', {'form': form})


@login_required #atualizar perfil
def perfil(request):
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil atualizado com sucesso!')
            return redirect('perfil')
    else:
        form = PerfilForm(instance=request.user)
    return render(request, 'usuarios/index.html', {'form': form})


@login_required
def alterar_senha(request): #alterar a asenha
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user) #atualiza a sessão para que a pessoa continue conectada.
            messages.success(request, 'Senha alterada com sucesso!')
            return redirect('perfil')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'usuarios/alterar_senha.html', {'form': form})


def is_staff(user):
    return user.is_authenticated and user.is_staff #implementa a diferenciação entre usuário comum e administrador.


@login_required
@user_passes_test(is_staff, login_url='/financeiro/')
def administrativo_index(request):
    return render(request, 'administrativo/index.html')


# Receitas 

@login_required
def receita_listar(request):
    receitas = Receita.objects.filter(usuario=request.user)#filtra as receitas para os usuarios
    return render(request, 'financeiro/receitas/listar.html', {'receitas': receitas})


@login_required
def receita_cadastrar(request):
    if request.method == 'POST':
        form = ReceitaForm(request.POST)
        if form.is_valid():
            receita = form.save(commit=False)
            receita.usuario = request.user
            receita.save()
            messages.success(request, 'Receita cadastrada com sucesso!')
            return redirect('receita_listar')
    else:
        form = ReceitaForm()
    return render(request, 'financeiro/receitas/cadastrar.html', {'form': form})


@login_required
def receita_editar(request, id):
    receita = get_object_or_404(Receita, id_receita=id, usuario=request.user) #edita de acordo com a receita e o usuario
    if request.method == 'POST':
        form = ReceitaForm(request.POST, instance=receita)
        if form.is_valid():
            form.save()
            messages.success(request, 'Receita atualizada com sucesso!')
            return redirect('receita_listar')
    else:
        form = ReceitaForm(instance=receita)
    return render(request, 'financeiro/receitas/editar.html', {
        'form': form,
        'receita': receita,
    })


@login_required
def receita_excluir(request, id):
    receita = get_object_or_404(Receita, id_receita=id, usuario=request.user) #edita de acordo com a receita e o usuario
    if request.method == 'POST':
        receita.delete()
        messages.success(request, 'Receita excluida com sucesso!')
        return redirect('receita_listar')
    return render(request, 'financeiro/receitas/excluir.html', {'receita': receita})


#Despesas 

@login_required
def despesa_listar(request):
    despesas = Despesa.objects.filter(usuario=request.user)
    return render(request, 'financeiro/despesas/listar.html', {'despesas': despesas})


@login_required
def despesa_cadastrar(request):
    if request.method == 'POST':
        form = DespesaForm(request.POST)
        if form.is_valid():
            despesa = form.save(commit=False)
            despesa.usuario = request.user
            despesa.save()
            messages.success(request, 'Despesa cadastrada com sucesso!')
            return redirect('despesa_listar')
    else:
        form = DespesaForm()
    return render(request, 'financeiro/despesas/cadastrar.html', {'form': form})


@login_required
def despesa_editar(request, id):
    despesa = get_object_or_404(Despesa, id_despesa=id, usuario=request.user)
    if request.method == 'POST':
        form = DespesaForm(request.POST, instance=despesa)
        if form.is_valid():
            form.save()
            messages.success(request, 'Despesa atualizada com sucesso!')
            return redirect('despesa_listar')
    else:
        form = DespesaForm(instance=despesa)
    return render(request, 'financeiro/despesas/editar.html', {
        'form': form,
        'despesa': despesa,
    })


@login_required
def despesa_excluir(request, id):
    despesa = get_object_or_404(Despesa, id_despesa=id, usuario=request.user)
    if request.method == 'POST':
        despesa.delete()
        messages.success(request, 'Despesa excluida com sucesso!')
        return redirect('despesa_listar')
    return render(request, 'financeiro/despesas/excluir.html', {'despesa': despesa})


#Categorias 

@login_required
def categoria_listar(request):#todo usuário vê todas as categorias.
    categorias = Categoria.objects.all()
    return render(request, 'financeiro/categorias/listar.html', {'categorias': categorias})
