from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from datetime import date

from app.models import Categoria, Receita, Despesa, MetaFinanceira, PlanejamentoMensal


class BaseTeste(TestCase):
    """
    Classe base com utilidades compartilhadas pelos testes.

    Cria dois usuários e uma categoria para cada um, além de
    receitas, despesas, metas e planejamentos — tudo separado
    por usuário, para testar o isolamento de dados.
    """

    def setUp(self):
        # Data de hoje, utilizada nos registros para que os testes
        # de resumo mensal e planejamento funcionem em qualquer mês.
        hoje = date.today()

        # Usuário 1 (dono dos dados principais).
        self.usuario1 = User.objects.create_user(
            username='joao', password='senha12345', first_name='Joao'
        )

        # Usuário 2 (usado para verificar o isolamento de dados).
        self.usuario2 = User.objects.create_user(
            username='maria', password='senha12345', first_name='Maria'
        )

        # Categorias próprias de cada usuário.
        self.categoria1 = Categoria.objects.create(
            nome_categoria='Salario', usuario=self.usuario1
        )
        self.categoria1_usuario2 = Categoria.objects.create(
            nome_categoria='Salario', usuario=self.usuario2
        )

        # Receitas e despesas apenas do usuário 1.
        # Usamos o mês atual para que os testes de planejamento
        # e resumo mensal funcionem em qualquer data de execução.
        Receita.objects.create(
            usuario=self.usuario1, valor=3000,
            descricao='Salario do mes',
            data_receita=date(hoje.year, hoje.month, 5),
            categoria=self.categoria1
        )
        Despesa.objects.create(
            usuario=self.usuario1, valor=800,
            descricao='Aluguel',
            data_despesa=date(hoje.year, hoje.month, 10),
            categoria=self.categoria1
        )

    def fazer_login(self, usuario):
        """Autentica o usuário informado no client de testes."""
        self.client.login(username=usuario.username, password='senha12345')


class PaginasTestes(BaseTeste):
    def test_paginas_exigem_login(self):
        """Páginas financeiras sem login devem redirecionar para a tela de login."""
        for url in [
            reverse('financeiro_index'),
            reverse('meta_listar'),
            reverse('planejamento'),
            reverse('historico'),
        ]:
            resposta = self.client.get(url)
            # 302 = redirecionamento (para a URL de login).
            self.assertEqual(resposta.status_code, 302)

    def test_dashboard_mostra_dados_do_usuario_logado(self):
        """Dashboard deve exibir saldo, totais e movimentações do usuário."""
        self.fazer_login(self.usuario1)
        resposta = self.client.get(reverse('financeiro_index'))

        self.assertEqual(resposta.status_code, 200)
        # Saldo esperado: 3000 (receita) - 800 (despesa) = 2200.
        # Observação: no locale pt-BR o Django formata com vírgula (2200,00).
        self.assertContains(resposta, '2200,00')
        self.assertContains(resposta, 'R$ 3000,00')  # Total de receitas.
        self.assertContains(resposta, 'R$ 800,00')   # Total de despesas.
        # Movimentação recente aparece no dashboard.
        self.assertContains(resposta, 'Salario do mes')

    def test_dashboard_nao_exibe_dados_de_outro_usuario(self):
        """Usuário 2 não pode ver as movimentações do usuário 1."""
        self.fazer_login(self.usuario2)
        resposta = self.client.get(reverse('financeiro_index'))

        # Não deve conter as movimentações do usuário 1.
        self.assertNotContains(resposta, 'Salario do mes')
        self.assertNotContains(resposta, 'Aluguel')

    def test_paginas_existentes_renderizam(self):
        """Páginas antigas continuam funcionando com a navbar atualizada."""
        self.fazer_login(self.usuario1)
        for url in [
            reverse('receita_listar'),
            reverse('receita_cadastrar'),
            reverse('despesa_listar'),
            reverse('despesa_cadastrar'),
            reverse('categoria_listar'),
            reverse('categoria_cadastrar'),
            reverse('perfil'),
        ]:
            resposta = self.client.get(url)
            self.assertEqual(resposta.status_code, 200)


class MetasTestes(BaseTeste):
    def test_criar_meta_com_progresso(self):
        """Meta com percentual calculado corretamente."""
        self.fazer_login(self.usuario1)
        self.client.post(reverse('meta_cadastrar'), {
            'nome_meta': 'Comprar notebook',
            'valor_objetivo': '4000.00',
            'valor_atual': '1500.00',
            'prazo': '2026-12-20',
        })

        meta = MetaFinanceira.objects.get(usuario=self.usuario1, nome_meta='Comprar notebook')
        # percentual = (1500 / 4000) * 100 = 37.5
        self.assertEqual(meta.percentual, 37.5)

    def test_meta_valor_objetivo_invalido(self):
        """Valor objetivo <= 0 deve ser rejeitado pelo formulário."""
        self.fazer_login(self.usuario1)
        resposta = self.client.post(reverse('meta_cadastrar'), {
            'nome_meta': 'Meta invalida',
            'valor_objetivo': '0',
            'valor_atual': '100',
            'prazo': '2026-12-20',
        })
        # Se a meta não foi criada, o formulário é exibido novamente (200).
        self.assertEqual(resposta.status_code, 200)
        self.assertFalse(MetaFinanceira.objects.filter(nome_meta='Meta invalida').exists())

    def test_meta_nao_pertence_a_outro_usuario(self):
        """Usuário 2 não pode editar/excluir meta do usuário 1."""
        meta = MetaFinanceira.objects.create(
            usuario=self.usuario1, nome_meta='Meta do Joao',
            valor_objetivo=1000, valor_atual=200, prazo=date(2026, 12, 20)
        )

        self.fazer_login(self.usuario2)
        # Tenta editar a meta do João pela URL (deve retornar 404).
        resposta = self.client.get(reverse('meta_editar', args=[meta.id_meta]))
        self.assertEqual(resposta.status_code, 404)

        # Tenta excluir (deve retornar 404).
        resposta = self.client.get(reverse('meta_excluir', args=[meta.id_meta]))
        self.assertEqual(resposta.status_code, 404)


class PlanejamentoTestes(BaseTeste):
    def test_planejamento_calcula_limite_utilizado(self):
        """Percentual utilizado deve ser calculado corretamente."""
        self.fazer_login(self.usuario1)

        # Utiliza o mês atual do sistema para não depender de data fixa.
        hoje = date.today()
        mes_ano = f'{hoje.year:04d}-{hoje.month:02d}'

        # Cria planejamento com limite de 2000 para o mês atual.
        self.client.post(reverse('planejamento'), {
            'limite_gastos': '2000.00',
        })

        planejamento = PlanejamentoMensal.objects.get(
            usuario=self.usuario1, mes=hoje.month, ano=hoje.year
        )
        self.assertEqual(planejamento.limite_gastos, 2000)

        # Acesso à página do mês: gasto = 800, restante = 1200,
        # percentual = (800/2000)*100 = 40. Formato pt-BR usa vírgula.
        resposta = self.client.get(
            reverse('planejamento') + f'?mes_ano={mes_ano}'
        )
        self.assertContains(resposta, 'R$ 800,00')
        self.assertContains(resposta, 'R$ 1200,00')
        self.assertContains(resposta, '40,0%')


class HistoricoTestes(BaseTeste):
    def test_historico_mostra_movimentacoes_e_filtro(self):
        """Histórico deve filtrar por tipo corretamente."""
        self.fazer_login(self.usuario1)

        resposta = self.client.get(reverse('historico'))
        self.assertEqual(resposta.status_code, 200)
        self.assertContains(resposta, 'Salario do mes')
        self.assertContains(resposta, 'Aluguel')

        # Filtro por tipo Despesa: apenas o aluguel deve aparecer.
        resposta = self.client.get(reverse('historico'), {'tipo': 'Despesa'})
        self.assertContains(resposta, 'Aluguel')
        self.assertNotContains(resposta, 'Salario do mes')