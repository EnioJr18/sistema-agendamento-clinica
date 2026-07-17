from django.conf import settings
from django.db import IntegrityError, transaction
from django.urls import reverse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError
from rest_framework.response import Response

from .models import (
    Agendamento,
    BloqueioAgendaClinica,
    Clinica,
    ConviteCadastroPaciente,
    Dentista,
    EvolucaoClinica,
    HorarioFuncionamentoClinica,
    IndisponibilidadeDentista,
    ItemPlanoTratamento,
    Odontograma,
    PlanoTratamento,
    Procedimento,
    ProntuarioPaciente,
    RegistroOdontograma,
    Usuario,
)
from .serializers import (
    AgendamentoSerializer,
    AlterarSenhaSerializer,
    AnamneseSerializer,
    BloqueioAgendaClinicaSerializer,
    CadastroViaConviteSerializer,
    ClinicaSerializer,
    ConviteCadastroPacienteSerializer,
    DentistaSerializer,
    EvolucaoClinicaSerializer,
    HorarioFuncionamentoClinicaSerializer,
    IndisponibilidadeDentistaSerializer,
    ItemPlanoTratamentoSerializer,
    OdontogramaSerializer,
    PerfilUsuarioSerializer,
    PlanoTratamentoSerializer,
    ProcedimentoSerializer,
    ProntuarioPacienteSerializer,
    ReagendarAgendamentoSerializer,
    RegistroOdontogramaSerializer,
    RegistroUsuarioSerializer,
    UsuarioAdminSerializer,
)
from .services import (
    cancelar_agendamento,
    concluir_agendamento,
    confirmar_agendamento,
    marcar_falta_agendamento,
    reagendar_agendamento,
    transicionar_plano,
    validar_contexto_odontologico,
    validar_criacao_evolucao,
)


class ClinicaViewSet(viewsets.ModelViewSet):
    queryset = Clinica.objects.none()
    serializer_class = ClinicaSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['nome', 'criado_em']
    ordering = ['nome']

    def get_permissions(self):
        if self.action == 'cadastrar_paciente':
            return [permissions.AllowAny()]
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Clinica.objects.none()
        usuario = self.request.user
        if usuario.is_staff:
            return Clinica.objects.all()
        if usuario.clinica_id:
            return Clinica.objects.filter(pk=usuario.clinica_id)
        return Clinica.objects.none()

    @extend_schema(request=RegistroUsuarioSerializer, responses=RegistroUsuarioSerializer)
    @action(detail=False, methods=['post'], url_path=r'(?P<slug>[-a-zA-Z0-9_]+)/pacientes')
    def cadastrar_paciente(self, request, slug=None):
        try:
            clinica = Clinica.objects.get(slug=slug)
        except Clinica.DoesNotExist:
            return Response({'detail': 'Clinica nao encontrada.'}, status=status.HTTP_404_NOT_FOUND)
        if not clinica.ativa:
            raise ValidationError({'clinica': 'Clinica inativa nao permite cadastro publico.'})

        serializer = RegistroUsuarioSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        usuario = serializer.save(clinica=clinica)
        return Response(RegistroUsuarioSerializer(usuario, context={'request': request}).data, status=status.HTTP_201_CREATED)


class HorarioFuncionamentoClinicaViewSet(viewsets.ModelViewSet):
    queryset = HorarioFuncionamentoClinica.objects.none()
    serializer_class = HorarioFuncionamentoClinicaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['clinica', 'dia_semana', 'ativo']
    ordering_fields = ['dia_semana', 'horario_inicio']
    ordering = ['dia_semana', 'horario_inicio']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return HorarioFuncionamentoClinica.objects.none()
        usuario = self.request.user
        if usuario.is_staff:
            return HorarioFuncionamentoClinica.objects.all()
        if usuario.clinica_id:
            return HorarioFuncionamentoClinica.objects.filter(clinica_id=usuario.clinica_id)
        return HorarioFuncionamentoClinica.objects.none()


class BloqueioAgendaClinicaViewSet(viewsets.ModelViewSet):
    queryset = BloqueioAgendaClinica.objects.none()
    serializer_class = BloqueioAgendaClinicaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['clinica', 'ativo']
    ordering_fields = ['inicio', 'fim', 'criado_em']
    ordering = ['inicio']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return BloqueioAgendaClinica.objects.none()
        usuario = self.request.user
        if usuario.is_staff:
            return BloqueioAgendaClinica.objects.all()
        if usuario.clinica_id:
            return BloqueioAgendaClinica.objects.filter(clinica_id=usuario.clinica_id)
        return BloqueioAgendaClinica.objects.none()


class IndisponibilidadeDentistaViewSet(viewsets.ModelViewSet):
    queryset = IndisponibilidadeDentista.objects.none()
    serializer_class = IndisponibilidadeDentistaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['clinica', 'dentista', 'ativo']
    ordering_fields = ['inicio', 'fim', 'criado_em']
    ordering = ['inicio']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return IndisponibilidadeDentista.objects.none()
        usuario = self.request.user
        if usuario.is_staff:
            return IndisponibilidadeDentista.objects.all()
        if usuario.clinica_id:
            return IndisponibilidadeDentista.objects.filter(clinica_id=usuario.clinica_id)
        return IndisponibilidadeDentista.objects.none()


class ConviteCadastroPacienteViewSet(viewsets.ModelViewSet):
    queryset = ConviteCadastroPaciente.objects.none()
    serializer_class = ConviteCadastroPacienteSerializer
    lookup_field = 'token'
    lookup_value_regex = '[-_a-zA-Z0-9]+'
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['clinica', 'ativo']
    ordering_fields = ['expira_em', 'criado_em', 'usado_em']
    ordering = ['-criado_em']

    def get_permissions(self):
        if self.action == 'cadastrar':
            return [permissions.AllowAny()]
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ConviteCadastroPaciente.objects.none()
        usuario = self.request.user
        if usuario.is_staff:
            return ConviteCadastroPaciente.objects.select_related('clinica', 'criado_por')
        if usuario.clinica_id:
            return ConviteCadastroPaciente.objects.select_related('clinica', 'criado_por').filter(clinica_id=usuario.clinica_id)
        return ConviteCadastroPaciente.objects.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        convite = serializer.save(criado_por=request.user)
        dados = self.get_serializer(convite).data
        endpoint_cadastro = request.build_absolute_uri(
            reverse('convite-paciente-cadastrar', kwargs={'token': convite.token})
        )
        frontend_base_url = getattr(settings, 'FRONTEND_BASE_URL', '')
        dados['token'] = convite.token
        dados['endpoint_cadastro'] = endpoint_cadastro
        dados['link_cadastro'] = (
            f'{frontend_base_url}/cadastro?convite={convite.token}'
            if frontend_base_url
            else endpoint_cadastro
        )
        headers = self.get_success_headers(dados)
        return Response(dados, status=status.HTTP_201_CREATED, headers=headers)

    @extend_schema(request=CadastroViaConviteSerializer, responses=RegistroUsuarioSerializer)
    @action(detail=True, methods=['post'], url_path='cadastrar')
    def cadastrar(self, request, token=None):
        with transaction.atomic():
            try:
                convite = ConviteCadastroPaciente.objects.select_for_update().select_related('clinica').get(token=token)
            except ConviteCadastroPaciente.DoesNotExist:
                return Response({'detail': 'Convite nao encontrado.'}, status=status.HTTP_404_NOT_FOUND)

            if not convite.clinica.ativa:
                raise ValidationError({'clinica': 'Clinica inativa nao permite cadastro por convite.'})
            if not convite.ativo:
                raise ValidationError({'convite': 'Convite inativo.'})
            if convite.usado_em is not None:
                raise ValidationError({'convite': 'Convite ja utilizado.'})
            if convite.expira_em <= timezone.now():
                raise ValidationError({'convite': 'Convite expirado.'})

            serializer = CadastroViaConviteSerializer(data=request.data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            usuario = serializer.save(clinica=convite.clinica)
            convite.usado_em = timezone.now()
            convite.save(update_fields=['usado_em', 'atualizado_em'])

        return Response(RegistroUsuarioSerializer(usuario, context={'request': request}).data, status=status.HTTP_201_CREATED)


class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        if self.action in ['list', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        # is_staff e a unica regra de administracao da API.
        if self.request.user.is_staff:
            return Usuario.objects.all()
        return Usuario.objects.filter(pk=self.request.user.pk)

    def get_serializer_class(self):
        if self.action == 'create':
            return RegistroUsuarioSerializer
        if self.action == 'alterar_senha':
            return AlterarSenhaSerializer
        if self.request.user.is_staff:
            return UsuarioAdminSerializer
        return PerfilUsuarioSerializer

    @action(detail=False, methods=['post'], url_path='alterar-senha')
    def alterar_senha(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['nova_senha'])
        request.user.save(update_fields=['password'])
        return Response(status=status.HTTP_204_NO_CONTENT)


class DentistaViewSet(viewsets.ModelViewSet):
    queryset = Dentista.objects.none()
    serializer_class = DentistaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['especialidade', 'ativo']
    ordering_fields = ['usuario__nome_completo', 'especialidade']
    ordering = ['usuario__nome_completo']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Dentista.objects.none()
        usuario = self.request.user
        if usuario.is_staff:
            return Dentista.objects.all()
        if usuario.clinica_id:
            return Dentista.objects.filter(clinica_id=usuario.clinica_id)
        return Dentista.objects.none()


class ProcedimentoViewSet(viewsets.ModelViewSet):
    queryset = Procedimento.objects.none()
    serializer_class = ProcedimentoSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['ativo']
    ordering_fields = ['nome', 'criado_em']
    ordering = ['nome']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Procedimento.objects.none()
        usuario = self.request.user
        if usuario.is_staff:
            return Procedimento.objects.all()
        if usuario.clinica_id:
            return Procedimento.objects.filter(clinica_id=usuario.clinica_id)
        return Procedimento.objects.none()


class ProntuarioPacienteViewSet(viewsets.ModelViewSet):
    queryset = ProntuarioPaciente.objects.none()
    serializer_class = ProntuarioPacienteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['clinica', 'paciente', 'ativo']
    ordering_fields = ['paciente__nome_completo', 'criado_em', 'atualizado_em']
    ordering = ['paciente__nome_completo']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ProntuarioPaciente.objects.none()
        usuario = self.request.user
        queryset = ProntuarioPaciente.objects.select_related('clinica', 'paciente', 'criado_por', 'atualizado_por')
        if usuario.is_staff:
            return queryset
        if not usuario.clinica_id:
            return queryset.none()
        if usuario.tipo == 'PACIENTE':
            return queryset.filter(clinica_id=usuario.clinica_id, paciente=usuario)
        if usuario.tipo == 'DENTISTA':
            return queryset.filter(clinica_id=usuario.clinica_id)
        return queryset.none()

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise PermissionDenied('Apenas staff/admin pode criar prontuarios.')
        try:
            with transaction.atomic():
                return super().create(request, *args, **kwargs)
        except IntegrityError:
            raise ValidationError({'paciente': 'Ja existe prontuario para este paciente nesta clinica.'})

    def perform_create(self, serializer):
        serializer.save(criado_por=self.request.user, atualizado_por=self.request.user)

    def perform_update(self, serializer):
        if not self.request.user.is_staff:
            raise PermissionDenied('Apenas staff/admin pode alterar o prontuario.')
        serializer.save(atualizado_por=self.request.user)

    def destroy(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Prontuarios nao podem ser excluidos fisicamente.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    @extend_schema(request=AnamneseSerializer, responses=AnamneseSerializer)
    @action(detail=True, methods=['get', 'patch'], url_path='anamnese')
    def anamnese(self, request, pk=None):
        prontuario = self.get_object()
        if request.method == 'GET':
            try:
                return Response(AnamneseSerializer(prontuario.anamnese).data)
            except ProntuarioPaciente.anamnese.RelatedObjectDoesNotExist as exc:
                raise NotFound('Anamnese ainda nao preenchida.') from exc

        if request.user.tipo == 'PACIENTE' and not request.user.is_staff:
            raise PermissionDenied('Paciente nao pode alterar dados clinicos.')
        if not request.user.is_staff and request.user.tipo != 'DENTISTA':
            raise PermissionDenied('Usuario sem permissao para alterar anamnese.')
        try:
            anamnese = prontuario.anamnese
            serializer = AnamneseSerializer(anamnese, data=request.data, partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save(atualizada_por=request.user)
        except ProntuarioPaciente.anamnese.RelatedObjectDoesNotExist:
            serializer = AnamneseSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            anamnese = serializer.save(
                prontuario=prontuario,
                preenchida_por=request.user,
                atualizada_por=request.user,
            )
        return Response(AnamneseSerializer(anamnese).data)

    @extend_schema(responses=EvolucaoClinicaSerializer(many=True))
    @action(detail=True, methods=['get'], url_path='evolucoes')
    def evolucoes(self, request, pk=None):
        prontuario = self.get_object()
        if request.user.tipo == 'PACIENTE' and not request.user.is_staff:
            raise PermissionDenied('Paciente nao acessa evolucoes clinicas nesta fase.')
        queryset = prontuario.evolucoes.select_related('agendamento', 'dentista__usuario', 'criado_por')
        return Response(EvolucaoClinicaSerializer(queryset, many=True).data)


class EvolucaoClinicaViewSet(viewsets.ModelViewSet):
    queryset = EvolucaoClinica.objects.none()
    serializer_class = EvolucaoClinicaSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['prontuario', 'agendamento', 'dentista']
    ordering_fields = ['criado_em', 'atualizado_em']
    ordering = ['-criado_em']

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return EvolucaoClinica.objects.none()
        usuario = self.request.user
        queryset = EvolucaoClinica.objects.select_related('prontuario__clinica', 'agendamento', 'dentista__usuario', 'criado_por')
        if usuario.is_staff:
            return queryset
        if usuario.tipo == 'DENTISTA' and usuario.clinica_id:
            return queryset.filter(prontuario__clinica_id=usuario.clinica_id)
        return queryset.none()

    def perform_create(self, serializer):
        usuario = self.request.user
        if usuario.is_staff:
            dentista = serializer.validated_data.get('dentista')
            if not dentista:
                raise ValidationError({'dentista': 'Informe o dentista responsavel.'})
        elif usuario.tipo == 'DENTISTA' and usuario.clinica_id:
            try:
                dentista = usuario.perfil_dentista
            except Dentista.DoesNotExist as exc:
                raise PermissionDenied('Usuario dentista sem perfil profissional.') from exc
            enviado = serializer.validated_data.get('dentista')
            if enviado and enviado.pk != dentista.pk:
                raise PermissionDenied('Dentista nao pode registrar evolucao para outro profissional.')
        else:
            raise PermissionDenied('Paciente nao pode criar evolucoes clinicas.')

        prontuario = serializer.validated_data['prontuario']
        agendamento = serializer.validated_data['agendamento']
        validar_criacao_evolucao(prontuario=prontuario, agendamento=agendamento, dentista=dentista)
        serializer.save(dentista=dentista, criado_por=usuario)

    def update(self, request, *args, **kwargs):
        evolucao = self.get_object()
        if not request.user.is_staff and evolucao.criado_por_id != request.user.id:
            raise PermissionDenied('Apenas o autor ou staff/admin pode editar a evolucao.')
        imutaveis = {'prontuario', 'agendamento', 'dentista', 'criado_por'} & set(request.data)
        if imutaveis:
            raise ValidationError({campo: 'Campo historico imutavel.' for campo in imutaveis})
        return super().update(request, *args, **kwargs)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Evolucoes clinicas nao podem ser excluidas fisicamente.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )


class ClinicoBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        if not request.user.is_staff and request.user.tipo != 'DENTISTA':
            raise PermissionDenied('Paciente nao pode criar dados clinicos.')
        return super().create(request, *args, **kwargs)

    def clinica_queryset(self, queryset, campo='clinica_id'):
        user = self.request.user
        if user.is_staff:
            return queryset
        if not user.clinica_id:
            return queryset.none()
        if user.tipo == 'PACIENTE':
            return queryset.filter(**{f'{campo}': user.clinica_id, 'prontuario__paciente': user})
        if user.tipo == 'DENTISTA':
            return queryset.filter(**{campo: user.clinica_id})
        return queryset.none()

    def profissional(self):
        if self.request.user.is_staff:
            return None
        if self.request.user.tipo != 'DENTISTA':
            raise PermissionDenied('Paciente nao pode alterar dados clinicos.')
        try:
            return self.request.user.perfil_dentista
        except Dentista.DoesNotExist as exc:
            raise PermissionDenied('Usuario dentista sem perfil profissional.') from exc


class OdontogramaViewSet(ClinicoBaseViewSet):
    serializer_class = OdontogramaSerializer
    queryset = Odontograma.objects.none()

    def get_queryset(self):
        return self.clinica_queryset(Odontograma.objects.select_related('prontuario__paciente'), 'clinica_id')

    def perform_create(self, serializer):
        dentista = self.profissional()
        prontuario = serializer.validated_data['prontuario']
        clinica = prontuario.clinica
        validar_contexto_odontologico(prontuario=prontuario, clinica=clinica, dentista=dentista)
        try:
            serializer.save(clinica=clinica, criado_por=self.request.user, atualizado_por=self.request.user)
        except IntegrityError as exc:
            raise ValidationError({'prontuario': 'Ja existe odontograma ativo para este prontuario.'}) from exc

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Odontogramas nao podem ser excluidos fisicamente.'}, status=405)


class RegistroOdontogramaViewSet(ClinicoBaseViewSet):
    serializer_class = RegistroOdontogramaSerializer
    queryset = RegistroOdontograma.objects.none()

    def get_queryset(self):
        queryset = RegistroOdontograma.objects.select_related('odontograma__prontuario__paciente', 'dentista')
        if self.request.user.tipo == 'PACIENTE' and not self.request.user.is_staff:
            return queryset.filter(odontograma__prontuario__paciente=self.request.user)
        return self.clinica_queryset(queryset, 'odontograma__clinica_id')

    def perform_create(self, serializer):
        dentista = self.profissional()
        if dentista is None:
            dentista = serializer.validated_data.get('dentista')
        if not dentista:
            raise ValidationError({'dentista': 'Informe o dentista responsavel.'})
        odontograma = serializer.validated_data['odontograma']
        validar_contexto_odontologico(prontuario=odontograma.prontuario, clinica=odontograma.clinica, dentista=dentista)
        serializer.save(dentista=dentista, criado_por=self.request.user)

    def update(self, request, *args, **kwargs):
        raise ValidationError({'detail': 'Registros odontologicos sao historicos e imutaveis.'})

    partial_update = update

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Registros odontologicos nao podem ser excluidos fisicamente.'}, status=405)


class PlanoTratamentoViewSet(ClinicoBaseViewSet):
    serializer_class = PlanoTratamentoSerializer
    queryset = PlanoTratamento.objects.none()

    def get_queryset(self):
        return self.clinica_queryset(PlanoTratamento.objects.select_related('prontuario__paciente'), 'clinica_id')

    def perform_create(self, serializer):
        dentista = self.profissional()
        prontuario = serializer.validated_data['prontuario']
        validar_contexto_odontologico(prontuario=prontuario, clinica=prontuario.clinica, dentista=dentista)
        serializer.save(clinica=prontuario.clinica, criado_por=self.request.user)

    def update(self, request, *args, **kwargs):
        self.profissional()
        if {'clinica', 'prontuario', 'status', 'criado_por'} & set(request.data):
            raise ValidationError({'detail': 'Campos de contexto e status sao imutaveis nesta rota.'})
        return super().update(request, *args, **kwargs)

    partial_update = update

    def _transicao(self, request, status_destino, pk):
        self.profissional()
        return Response(self.get_serializer(transicionar_plano(self.get_object(), status_destino)).data)

    @action(detail=True, methods=['post'])
    def propor(self, request, pk=None): return self._transicao(request, 'PROPOSTO', pk)
    @action(detail=True, methods=['post'])
    def aprovar(self, request, pk=None): return self._transicao(request, 'APROVADO', pk)
    @action(detail=True, methods=['post'])
    def iniciar(self, request, pk=None): return self._transicao(request, 'EM_ANDAMENTO', pk)
    @action(detail=True, methods=['post'])
    def concluir(self, request, pk=None): return self._transicao(request, 'CONCLUIDO', pk)
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None): return self._transicao(request, 'CANCELADO', pk)


class ItemPlanoTratamentoViewSet(ClinicoBaseViewSet):
    serializer_class = ItemPlanoTratamentoSerializer
    queryset = ItemPlanoTratamento.objects.none()

    def get_queryset(self):
        queryset = ItemPlanoTratamento.objects.select_related('plano__prontuario__paciente', 'procedimento_ref')
        if self.request.user.tipo == 'PACIENTE' and not self.request.user.is_staff:
            return queryset.filter(plano__prontuario__paciente=self.request.user)
        return self.clinica_queryset(queryset, 'plano__clinica_id')

    def perform_create(self, serializer):
        self.profissional()
        plano = serializer.validated_data['plano']
        if plano.status in {'CONCLUIDO', 'CANCELADO'}:
            raise ValidationError({'plano': 'Plano concluido ou cancelado nao aceita novos itens.'})
        procedimento = serializer.validated_data.get('procedimento_ref')
        if procedimento and procedimento.clinica_id != plano.clinica_id:
            raise ValidationError({'procedimento_ref': 'Procedimento pertence a outra clinica.'})
        serializer.save()

    def update(self, request, *args, **kwargs):
        self.profissional()
        if 'plano' in request.data:
            raise ValidationError({'plano': 'Item nao pode ser movido para outro plano.'})
        return super().update(request, *args, **kwargs)

    partial_update = update


class AgendamentoViewSet(viewsets.ModelViewSet):
    queryset = Agendamento.objects.none()
    serializer_class = AgendamentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['data_horario', 'criado_em']
    ordering = ['data_horario']

    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Use as acoes explicitas de agendamento.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def partial_update(self, request, *args, **kwargs):
        return Response(
            {'detail': 'Use as acoes explicitas de agendamento.'},
            status=status.HTTP_405_METHOD_NOT_ALLOWED,
        )

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Agendamento.objects.none()
        usuario_logado = self.request.user
        if usuario_logado.is_staff:
            return Agendamento.objects.all()
        if not usuario_logado.clinica_id:
            return Agendamento.objects.none()
        if usuario_logado.tipo == 'DENTISTA':
            return Agendamento.objects.filter(clinica_id=usuario_logado.clinica_id, dentista__usuario=usuario_logado)
        if usuario_logado.tipo == 'PACIENTE':
            return Agendamento.objects.filter(clinica_id=usuario_logado.clinica_id, paciente=usuario_logado)
        return Agendamento.objects.none()

    def perform_create(self, serializer):
        usuario_logado = self.request.user
        if usuario_logado.is_staff:
            serializer.save()
        elif not usuario_logado.clinica_id:
            raise PermissionDenied('Usuario sem clinica vinculada.')
        else:
            serializer.save(paciente=usuario_logado, clinica=usuario_logado.clinica)

    def _exigir_profissional_ou_staff(self, request):
        if request.user.is_staff or request.user.tipo == 'DENTISTA':
            return
        raise PermissionDenied('Paciente nao tem permissao para esta acao.')

    @extend_schema(request=None, responses=AgendamentoSerializer)
    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        agendamento = cancelar_agendamento(self.get_object(), usuario=request.user)
        return Response(self.get_serializer(agendamento).data)

    @extend_schema(request=None, responses=AgendamentoSerializer)
    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        self._exigir_profissional_ou_staff(request)
        agendamento = confirmar_agendamento(self.get_object())
        return Response(self.get_serializer(agendamento).data)

    @extend_schema(request=None, responses=AgendamentoSerializer)
    @action(detail=True, methods=['post'])
    def concluir(self, request, pk=None):
        self._exigir_profissional_ou_staff(request)
        agendamento = concluir_agendamento(self.get_object())
        return Response(self.get_serializer(agendamento).data)

    @extend_schema(request=None, responses=AgendamentoSerializer)
    @action(detail=True, methods=['post'], url_path='marcar-falta')
    def marcar_falta(self, request, pk=None):
        self._exigir_profissional_ou_staff(request)
        agendamento = marcar_falta_agendamento(self.get_object())
        return Response(self.get_serializer(agendamento).data)

    @extend_schema(request=ReagendarAgendamentoSerializer, responses=AgendamentoSerializer)
    @action(detail=True, methods=['post'])
    def reagendar(self, request, pk=None):
        agendamento = self.get_object()
        serializer = ReagendarAgendamentoSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        agendamento = reagendar_agendamento(agendamento, serializer.validated_data['data_horario'])
        return Response(self.get_serializer(agendamento).data)
