from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Dentista, Usuario


class DentistaViewSetTest(APITestCase):
    def setUp(self):
        self.paciente = Usuario.objects.create_user(
            username='paciente_teste', password='senha123', tipo='PACIENTE'
        )
        self.user_dentista = Usuario.objects.create_user(
            username='dentista_teste', password='senha123', first_name='Ana', tipo='DENTISTA'
        )
        Dentista.objects.create(
            usuario=self.user_dentista,
            especialidade='Odontopediatria',
            cro='98765-AL',
        )
        self.url = reverse('dentista-list')

    def test_listar_dentistas_sem_token_retorna_401(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_listar_dentistas_com_token_retorna_200(self):
        self.client.force_authenticate(user=self.paciente)
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['especialidade'], 'Odontopediatria')


class UsuarioSegurancaViewSetTest(APITestCase):
    def setUp(self):
        self.usuario = Usuario.objects.create_user(
            username='paciente_um', password='SenhaAtual123!', tipo='PACIENTE', first_name='Paciente'
        )
        self.outro_usuario = Usuario.objects.create_user(
            username='paciente_dois', password='SenhaAtual123!', tipo='PACIENTE'
        )
        self.admin = Usuario.objects.create_user(
            username='administrador', password='SenhaAtual123!', tipo='ADMIN', is_staff=True
        )
        self.lista_url = reverse('usuario-list')
        self.detalhe_outro_url = reverse('usuario-detail', args=[self.outro_usuario.pk])
        self.meu_perfil_url = reverse('usuario-detail', args=[self.usuario.pk])
        self.alterar_senha_url = reverse('usuario-alterar-senha')

    def test_cadastro_publico_ignora_tipo_admin_e_nao_retorna_senha(self):
        response = self.client.post(
            self.lista_url,
            {
                'username': 'novo_usuario',
                'password': 'SenhaForte123!',
                'first_name': 'Novo',
                'tipo': 'ADMIN',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        usuario = Usuario.objects.get(username='novo_usuario')
        self.assertEqual(usuario.tipo, 'PACIENTE')
        self.assertNotIn('password', response.data)
        self.assertNotIn('tipo', response.data)

    def test_usuario_comum_nao_lista_usuarios(self):
        self.client.force_authenticate(self.usuario)
        response = self.client.get(self.lista_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_usuario_comum_nao_acessa_outro_perfil(self):
        self.client.force_authenticate(self.usuario)
        response = self.client.get(self.detalhe_outro_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_usuario_comum_nao_altera_tipo_e_senha_nao_vaza(self):
        senha_original = self.usuario.password
        self.client.force_authenticate(self.usuario)
        response = self.client.patch(
            self.meu_perfil_url,
            {'first_name': 'Nome Atualizado', 'tipo': 'ADMIN', 'password': 'TextoPuro123!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.tipo, 'PACIENTE')
        self.assertEqual(self.usuario.password, senha_original)
        self.assertNotIn('password', response.data)
        self.assertNotIn('tipo', response.data)

    def test_alteracao_de_senha_usa_set_password(self):
        self.client.force_authenticate(self.usuario)
        response = self.client.post(
            self.alterar_senha_url,
            {'senha_atual': 'SenhaAtual123!', 'nova_senha': 'NovaSenhaForte123!'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.usuario.refresh_from_db()
        self.assertTrue(self.usuario.check_password('NovaSenhaForte123!'))
        self.assertNotEqual(self.usuario.password, 'NovaSenhaForte123!')

    def test_cors_nao_permite_todas_as_origens(self):
        self.assertFalse(settings.CORS_ALLOW_ALL_ORIGINS)
        self.assertIn('http://localhost:5173', settings.CORS_ALLOWED_ORIGINS)
