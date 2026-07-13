from django.test import TestCase

from api.models import Clinica, Dentista, Usuario


class DentistaModelTest(TestCase):
    def setUp(self):
        self.clinica = Clinica.objects.create(nome='Clinica Teste')
        self.usuario = Usuario.objects.create_user(
            username='joaodentista',
            password='SenhaAtual123!',
            nome_completo='Joao Silva',
            email='joao.silva@example.com',
            cpf='40000000001',
            data_nascimento='1985-01-10',
            telefone='82955554444',
            tipo='DENTISTA',
            clinica=self.clinica,
        )

        self.dentista = Dentista.objects.create(
            clinica=self.clinica,
            usuario=self.usuario,
            especialidade='Ortodontia',
            cro='12345-AL',
        )

    def test_dentista_str_retorna_nome_e_especialidade(self):
        resultado_esperado = 'Dr(a). Joao Silva - Ortodontia'

        self.assertEqual(str(self.dentista), resultado_esperado)
