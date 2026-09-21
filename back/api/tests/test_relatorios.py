from datetime import timedelta
from decimal import Decimal

from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Agendamento, Clinica, Dentista, Orcamento, Pagamento, Procedimento, Usuario


def usuario(username, cpf, email, clinica=None, tipo='PACIENTE', staff=False):
    return Usuario.objects.create_user(username=username, password='SenhaAtual123!', nome_completo=username, email=email, cpf=cpf, telefone='82999990000', data_nascimento='1990-01-01', clinica=clinica, tipo=tipo, is_staff=staff)


class RelatoriosApiTest(APITestCase):
    def setUp(self):
        self.a, self.b = Clinica.objects.create(nome='Clinica Relatorios A'), Clinica.objects.create(nome='Clinica Relatorios B')
        self.staff = usuario('staff_rel', '97000000001', 'staff.rel@example.com', tipo='ADMIN', staff=True)
        self.paciente_a = usuario('paciente_rel_a', '97000000002', 'pa.rel@example.com', self.a)
        self.paciente_b = usuario('paciente_rel_b', '97000000003', 'pb.rel@example.com', self.b)
        self.dentista_usuario = usuario('dentista_rel_a', '97000000004', 'da.rel@example.com', self.a, 'DENTISTA')
        self.dentista_b_usuario = usuario('dentista_rel_b', '97000000005', 'db.rel@example.com', self.b, 'DENTISTA')
        self.dentista = Dentista.objects.create(clinica=self.a, usuario=self.dentista_usuario, especialidade='Clinico', cro='97001-AL')
        self.dentista_b = Dentista.objects.create(clinica=self.b, usuario=self.dentista_b_usuario, especialidade='Clinico', cro='97002-AL')
        self.procedimento = Procedimento.objects.create(clinica=self.a, nome='Limpeza')
        agora = timezone.now() - timedelta(days=1)
        Agendamento.objects.create(clinica=self.a, paciente=self.paciente_a, dentista=self.dentista, procedimento='Limpeza', procedimento_ref=self.procedimento, data_horario=agora, data_hora_fim=agora + timedelta(minutes=30), duracao_minutos=30, status='CONCLUIDA')
        Agendamento.objects.create(clinica=self.b, paciente=self.paciente_b, dentista=self.dentista_b, procedimento='Outro', data_horario=agora, data_hora_fim=agora + timedelta(minutes=30), duracao_minutos=30, status='CANCELADA')
        orcamento = Orcamento.objects.create(clinica=self.a, paciente=self.paciente_a, titulo='Plano', status='APROVADO', total=Decimal('100.00'), saldo=Decimal('60.00'))
        Pagamento.objects.create(clinica=self.a, paciente=self.paciente_a, orcamento=orcamento, valor=Decimal('40.00'), forma_pagamento='PIX', pago_em=agora, registrado_por=self.staff)

    def test_dashboard_periodos_series_e_financeiro(self):
        self.client.force_authenticate(self.staff)
        resposta = self.client.get('/api/v1/dashboard/resumo/?periodo=7d')
        self.assertEqual(resposta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(resposta.data['evolucao']['agendamentos']), 7)
        self.assertEqual(resposta.data['financeiro']['total_recebido'], Decimal('40.00'))
        self.assertEqual(self.client.get('/api/v1/dashboard/resumo/?periodo=invalido').status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(self.client.get('/api/v1/dashboard/resumo/?data_inicial=2026-09-02&data_final=2026-09-01').status_code, status.HTTP_400_BAD_REQUEST)

    def test_relatorios_isolamento_permissoes_e_csv(self):
        self.client.force_authenticate(self.dentista_usuario)
        agenda = self.client.get('/api/v1/relatorios/agendamentos/?periodo=30d')
        self.assertEqual(agenda.status_code, status.HTTP_200_OK)
        self.assertEqual(agenda.data['total'], 1)
        self.assertEqual(self.client.get(f'/api/v1/relatorios/agendamentos/?dentista={self.dentista_b.id}').status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(self.client.get('/api/v1/dashboard/resumo/').status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(self.paciente_a)
        self.assertEqual(self.client.get('/api/v1/relatorios/pacientes/').status_code, status.HTTP_403_FORBIDDEN)
        self.client.force_authenticate(self.staff)
        self.assertEqual(self.client.get('/api/v1/relatorios/financeiro/exportar.csv?periodo=30d').status_code, status.HTTP_200_OK)
        self.assertEqual(self.client.get('/api/v1/relatorios/procedimentos/?periodo=30d').status_code, status.HTTP_200_OK)
