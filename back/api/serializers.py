from rest_framework import serializers
from datetime import date
from .models import Usuario, Dentista, Agendamento


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
    
    def validate_data_nascimento(self, value):
        if value and value > date.today():
            raise serializers.ValidationError("A data de nascimento não pode estar no futuro.")
        return value


class DentistaSerializer(serializers.ModelSerializer):
    # Campos calculados (Só leitura - buscam dados da tabela Usuario)
    nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    email = serializers.EmailField(source='usuario.email', read_only=True)
    telefone = serializers.CharField(source='usuario.telefone', read_only=True)

    class Meta:
        model = Dentista
        fields = ['id', 'usuario', 'nome', 'especialidade', 'cro', 'email', 'telefone', 'disponibilidade', 'ativo']


class AgendamentoSerializer(serializers.ModelSerializer):
    nome_dentista = serializers.CharField(source='dentista.usuario.get_full_name', read_only=True)
    especialidade_dentista = serializers.CharField(source='dentista.especialidade', read_only=True)
    procedimento = serializers.CharField(required=True)

    nome_paciente = serializers.CharField(source='paciente.get_full_name', read_only=True)
    email_paciente = serializers.CharField(source='paciente.email', read_only=True)
    telefone_paciente = serializers.CharField(source='paciente.telefone', read_only=True)
    idade_paciente = serializers.IntegerField(source='paciente.idade', read_only=True)

    class Meta:
        model = Agendamento
        fields = [
            'id', 
            'dentista', 'nome_dentista', 'especialidade_dentista', 
            'paciente', 'nome_paciente', 'email_paciente', 'telefone_paciente', 'idade_paciente',
            'procedimento',
            'data_horario', 'status', 'criado_em'
        ]
    
        read_only_fields = ['criado_em']
        
        extra_kwargs = {
            'paciente': {'required': False}
        }
