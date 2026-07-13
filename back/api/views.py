from django.db import transaction
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Agendamento, Clinica, Dentista, Procedimento, Usuario
from .serializers import (
    AgendamentoSerializer,
    AlterarSenhaSerializer,
    ClinicaSerializer,
    DentistaSerializer,
    PerfilUsuarioSerializer,
    ProcedimentoSerializer,
    ReagendarAgendamentoSerializer,
    RegistroUsuarioSerializer,
    UsuarioAdminSerializer,
)
from .services import (
    cancelar_agendamento,
    concluir_agendamento,
    confirmar_agendamento,
    marcar_falta_agendamento,
    reagendar_agendamento,
)


class ClinicaViewSet(viewsets.ModelViewSet):
    queryset = Clinica.objects.none()
    serializer_class = ClinicaSerializer
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['nome', 'criado_em']
    ordering = ['nome']

    def get_permissions(self):
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
        agendamento = cancelar_agendamento(self.get_object())
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
