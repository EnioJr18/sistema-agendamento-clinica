from datetime import timedelta

from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken

from api.models import Clinica, Usuario


class JwtThrottleAndObservabilityTest(APITestCase):
    def setUp(self):
        cache.clear()
        clinica = Clinica.objects.create(nome='Clinica Hardening')
        self.usuario = Usuario.objects.create_user(
            username='usuario_hardening',
            password='SenhaAtual123!',
            tipo='PACIENTE',
            nome_completo='Usuario Hardening',
            email='hardening@example.com',
            cpf='90000000001',
            telefone='82999999999',
            data_nascimento='1990-01-01',
            clinica=clinica,
        )

    def tearDown(self):
        cache.clear()

    def test_jwt_expirado_invalido_e_refresh_rotacionado(self):
        token_expirado = AccessToken.for_user(self.usuario)
        token_expirado.set_exp(from_time=timezone.now(), lifetime=timedelta(seconds=-1))
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {token_expirado}')
        self.assertEqual(self.client.get(reverse('dentista-list')).status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION='Bearer token-invalido')
        self.assertEqual(self.client.get(reverse('dentista-list')).status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials()
        login = self.client.post(reverse('token_obtain_pair'), {'username': self.usuario.username, 'password': 'SenhaAtual123!'})
        self.assertEqual(login.status_code, status.HTTP_200_OK)
        refresh = login.data['refresh']
        renovacao = self.client.post(reverse('token_refresh'), {'refresh': refresh})
        self.assertEqual(renovacao.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', renovacao.data)
        self.assertEqual(self.client.post(reverse('token_refresh'), {'refresh': refresh}).status_code, status.HTTP_401_UNAUTHORIZED)

    def test_login_e_limitado_por_throttle(self):
        for _ in range(10):
            response = self.client.post(reverse('token_obtain_pair'), {'username': 'invalido', 'password': 'invalida'})
            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            self.client.post(reverse('token_obtain_pair'), {'username': 'invalido', 'password': 'invalida'}).status_code,
            status.HTTP_429_TOO_MANY_REQUESTS,
        )

    @override_settings(REQUEST_LOGGING_ENABLED=True)
    def test_headers_request_id_e_log_sem_payload_sensivel(self):
        with self.assertLogs('api.request', level='INFO') as logs:
            response = self.client.get(reverse('health-check'), HTTP_X_REQUEST_ID='correlacao-123')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['X-Request-ID'], 'correlacao-123')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
        self.assertEqual(response['Referrer-Policy'], 'same-origin')
        self.assertIn('path=/api/health/', logs.output[0])
        self.assertNotIn('password', logs.output[0].lower())
        self.assertNotIn('authorization', logs.output[0].lower())
