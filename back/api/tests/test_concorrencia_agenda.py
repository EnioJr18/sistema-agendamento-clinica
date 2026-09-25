from concurrent.futures import ThreadPoolExecutor
from datetime import timedelta
from threading import Barrier
from unittest import skipUnless

from django.db import IntegrityError, OperationalError, close_old_connections, connection, transaction
from django.test import TransactionTestCase
from django.utils import timezone

from api.models import Agendamento, Clinica, Dentista, Usuario


@skipUnless(connection.vendor == 'postgresql', 'A exclusion constraint e exclusiva do PostgreSQL.')
class ConcorrenciaAgendaPostgresTest(TransactionTestCase):
    """Exerce a garantia de banco sem depender da validacao em memoria da API."""

    def setUp(self):
        self.clinica = Clinica.objects.create(nome='Clinica concorrencia A')
        self.outra_clinica = Clinica.objects.create(nome='Clinica concorrencia B')
        self.paciente = self.criar_usuario('paciente_concorrencia', '98000000001', self.clinica)
        usuario_dentista = self.criar_usuario('dentista_concorrencia', '98000000002', self.clinica, 'DENTISTA')
        usuario_dentista_b = self.criar_usuario('dentista_concorrencia_b', '98000000003', self.outra_clinica, 'DENTISTA')
        self.dentista = Dentista.objects.create(
            clinica=self.clinica, usuario=usuario_dentista, especialidade='Clinico', cro='98001-AL'
        )
        self.dentista_b = Dentista.objects.create(
            clinica=self.outra_clinica, usuario=usuario_dentista_b, especialidade='Clinico', cro='98002-AL'
        )
        self.inicio = timezone.now() + timedelta(days=10)

    @staticmethod
    def criar_usuario(username, cpf, clinica, tipo='PACIENTE'):
        return Usuario.objects.create_user(
            username=username,
            password='SenhaAtual123!',
            nome_completo=username,
            email=f'{username}@example.com',
            cpf=cpf,
            telefone='82999990000',
            data_nascimento='1990-01-01',
            clinica=clinica,
            tipo=tipo,
        )

    def criar(self, inicio, fim, *, dentista=None, clinica=None, status=Agendamento.STATUS_AGENDADA):
        dentista = dentista or self.dentista
        clinica = clinica or self.clinica
        return Agendamento.objects.create(
            clinica=clinica,
            dentista=dentista,
            paciente=self.paciente,
            procedimento='Consulta',
            data_horario=inicio,
            data_hora_fim=fim,
            duracao_minutos=int((fim - inicio).total_seconds() / 60),
            status=status,
        )

    def disputar(self, primeiro_inicio, primeiro_fim, segundo_inicio, segundo_fim):
        barreira = Barrier(2)

        def reservar(inicio, fim):
            close_old_connections()
            try:
                with transaction.atomic():
                    barreira.wait(timeout=10)
                    self.criar(inicio, fim)
                return 'criado'
            except (IntegrityError, OperationalError):
                # Escrita direta deliberadamente contorna o lock da API; o
                # PostgreSQL pode reportar exclusao ou abortar uma vitima de
                # deadlock, mas nunca confirma duas reservas incompatíveis.
                return 'conflito'
            finally:
                close_old_connections()

        with ThreadPoolExecutor(max_workers=2) as executor:
            resultados = list(executor.map(lambda intervalo: reservar(*intervalo), [(primeiro_inicio, primeiro_fim), (segundo_inicio, segundo_fim)]))
        return resultados

    def test_duas_reservas_simultaneas_no_mesmo_intervalo_criam_apenas_uma(self):
        resultados = self.disputar(self.inicio, self.inicio + timedelta(minutes=30), self.inicio, self.inicio + timedelta(minutes=30))
        self.assertCountEqual(resultados, ['criado', 'conflito'])
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_duas_reservas_simultaneas_com_sobreposicao_parcial_criam_apenas_uma(self):
        resultados = self.disputar(
            self.inicio,
            self.inicio + timedelta(minutes=60),
            self.inicio + timedelta(minutes=30),
            self.inicio + timedelta(minutes=90),
        )
        self.assertCountEqual(resultados, ['criado', 'conflito'])
        self.assertEqual(Agendamento.objects.count(), 1)

    def test_intervalos_distintos_e_status_nao_bloqueantes_sao_aceitos(self):
        self.criar(self.inicio, self.inicio + timedelta(minutes=30))
        self.criar(self.inicio + timedelta(minutes=30), self.inicio + timedelta(minutes=60))
        self.criar(self.inicio, self.inicio + timedelta(minutes=30), status=Agendamento.STATUS_CANCELADA)
        self.criar(self.inicio, self.inicio + timedelta(minutes=30), status=Agendamento.STATUS_NAO_COMPARECEU)
        self.assertEqual(Agendamento.objects.count(), 4)

    def test_dentistas_de_clinicas_distintas_nao_conflitam(self):
        # Um perfil Dentista pertence a uma unica clinica; por isso o cenario
        # valido entre clinicas usa perfis distintos no mesmo horario.
        self.criar(self.inicio, self.inicio + timedelta(minutes=30))
        self.criar(
            self.inicio,
            self.inicio + timedelta(minutes=30),
            dentista=self.dentista_b,
            clinica=self.outra_clinica,
        )
        self.assertEqual(Agendamento.objects.count(), 2)
