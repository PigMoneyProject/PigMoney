# ==========================================
# MODELS DO PIGMONEY
# ==========================================
# O Models define as estruturas de dados que serão
# armazenadas no banco de dados. Cada classe Python
# se transforma em uma tabela no PostgreSQL.
#
# O Django utiliza um ORM (Object-Relational Mapping),
# que permite trabalhar com o banco de dados usando
# código Python em vez de SQL direto.
#
# Exemplo: Receita.objects.all() retorna todas as
# receitas do banco — o Django traduz isso para:
#   SELECT * FROM app_receita;
# ==========================================

from django.db import models
# User é o model padrão de usuários do Django.
# Ele já possui: username, password, email, first_name,
# last_name, is_staff, is_active, date_joined, etc.
from django.contrib.auth.models import User


class Categoria(models.Model):
    """
    Modelo que representa uma categoria financeira.
    Exemplos: Alimentação, Transporte, Salário, Lazer.

    Existem dois tipos de categorias:

    CATEGORIA PADRÃO (usuario=NULL):
      Disponível para todos os usuários do sistema.
      Criada automaticamente pelo seed (migração 0002).
      Não pode ser editada nem excluída por usuários comuns.

    CATEGORIA PERSONALIZADA (usuario definido):
      Criada por um usuário específico.
      Somente o proprietário pode visualizar, editar e excluir.
      Aparece apenas para quem criou.
    """

    id_categoria = models.AutoField(primary_key=True)

    nome_categoria = models.CharField(max_length=100)

    # TextField: campo de texto longo, sem limite definido.
    # blank=True: pode ficar vazio no formulário.
    # null=True: pode ser NULL no banco de dados.
    descricao = models.TextField(blank=True, null=True)

    # ── RELACIONAMENTO COM USUÁRIO (OPCIONAL) ──
    # null=True: permite que o campo fique vazio no banco (categoria padrão).
    # blank=True: permite que o campo fique vazio no formulário.
    # on_delete=models.CASCADE: se o usuário for excluído, suas
    #   categorias personalizadas também serão removidas.
    # related_name='categorias_personalizadas': permite acessar as
    #   categorias personalizadas de um usuário assim:
    #   user.categorias_personalizadas.all()
    #
    # LÓGICA:
    #   usuario = NULL  → categoria padrão (visível para todos)
    #   usuario = User  → categoria pessoal (visível apenas para o dono)
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='categorias_personalizadas'
    )

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome_categoria']

    def __str__(self):
        return self.nome_categoria


class Receita(models.Model):
    """
    Modelo que representa uma receita (dinheiro recebido).
    Exemplos: salário,freelance, venda, etc.

    Cada receita pertence a um usuário e a uma categoria.
    """

    id_receita = models.AutoField(primary_key=True)

    # DecimalField: campo numérico com precisão exata (ideal para dinheiro).
    # max_digits=10: até 10 dígitos no total.
    # decimal_places=2: sempre 2 casas decimais (centavos).
    valor = models.DecimalField(max_digits=10, decimal_places=2)

    descricao = models.CharField(max_length=255)

    # DateField: armazena apenas data (sem hora).
    data_receita = models.DateField()

    # ── RELACIONAMENTO COM USUÁRIO ──
    # ForeignKey: cria uma ligação entre esta receita e um usuário.
    # on_delete=models.CASCADE: se o usuário for excluído, suas
    #   receitas também serão removidas automaticamente.
    # related_name='receitas': permite acessar as receitas de um
    #   usuário assim: user.receitas.all()
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='receitas'
    )

    # ── RELACIONAMENTO COM CATEGORIA ──
    # on_delete=models.PROTECT: impede que uma categoria seja excluída
    #   se houver receitas utilizando-a. Isso protege a integridade dos dados.
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='receitas'
    )

    class Meta:
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'
        # Ordenação decrescente (-): receitas mais recentes aparecem primeiro.
        ordering = ['-data_receita']

    def __str__(self):
        """Representação em texto da receita."""
        return f'{self.descricao} - R$ {self.valor}'


class Despesa(models.Model):
    """
    Modelo que representa uma despesa (dinheiro gasto).
    Estrutura idêntica à Receita, mas para saídas de dinheiro.
    """

    id_despesa = models.AutoField(primary_key=True)

    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=255)
    data_despesa = models.DateField()

    # Mesma lógica de relacionamento da Receita.
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='despesas'
    )

    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        related_name='despesas'
    )

    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering = ['-data_despesa']

    def __str__(self):
        return f'{self.descricao} - R$ {self.valor}'


class MetaFinanceira(models.Model):
    """
    Modelo que representa uma meta financeira do usuário.

    Exemplo:
      Nome: Comprar um notebook
      Valor objetivo: R$ 4.000,00
      Valor atual: R$ 1.500,00
      Prazo: 20/12/2026

    O percentual de progresso NÃO é armazenado no banco: ele é
    calculado automaticamente pela propriedade 'percentual' abaixo.
    Isso evita dados duplicados — se o valor atual mudar, o
    percentual é recalculado sozinho.
    """

    id_meta = models.AutoField(primary_key=True)

    nome_meta = models.CharField(max_length=255)

    # Valor que o usuário deseja alcançar (objetivo da meta).
    # Validação: deve ser maior que zero (feita no Form).
    valor_objetivo = models.DecimalField(max_digits=10, decimal_places=2)

    # Quanto o usuário já juntou até agora. Começa em 0.
    # Validação: não pode ser negativo (feita no Form).
    valor_atual = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0
    )

    # Data limite para atingir a meta.
    prazo = models.DateField()

    # Cada meta pertence a UM usuário específico.
    # on_delete=models.CASCADE: se o usuário for excluído, suas metas
    # também são removidas.
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='metas'
    )

    class Meta:
        verbose_name = 'Meta Financeira'
        verbose_name_plural = 'Metas Financeiras'
        ordering = ['prazo']

    def __str__(self):
        return f'{self.nome_meta} - R$ {self.valor_atual} / R$ {self.valor_objetivo}'

    @property
    def percentual(self):
        """
        Calcula a porcentagem alcançada da meta automaticamente.

        Fórmula: percentual = (valor_atual / valor_objetivo) * 100

        Proteções:
        - Se valor_objetivo for 0, evitamos divisão por zero (retorna 0).
        - min(..., 100) impede que o percentual passe de 100%
          (caso o usuário junte mais do que a meta pedia).
        """
        if self.valor_objetivo <= 0:
            return 0
        # round(..., 1) limita a 1 casa decimal (ex: 37.5%).
        # min(..., 100) impede que o percentual passe de 100%
        # (caso o usuário junte mais do que a meta pedia).
        percentual = (self.valor_atual / self.valor_objetivo) * 100
        return min(round(percentual, 1), 100)


class PlanejamentoMensal(models.Model):
    """
    Modelo que representa um limite de gastos para um mês específico.

    Cada usuário possui UM planejamento por (mês + ano).
    Exemplo: limite de R$ 2.000,00 para Setembro de 2026.

    O campo 'mes' guarda o número do mês (1 a 12) e o campo 'ano'
    guarda o ano (ex: 2026). Separamos em dois campos inteiros para
    facilitar a comparação com as despesas do mesmo mês/ano.
    """

    id_planejamento = models.AutoField(primary_key=True)

    # Número do mês: 1 = Janeiro, 2 = Fevereiro, ..., 12 = Dezembro.
    mes = models.IntegerField()

    # Ano do planejamento (ex: 2026).
    ano = models.IntegerField()

    # Quanto o usuário pretende gastar no mês.
    limite_gastos = models.DecimalField(max_digits=10, decimal_places=2)

    # Cada planejamento pertence a UM usuário.
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='planejamentos_mensais'
    )

    class Meta:
        verbose_name = 'Planejamento Mensal'
        verbose_name_plural = 'Planejamentos Mensais'
        ordering = ['-ano', '-mes']

        # Restrição de unicidade: o mesmo usuário só pode ter UM
        # planejamento para o mesmo mês/ano. Se tentar criar outro,
        # o formulário de edição é usado no lugar.
        constraints = [
            models.UniqueConstraint(
                fields=['usuario', 'mes', 'ano'],
                name='planejamento_unico_por_usuario_mes_ano'
            ),
        ]

    def __str__(self):
        return f'{self.mes}/{self.ano} - R$ {self.limite_gastos}'
