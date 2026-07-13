from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from .models import Agendamento, Clinica, Dentista, Procedimento, Usuario
from .serializers import AgendamentoSerializer, AlterarSenhaSerializer, ClinicaSerializer, DentistaSerializer, PerfilUsuarioSerializer, ProcedimentoSerializer, RegistroUsuarioSerializer, UsuarioAdminSerializer


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
