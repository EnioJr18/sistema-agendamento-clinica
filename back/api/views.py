from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from .models import Usuario, Medico, Agendamento
from .serializers import UsuarioSerializer, MedicoSerializer, AgendamentoSerializer
from django_filters.rest_framework import DjangoFilterBackend

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

    # 1. Ativa o motor de busca do django-filter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter] 
    
    # 2. Define por quais campos o Front-end pode pesquisar
    filterset_fields = ['especialidade', 'ativo']
    
    # (Opcional) Já deixo a ordenação padrão por nome também
    ordering_fields = ['nome']
    ordering = ['nome']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        
        return [permissions.IsAuthenticated()]

class AgendamentoViewSet(viewsets.ModelViewSet):
    queryset = Agendamento.objects.all()
    serializer_class = AgendamentoSerializer
    permission_classes = [permissions.IsAuthenticated]

    # 1. Avisa que essa View aceita filtros de ordenação
    filter_backends = [filters.OrderingFilter]
    
    # 2. Quais campos o front-end pode pedir para ordenar?
    ordering_fields = ['data_horario', 'criado_em']
    
    # 3. Qual é a ordem PADRÃO se o front-end não pedir nada? 
    # (data_horario crescente = do mais próximo no tempo para o mais distante)
    ordering = ['data_horario']

    def perform_create(self, serializer):
        usuario_logado = self.request.user
        
        # Se for o ADMIN/Secretária logado, ele salva usando o ID do paciente que veio no JSON do Front-end
        if usuario_logado.is_staff or usuario_logado.tipo == 'ADMIN':
            serializer.save() 
            
        # Se for um PACIENTE comum, o sistema ignora o JSON e TRAVA a consulta no nome de quem está logado
        else:
            serializer.save(paciente=usuario_logado)

