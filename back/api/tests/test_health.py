from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class HealthCheckTest(APITestCase):
    def test_health_check_retorna_200_sem_dados_sensiveis(self):
        response = self.client.get(reverse('health-check'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'ok')
        self.assertEqual(response.data['database'], 'ok')
        self.assertNotIn('SECRET_KEY', response.data)
        self.assertNotIn('DATABASE_URL', response.data)
