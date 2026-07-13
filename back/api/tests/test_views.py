from django.conf import settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import Agendamento, Clinica, Dentista, Procedimento, Usuario


def criar_usuario(username, cpf, email, password='SenhaAtual123!', tipo='PACIENTE', **extra):
    dados = {
        'username': username,
        'password': password,
        'tipo': tipo,
        'nome_completo': extra.pop('nome_completo', f'Usuario {username}'),
        'email': email,
        'cpf': cpf,
        'data_nascimento': extra.pop('data_nascimento', '1990-01-01'),
        'telefone': extra.pop('telefone', '82999999999'),
    }
    dados.update(extra)
    return Usuario.objects.create_user(**dados)


class DentistaViewSetTest(APITestCase):
    def setUp(self):
        self.clinica = Clinica.objects.create(nome='Clinica Teste')
        self.paciente = criar_usuario(
            username='paciente_teste',
            cpf='10000000001',
            email='paciente@example.com',
            clinica=self.clinica,
        )
        self.user_dentista = criar_usuario(
            username='dentista_teste',
            cpf='10000000002',
            email='dentista@example.com',
            nome_completo='Ana Silva',
            tipo='DENTISTA',
            clinica=self.clinica,
        )
        Dentista.objects.create(
            clinica=self.clinica,
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


class UsuarioCadastroViewSetTest(APITestCase):
    def setUp(self):
        self.lista_url = reverse('usuario-list')

    def payload_cadastro(self, **overrides):
        payload = {
            'username': 'novo_usuario',
            'password': 'SenhaForte123!',
            'nome_completo': 'Novo Paciente',
            'nome_preferido': '',
            'email': 'novo.paciente@example.com',
            'cpf': '123.456.789-09',
            'data_nascimento': '1995-04-20',
            'telefone': '82988887777',
        }
        payload.update(overrides)
        return payload

    def test_cadastro_publico_cria_paciente_com_dados_padronizados(self):
        response = self.client.post(self.lista_url, self.payload_cadastro(), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        usuario = Usuario.objects.get(username='novo_usuario')
        self.assertEqual(usuario.tipo, 'PACIENTE')
        self.assertEqual(usuario.nome_completo, 'Novo Paciente')
        self.assertEqual(usuario.nome_preferido, '')
        self.assertEqual(usuario.email, 'novo.paciente@example.com')
        self.assertEqual(usuario.cpf, '12345678909')
        self.assertEqual(usuario.telefone, '82988887777')
        self.assertNotIn('password', response.data)
        self.assertNotIn('tipo', response.data)

    def test_cadastro_publico_nao_permite_criar_admin(self):
        response = self.client.post(self.lista_url, self.payload_cadastro(tipo='ADMIN'), format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        usuario = Usuario.objects.get(username='novo_usuario')
        self.assertEqual(usuario.tipo, 'PACIENTE')

    def test_cpf_duplicado_deve_ser_rejeitado(self):
        criar_usuario('existente', '12345678909', 'existente@example.com')

        response = self.client.post(self.lista_url, self.payload_cadastro(), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('cpf', response.data)

    def test_email_duplicado_deve_ser_rejeitado(self):
        criar_usuario('existente', '99999999999', 'novo.paciente@example.com')

        response = self.client.post(self.lista_url, self.payload_cadastro(), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('email', response.data)

    def test_telefone_obrigatorio_deve_ser_validado(self):
        response = self.client.post(self.lista_url, self.payload_cadastro(telefone=''), format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('telefone', response.data)

    def test_endereco_estruturado_e_salvo_e_retornado(self):
        response = self.client.post(
            self.lista_url,
            self.payload_cadastro(
                endereco={
                    'cep': '57000-000',
                    'logradouro': 'Rua das Flores',
                    'numero': '123',
                    'complemento': 'Sala 2',
                    'bairro': 'Centro',
                    'cidade': 'Maceio',
                    'estado': 'AL',
                }
            ),
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        usuario = Usuario.objects.get(username='novo_usuario')
        self.assertEqual(usuario.endereco.cidade, 'Maceio')
        self.assertEqual(response.data['endereco']['logradouro'], 'Rua das Flores')
        self.assertEqual(response.data['endereco']['estado'], 'AL')


class UsuarioSegurancaViewSetTest(APITestCase):
    def setUp(self):
        self.clinica = Clinica.objects.create(nome='Clinica A')
        self.outra_clinica = Clinica.objects.create(nome='Clinica B')
        self.usuario = criar_usuario(
            username='paciente_um',
            cpf='20000000001',
            email='paciente.um@example.com',
            nome_completo='Paciente Um',
            clinica=self.clinica,
        )
        self.outro_usuario = criar_usuario(
            username='paciente_dois',
            cpf='20000000002',
            email='paciente.dois@example.com',
            clinica=self.outra_clinica,
        )
        self.admin = criar_usuario(
            username='administrador',
            cpf='20000000003',
            email='admin@example.com',
            tipo='ADMIN',
            is_staff=True,
        )
        self.lista_url = reverse('usuario-list')
        self.detalhe_outro_url = reverse('usuario-detail', args=[self.outro_usuario.pk])
        self.meu_perfil_url = reverse('usuario-detail', args=[self.usuario.pk])
        self.alterar_senha_url = reverse('usuario-alterar-senha')

    def test_usuario_comum_nao_lista_usuarios(self):
        self.client.force_authenticate(self.usuario)
        response = self.client.get(self.lista_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_usuario_comum_nao_acessa_outro_perfil(self):
        self.client.force_authenticate(self.usuario)
        response = self.client.get(self.detalhe_outro_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_usuario_comum_nao_altera_tipo_cpf_ou_senha_no_endpoint_comum(self):
        senha_original = self.usuario.password
        cpf_original = self.usuario.cpf
        self.client.force_authenticate(self.usuario)
        response = self.client.patch(
            self.meu_perfil_url,
            {
                'nome_preferido': 'Paciente',
                'telefone': '82977776666',
                'tipo': 'ADMIN',
                'clinica': self.outra_clinica.pk,
                'cpf': '30000000000',
                'password': 'TextoPuro123!',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.tipo, 'PACIENTE')
        self.assertEqual(self.usuario.clinica_id, self.clinica.id)
        self.assertEqual(self.usuario.cpf, cpf_original)
        self.assertEqual(self.usuario.password, senha_original)
        self.assertEqual(self.usuario.telefone, '82977776666')
        self.assertNotIn('password', response.data)
        self.assertNotIn('tipo', response.data)

    def test_atualizacao_de_perfil_respeita_campos_permitidos(self):
        self.client.force_authenticate(self.usuario)
        response = self.client.patch(
            self.meu_perfil_url,
            {
                'nome_completo': 'Paciente Um Atualizado',
                'nome_preferido': 'Paciente',
                'email': 'paciente.atualizado@example.com',
                'telefone': '82966665555',
                'data_nascimento': '1991-02-03',
                'endereco': {
                    'cep': '57000-111',
                    'logradouro': 'Avenida Principal',
                    'numero': '456',
                    'bairro': 'Farol',
                    'cidade': 'Maceio',
                    'estado': 'AL',
                },
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.usuario.refresh_from_db()
        self.assertEqual(self.usuario.nome_completo, 'Paciente Um Atualizado')
        self.assertEqual(self.usuario.email, 'paciente.atualizado@example.com')
        self.assertEqual(self.usuario.endereco.numero, '456')
        self.assertEqual(response.data['endereco']['bairro'], 'Farol')

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


class MultiClinicaViewSetTest(APITestCase):
    def setUp(self):
        self.clinica_a = Clinica.objects.create(nome='Clinica A')
        self.clinica_b = Clinica.objects.create(nome='Clinica B')
        self.staff = criar_usuario(
            username='staff',
            cpf='50000000001',
            email='staff@example.com',
            is_staff=True,
            tipo='ADMIN',
        )
        self.paciente_a = criar_usuario(
            username='paciente_a',
            cpf='50000000002',
            email='paciente.a@example.com',
            nome_completo='Paciente A',
            clinica=self.clinica_a,
        )
        self.paciente_b = criar_usuario(
            username='paciente_b',
            cpf='50000000003',
            email='paciente.b@example.com',
            nome_completo='Paciente B',
            clinica=self.clinica_b,
        )
        self.usuario_dentista_a = criar_usuario(
            username='dentista_a',
            cpf='50000000004',
            email='dentista.a@example.com',
            nome_completo='Dentista A',
            tipo='DENTISTA',
            clinica=self.clinica_a,
        )
        self.usuario_dentista_b = criar_usuario(
            username='dentista_b',
            cpf='50000000005',
            email='dentista.b@example.com',
            nome_completo='Dentista B',
            tipo='DENTISTA',
            clinica=self.clinica_b,
        )
        self.dentista_a = Dentista.objects.create(
            clinica=self.clinica_a,
            usuario=self.usuario_dentista_a,
            especialidade='Ortodontia',
            cro='CRO-A',
        )
        self.dentista_b = Dentista.objects.create(
            clinica=self.clinica_b,
            usuario=self.usuario_dentista_b,
            especialidade='Implantodontia',
            cro='CRO-B',
        )
        self.procedimento_a = Procedimento.objects.create(
            clinica=self.clinica_a,
            nome='Limpeza',
            duracao_minutos=30,
        )
        self.procedimento_b = Procedimento.objects.create(
            clinica=self.clinica_b,
            nome='Clareamento',
            duracao_minutos=45,
        )
        self.agendamento_b = Agendamento.objects.create(
            clinica=self.clinica_b,
            dentista=self.dentista_b,
            paciente=self.paciente_b,
            procedimento='Clareamento',
            procedimento_ref=self.procedimento_b,
            data_horario='2030-01-10T10:00:00Z',
        )

    def test_staff_consegue_criar_clinica(self):
        self.client.force_authenticate(self.staff)
        response = self.client.post(
            reverse('clinica-list'),
            {'nome': 'Clinica Nova', 'cnpj': '12.345.678/0001-99', 'telefone': '82911112222', 'email': 'nova@example.com'},
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(Clinica.objects.filter(nome='Clinica Nova').exists())

    def test_usuario_comum_lista_apenas_sua_clinica(self):
        self.client.force_authenticate(self.paciente_a)
        response = self.client.get(reverse('clinica-list'))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['id'], self.clinica_a.id)

    def test_usuario_de_clinica_a_nao_acessa_dentista_da_clinica_b(self):
        self.client.force_authenticate(self.paciente_a)
        response = self.client.get(reverse('dentista-detail', args=[self.dentista_b.pk]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_usuario_de_clinica_a_recebe_404_para_agendamento_da_clinica_b(self):
        self.client.force_authenticate(self.paciente_a)
        response = self.client.get(reverse('agendamento-detail', args=[self.agendamento_b.pk]))

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_usuario_de_clinica_a_nao_cria_agendamento_com_dentista_da_clinica_b(self):
        self.client.force_authenticate(self.paciente_a)
        response = self.client.post(
            reverse('agendamento-list'),
            {
                'dentista': self.dentista_b.pk,
                'procedimento': 'Consulta',
                'data_horario': '2030-01-11T10:00:00Z',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('dentista', response.data)

    def test_usuario_de_clinica_a_nao_cria_agendamento_com_procedimento_da_clinica_b(self):
        self.client.force_authenticate(self.paciente_a)
        response = self.client.post(
            reverse('agendamento-list'),
            {
                'dentista': self.dentista_a.pk,
                'procedimento_ref': self.procedimento_b.pk,
                'data_horario': '2030-01-12T10:00:00Z',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('procedimento_ref', response.data)

    def test_agendamento_criado_por_usuario_comum_recebe_clinica_do_usuario(self):
        self.client.force_authenticate(self.paciente_a)
        response = self.client.post(
            reverse('agendamento-list'),
            {
                'dentista': self.dentista_a.pk,
                'procedimento_ref': self.procedimento_a.pk,
                'data_horario': '2030-01-13T10:00:00Z',
            },
            format='json',
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        agendamento = Agendamento.objects.get(pk=response.data['id'])
        self.assertEqual(agendamento.clinica_id, self.clinica_a.id)
        self.assertEqual(agendamento.paciente_id, self.paciente_a.id)
        self.assertEqual(agendamento.procedimento, 'Limpeza')
