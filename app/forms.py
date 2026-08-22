# ==========================================
# FORMS (FORMULARIOS) DO PIGMONEY
# ==========================================
# O arquivo forms.py cria e valida os formularios
# utilizados para inserir e editar dados no sistema.
#
# Formularios atuam como camada de validacao entre
# o HTML (template) e o banco de dados (Models).
#
# Tipos principais:
#   - forms.Form: formulario generico (sem ligacao com Model)
#   - forms.ModelForm: vinculado a um Model (salva automaticamente)
#   - UserCreationForm: especial para criar usuarios (Django)
# ==========================================

from decimal import Decimal

from django import forms

# UserCreationForm ja traz validacao de senha:
# confirmacao, minimo de caracteres, senhas fracas, etc.
from django.contrib.auth.forms import UserCreationForm

from django.contrib.auth.models import User

from .models import Receita, Despesa, Categoria


# ==========================================
# FORMULARIO DE CADASTRO DE USUARIO
# ==========================================

class CadastroForm(UserCreationForm):
    """
    Herda de UserCreationForm (Django) e adiciona campos
    extras: nome, sobrenome e e-mail.

    Os nomes internos (username, password1, password2) NAO
    sao traduzidos porque sao usados pelo Django internamente.
    Labels e placeholders sao usados para exibir em portugues.
    """

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
        # Qual Model este formulario esta vinculado.
        model = User

        # Campos que aparecem no formulario (ordem de exibicao).
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]

        # Widgets personalizam a aparencia dos campos no HTML.
        widgets = {
            'username': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nome de usuario',
            }),
        }

        # Labels personalizam o texto ao lado de cada campo.
        labels = {
            'username': 'Nome de usuario',
        }

    def __init__(self, *args, **kwargs):
        """
        Metodo executado quando o formulario e criado.

        - __init__ e o construtor da classe.
        - *args e **kwargs sao argumentos passados para a classe pai.
        - super().__init__() executa a inicializacao do UserCreationForm,
          que ja configura os campos password1 e password2.
        - Depois podemos personalizar labels e classes CSS.
        """
        super().__init__(*args, **kwargs)

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


# ==========================================
# FORMULARIO DE PERFIL (EDICAO)
# ==========================================

class PerfilForm(forms.ModelForm):
    """
    Formulario para editar os dados do usuario logado.
    instance=request.user na View preenche com os dados atuais.
    """

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
        label='Nome de usuario',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nome de usuario',
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


# ==========================================
# FORMULARIO DE CATEGORIAS
# ==========================================

# django.db.models.Q permite criar consultas complexas com OR (|).
# Sem ele, só seria possível filtrar com AND.
from django.db.models import Q


class CategoriaForm(forms.ModelForm):
    """
    Formulário para cadastrar e editar categorias personalizadas.

    O campo 'usuario' NÃO aparece no formulário porque é preenchido
    automaticamente pela View com request.user. O usuário não escolhe
    a quem a categoria pertence — o sistema define isso sozinho.
    """

    class Meta:
        model = Categoria

        fields = ['nome_categoria', 'descricao']

        labels = {
            'nome_categoria': 'Nome da categoria',
            'descricao': 'Descricao',
        }

        widgets = {
            'nome_categoria': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ex: Academia, Viagens, Pets',
            }),

            'descricao': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Descricao opcional da categoria',
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Recebe o usuario logado para validar nomes duplicados.
        O usuario e capturado da View e passado como parametro opcional.
        """
        self.usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

    def clean_nome_categoria(self):
        """
        Valida se ja existe uma categoria com o mesmo nome
        para o mesmo usuario (ou categorias padrao).

        Regras:
        - Nao pode duplicar nome entre categorias pessoais do mesmo usuario.
        - Nao pode duplicar nome de uma categoria padrao.
        - Outros usuarios podem criar categorias com o mesmo nome.
        """
        nome = self.cleaned_data.get('nome_categoria')
        if not nome:
            return nome

        # Verifica se ja existe uma categoria padrao com este nome.
        categoria_padrao = Categoria.objects.filter(
            usuario__isnull=True,
            nome_categoria__iexact=nome
        )

        # Se estamos editando, excluimos a propria categoria da verificacao.
        if self.instance and self.instance.pk:
            categoria_padrao = categoria_padrao.exclude(
                id_categoria=self.instance.pk
            )

        if categoria_padrao.exists():
            raise forms.ValidationError(
                'Ja existe uma categoria padrao com esse nome.'
            )

        # Verifica se o usuario ja possui uma categoria com este nome.
        if self.usuario:
            duplicada = Categoria.objects.filter(
                usuario=self.usuario,
                nome_categoria__iexact=nome
            )

            if self.instance and self.instance.pk:
                duplicada = duplicada.exclude(
                    id_categoria=self.instance.pk
                )

            if duplicada.exists():
                raise forms.ValidationError(
                    'Voce ja possui uma categoria com esse nome.'
                )

        return nome


# ==========================================
# FORMULARIO DE RECEITAS
# ==========================================
# A View envia usuario=request.user para filtrar o campo categoria.

class ReceitaForm(forms.ModelForm):
    """
    Formulario para cadastrar e editar receitas.
    Herda de ModelForm vinculado ao model Receita.
    """

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
            'descricao': 'Descricao',
            'data_receita': 'Data da receita',
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
                'placeholder': 'Ex: Salario',
            }),

            'data_receita': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),

            'categoria': forms.Select(attrs={
                'class': 'form-control',
            }),
        }

    def __init__(self, *args, **kwargs):
        """
        Filtra o campo categoria para mostrar apenas:
        - categorias padrao (usuario=NULL)
        - categorias pessoais do usuario logado

        O parametro 'usuario' e passado pela View e removido dos kwargs
        antes de chamar super().__init__(), pois o ModelForm nao o conhece.
        """
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        if usuario:
            # Q(usuario__isnull=True) | Q(usuario=usuario)
            # Retorna categorias globais OU pertencentes ao usuario.
            self.fields['categoria'].queryset = Categoria.objects.filter(
                Q(usuario__isnull=True) | Q(usuario=usuario)
            )

    def clean_valor(self):
        """
        Validacao customizada do campo valor.

        cleaned_data contem os valores ja validados pelo Django.
        Se valor for None, zero ou negativo, levanta um erro.
        """
        valor = self.cleaned_data.get('valor')

        if valor is None or valor <= Decimal('0.00'):
            raise forms.ValidationError(
                'O valor deve ser maior que zero.'
            )

        return valor


# ==========================================
# FORMULARIO DE DESPESAS
# ==========================================

class DespesaForm(forms.ModelForm):
    """
    Formulario para cadastrar e editar despesas.
    Estrutura identica ao ReceitaForm.
    """

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
            'descricao': 'Descricao',
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

    def __init__(self, *args, **kwargs):
        """
        Mesma logica do ReceitaForm: filtra categorias
        para mostrar apenas padrao + pessoais do usuario.
        """
        usuario = kwargs.pop('usuario', None)
        super().__init__(*args, **kwargs)

        if usuario:
            self.fields['categoria'].queryset = Categoria.objects.filter(
                Q(usuario__isnull=True) | Q(usuario=usuario)
            )

    def clean_valor(self):
        """Validacao customizada: valor deve ser maior que zero."""
        valor = self.cleaned_data.get('valor')

        if valor is None or valor <= Decimal('0.00'):
            raise forms.ValidationError(
                'O valor deve ser maior que zero.'
            )

        return valor
