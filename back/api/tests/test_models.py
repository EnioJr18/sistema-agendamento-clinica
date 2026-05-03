from django.test import TestCase
from api.models import Usuario, Dentista

class DentistaModelTest(TestCase):
    def setUp(self):
        """
        O setUp roda ANTES de cada teste. 
        É aqui que preparamos o 'terreno' criando dados fictícios no banco SQLite.
        """
        # 1. Criamos um usuário com Nome e Sobrenome
        self.usuario = Usuario.objects.create(
            username="joaodentista",
            first_name="João",
            last_name="Silva"
        )
        
        # 2. Criamos o dentista e vinculamos ao usuário acima
        self.dentista = Dentista.objects.create(
            usuario=self.usuario,
            especialidade="Ortodontia",
            cro="12345-AL"
        )

    def test_dentista_str_retorna_nome_e_especialidade(self):
        """
        Testa se o painel do Admin e o sistema vão exibir o nome corretamente.
        """
        # O que esperamos que o sistema gere?
        resultado_esperado = "Dr(a). João Silva - Ortodontia"
        
        # Comparamos a string gerada pelo modelo com o que esperamos
        self.assertEqual(str(self.dentista), resultado_esperado)