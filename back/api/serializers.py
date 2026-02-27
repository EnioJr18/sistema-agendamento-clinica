from rest_framework import serializers
from .models import Usuario, Medico, Agendamento


class UsuarioSerializer(serializers.ModelSerializer):
    idade = serializers.IntegerField(read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'tipo', 'telefone', 'data_nascimento', 'idade']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario(**validated_data)
        user.set_password(password)
        user.save()
        return user


class MedicoSerializer(serializers.ModelSerializer):
    # Campos calculados (Só leitura - buscam dados da tabela Usuario)
    nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    email = serializers.EmailField(source='usuario.email', read_only=True)
    telefone = serializers.CharField(source='usuario.telefone', read_only=True)

    class Meta:
        model = Medico
        fields = ['id', 'usuario', 'nome', 'especialidade', 'crm', 'email', 'telefone', 'disponibilidade', 'ativo']


class AgendamentoSerializer(serializers.ModelSerializer):
    nome_medico = serializers.CharField(source='medico.usuario.get_full_name', read_only=True)
    especialidade_medico = serializers.CharField(source='medico.especialidade', read_only=True)

    nome_paciente = serializers.CharField(source='paciente.get_full_name', read_only=True)
    email_paciente = serializers.CharField(source='paciente.email', read_only=True)
    telefone_paciente = serializers.CharField(source='paciente.telefone', read_only=True)
    idade_paciente = serializers.IntegerField(source='paciente.idade', read_only=True)

    class Meta:
        model = Agendamento
        fields = [
            'id', 
            'medico', 'nome_medico', 'especialidade_medico', 
            'paciente', 'nome_paciente', 'email_paciente', 'telefone_paciente', 'idade_paciente',
            'data_horario', 'status', 'criado_em'
        ]
        read_only_fields = ['paciente', 'criado_em']
