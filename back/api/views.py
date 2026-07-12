from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Agendamento, Dentista, Usuario
from .serializers import AgendamentoSerializer, AlterarSenhaSerializer, DentistaSerializer, PerfilUsuarioSerializer, RegistroUsuarioSerializer, UsuarioAdminSerializer


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
    queryset = Dentista.objects.all()
    serializer_class = DentistaSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['especialidade', 'ativo']
    ordering_fields = ['usuario__first_name', 'especialidade']
    ordering = ['usuario__first_name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return [permissions.IsAuthenticated()]


class AgendamentoViewSet(viewsets.ModelViewSet):
    serializer_class = AgendamentoSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['data_horario', 'criado_em']
    ordering = ['data_horario']

    def get_queryset(self):
        usuario_logado = self.request.user
        if usuario_logado.is_staff:
            return Agendamento.objects.all()
        if usuario_logado.tipo == 'DENTISTA':
            return Agendamento.objects.filter(dentista__usuario=usuario_logado)
        if usuario_logado.tipo == 'PACIENTE':
            return Agendamento.objects.filter(paciente=usuario_logado)
        return Agendamento.objects.none()

    def perform_create(self, serializer):
        usuario_logado = self.request.user
        if usuario_logado.is_staff:
            serializer.save()
        else:
            serializer.save(paciente=usuario_logado)
