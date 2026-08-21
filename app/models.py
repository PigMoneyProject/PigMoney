#O models define as entidades e os dados que serão armazenados no banco. Cada Model representa uma estrutura de dados que o Django transforma em tabelas através das migrations.
from django.db import models
from django.contrib.auth.models import User


class Categoria(models.Model):
    id_categoria = models.AutoField(primary_key=True)
    nome_categoria = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Categoria'
        verbose_name_plural = 'Categorias'
        ordering = ['nome_categoria'] #faz com que as categorias apareçam em ordem alfabética.

    def __str__(self):
        return self.nome_categoria


class Receita(models.Model):
    id_receita = models.AutoField(primary_key=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=255)
    data_receita = models.DateField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receitas')#Se o usuário for excluído, suas receitas/despesas também são excluídas.
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='receitas')#a categoria estiver sendo utilizada, o Django impede que ela seja excluída.

    class Meta:
        verbose_name = 'Receita'
        verbose_name_plural = 'Receitas'
        ordering = ['-data_receita']

    def __str__(self):
        return f'{self.descricao} - R$ {self.valor}'


class Despesa(models.Model):
    id_despesa = models.AutoField(primary_key=True)
    valor = models.DecimalField(max_digits=10, decimal_places=2)
    descricao = models.CharField(max_length=255)
    data_despesa = models.DateField()
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='despesas')
    categoria = models.ForeignKey(Categoria, on_delete=models.PROTECT, related_name='despesas')

    class Meta:
        verbose_name = 'Despesa'
        verbose_name_plural = 'Despesas'
        ordering = ['-data_despesa']

    def __str__(self):
        return f'{self.descricao} - R$ {self.valor}'
