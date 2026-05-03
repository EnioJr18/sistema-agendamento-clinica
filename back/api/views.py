from django.shortcuts import render
from rest_framework import viewsets, permissions, filters
from .models import Usuario, Dentista, Agendamento
from .serializers import UsuarioSerializer, DentistaSerializer, AgendamentoSerializer
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

class DentistaViewSet(viewsets.ModelViewSet):
    queryset = Dentista.objects.all()
    serializer_class = DentistaSerializer

    # 1. Ativa o motor de busca do django-filter
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter] 
    
    # 2. Define por quais campos o Front-end pode pesquisar
    filterset_fields = ['especialidade', 'ativo']
    
    # Ordenação cruzando a tabela Dentista -> Usuario
    ordering_fields = ['usuario__first_name', 'especialidade']
    ordering = ['usuario__first_name']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        
        return [permissions.IsAuthenticated()]

class AgendamentoViewSet(viewsets.ModelViewSet):
    serializer_class = AgendamentoSerializer
    permission_classes = [permissions.IsAuthenticated]

    # 1. Avisa que essa View aceita filtros de ordenação
    filter_backends = [filters.OrderingFilter]
    
    # 2. Quais campos o front-end pode pedir para ordenar?
    ordering_fields = ['data_horario', 'criado_em']
    
    # 3. Qual é a ordem PADRÃO se o front-end não pedir nada? 
    # (data_horario crescente = do mais próximo no tempo para o mais distante)
    ordering = ['data_horario']

    def get_queryset(self):
        """
        Filtra os agendamentos dependendo de QUEM está logado.
        """
        usuario_logado = self.request.user

        # 1. Se for o ADMIN ou a Secretária: Vê a agenda da clínica inteira
        if usuario_logado.is_staff or usuario_logado.tipo == 'ADMIN':
            return Agendamento.objects.all()

        # 2. Se for um DENTISTA: Vê apenas os agendamentos vinculados a ele
        elif usuario_logado.tipo == 'DENTISTA':
            # Atravessamos a relação: Agendamento -> Dentista -> Usuario
            return Agendamento.objects.filter(dentista__usuario=usuario_logado)

        # 3. Se for um PACIENTE comum: Vê apenas as próprias consultas marcadas
        elif usuario_logado.tipo == 'PACIENTE':
            return Agendamento.objects.filter(paciente=usuario_logado)

        # Retorno de segurança caso o usuário não se encaixe em nada
        return Agendamento.objects.none()

    def perform_create(self, serializer):
        usuario_logado = self.request.user
        
        # Se for o ADMIN/Secretária logado, ele salva usando o ID do paciente que veio no JSON do Front-end
        if usuario_logado.is_staff or usuario_logado.tipo == 'ADMIN':
            serializer.save() 
            
        # Se for um PACIENTE comum, o sistema ignora o JSON e TRAVA a consulta no nome de quem está logado
        else:
            serializer.save(paciente=usuario_logado)

