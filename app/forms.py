# forms é responsável por criar e validar os formulários
# utilizados para inserir e editar dados no sistema.

from decimal import Decimal #importaão para conseguir colocar números decimáis 

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Receita, Despesa



class CadastroForm(UserCreationForm): #formulario para cadastro

    first_name = forms.CharField(
        label='Nome',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu nome',
        }),
    )

    last_name = forms.CharField(
        label='Sobrenome',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Seu sobrenome',
        }),
    )

    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
        }),
    )

    class Meta:
        model = User

        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]

        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de usuário',
            }),
        }

        labels = {
            'username': 'Nome de usuário',
        }

    def __init__(self, *args, **kwargs): #é um método executado quando um objeto é criado.
        super().__init__(*args, **kwargs)

        # Traduz os textos dos campos de senha.
        self.fields['password1'].label = 'Senha'
        self.fields['password2'].label = 'Confirme a senha'

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Senha',
        })

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirme a senha',
        })



class PerfilForm(forms.ModelForm):#editar o usuário que já existe.

    first_name = forms.CharField(
        label='Nome',
        max_length=30,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome',
        }),
    )

    last_name = forms.CharField(
        label='Sobrenome',
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Sobrenome',
        }),
    )

    email = forms.EmailField(
        label='E-mail',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'seu@email.com',
        }),
    )

    username = forms.CharField(
        label='Nome de usuário',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome de usuário',
        }),
    )

    class Meta:
        model = User

        fields = [
            'first_name',
            'last_name',
            'email',
            'username',
        ]



#O sistema identifica automaticamente a pessoa autenticada, porque na views ja esta programada para pertencer a um usuário
class ReceitaForm(forms.ModelForm):

    class Meta:
        model = Receita

        fields = [
            'valor',
            'descricao',
            'data_receita',
            'categoria',
        ]

        labels = {
            'valor': 'Valor',
            'descricao': 'Descrição',
            'data_receita': 'Data da receita',
            'categoria': 'Categoria',
        }

        widgets = {
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',#permite valores com centavos
                'placeholder': '0,00',
            }),

            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Salário',
            }),

            'data_receita': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),

            'categoria': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

    # Validação para impedir valores iguais ou menores que zero(mesmo que alguem consiga ignorar o min=0.01)
    def clean_valor(self):
        valor = self.cleaned_data.get('valor')

        if valor is None or valor <= Decimal('0.00'):
            raise forms.ValidationError(
                'O valor deve ser maior que zero.'
            )

        return valor



class DespesaForm(forms.ModelForm):

    class Meta:
        model = Despesa

        fields = [
            'valor',
            'descricao',
            'data_despesa',
            'categoria',
        ]

        labels = {
            'valor': 'Valor',
            'descricao': 'Descrição',
            'data_despesa': 'Data da despesa',
            'categoria': 'Categoria',
        }

        widgets = {
            'valor': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0.01',
                'placeholder': '0,00',
            }),

            'descricao': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Supermercado',
            }),

            'data_despesa': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),

            'categoria': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

    # Validação para impedir valores iguais ou menores que zero.
    def clean_valor(self):
        valor = self.cleaned_data.get('valor')

        if valor is None or valor <= Decimal('0.00'):
            raise forms.ValidationError(
                'O valor deve ser maior que zero.'
            )

        return valor