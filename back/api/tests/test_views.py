from rest_framework.test import APITestCase
from rest_framework import status
from django.urls import reverse
from api.models import Usuario, Dentista

class DentistaViewSetTest(APITestCase):
    def setUp(self):
        """
        Prepara o cenário criando um Paciente e um Dentista no banco de testes.
        """
        # 1. Criamos um usuário comum (Paciente)
        self.paciente = Usuario.objects.create_user(
            username="paciente_teste",
            password="senha123",
            tipo="PACIENTE"
        )
        
        # 2. Criamos o usuário e o perfil do Dentista
        self.user_dentista = Usuario.objects.create_user(
            username="dentista_teste",
            password="senha123",
            first_name="Ana",
            tipo="DENTISTA"
        )
        self.dentista = Dentista.objects.create(
            usuario=self.user_dentista,
            especialidade="Odontopediatria",
            cro="98765-AL"
        )

        # 3. Descobrimos a URL da nossa API.
        # O DefaultRouter do Django nomeia as rotas de lista como 'nomedomodel-list'
        self.url = reverse('dentista-list')

    def test_listar_dentistas_sem_token_retorna_401(self):
        """
        Testa se a API bloqueia um 'hacker' tentando ver os dentistas sem estar logado.
        """
        # O self.client simula o Front-end fazendo um GET
        response = self.client.get(self.url)
        
        # Como bloqueamos isso na View, esperamos o Erro 401 (Não Autorizado)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listar_dentistas_com_token_retorna_200(self):
        """
        Testa se um paciente logado consegue ver a lista de dentistas paginada.
        """
        # Simulamos o login do paciente (injeta o token virtualmente)
        self.client.force_authenticate(user=self.paciente)
        
        # Agora tentamos fazer o GET novamente
        response = self.client.get(self.url)
        
        # 1. Esperamos o código 200 (Sucesso!)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # 2. Como ativamos a paginação, a lista vem dentro da chave 'results'
        # Vamos garantir que retornou exatamente 1 dentista
        self.assertEqual(len(response.data['results']), 1)
        
        # 3. E vamos garantir que é a Ana (Odontopediatra)
        self.assertEqual(response.data['results'][0]['especialidade'], "Odontopediatria")