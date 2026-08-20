from django.db import migrations


def seed_categorias(apps, schema_editor):
    Categoria = apps.get_model('app', 'Categoria')

    categorias = [
        ('Alimentacao', 'Gastos com comida, supermercado, restaurantes.'),
        ('Transporte', 'Gastos com combustivel, onibus, uber, estacionamento.'),
        ('Moradia', 'Aluguel, contas de agua, luz, gas, condominio.'),
        ('Lazer', 'Entretenimento, jogos, saidas, viagens.'),
        ('Educacao', 'Faculdade, cursos, livros, material escolar.'),
        ('Saude', 'Plano de saude, medicamentos, consultas.'),
        ('Salario', 'Receita proveniente de trabalho.'),
        ('Outros', 'Categorias nao classificadas.'),
    ]

    for nome, descricao in categorias:
        Categoria.objects.get_or_create(
            nome_categoria=nome,
            defaults={'descricao': descricao},
        )


def reverse_seed(apps, schema_editor):
    Categoria = apps.get_model('app', 'Categoria')
    Categoria.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_categorias, reverse_seed),
    ]
