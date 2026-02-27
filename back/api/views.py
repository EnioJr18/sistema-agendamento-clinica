from django.shortcuts import render
from rest_framework import viewsets
from .models import Usuario, Medico, Agendamento
from .serializers import UsuarioSerializer, MedicoSerializer, AgendamentoSerializer
from rest_framework import permissions

class UsuarioViewSet(viewsets.ModelViewSet):
    queryset = Usuario.objects.all()
    serializer_class = UsuarioSerializer
    def get_permissions(self):
        if self.action == 'create':
            # Se for POST (Criar conta), a porta está aberta!
            return [permissions.AllowAny()]
        # Para todo o resto (Ver perfil, editar, listar), exige o Token!
        return [permissions.IsAuthenticated()]

class MedicoViewSet(viewsets.ModelViewSet):
    queryset = Medico.objects.all()
    serializer_class = MedicoSerializer
    permission_classes = [permissions.IsAuthenticated]

class AgendamentoViewSet(viewsets.ModelViewSet):
    queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(paciente=self.request.user)

