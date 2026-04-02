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

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        
        return [permissions.IsAuthenticated()]

class AgendamentoViewSet(viewsets.ModelViewSet):
    queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        usuario_logado = self.request.user
        
        # Se for o ADMIN/Secretária logado, ele salva usando o ID do paciente que veio no JSON do Front-end
        if usuario_logado.is_staff or usuario_logado.tipo == 'ADMIN':
            serializer.save() 
            
        # Se for um PACIENTE comum, o sistema ignora o JSON e TRAVA a consulta no nome de quem está logado
        else:
            serializer.save(paciente=usuario_logado)

