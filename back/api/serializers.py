from datetime import date

from django.contrib.auth import password_validation
from rest_framework import serializers

from .models import Agendamento, Dentista, Usuario


class RegistroUsuarioSerializer(serializers.ModelSerializer):
    """Serializer do cadastro publico: cria exclusivamente pacientes."""
    idade = serializers.IntegerField(read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password', 'telefone', 'data_nascimento', 'idade']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = Usuario(tipo='PACIENTE', **validated_data)
        user.set_password(password)
        user.save()
        return user

    def validate_data_nascimento(self, value):
        if value and value > date.today():
            raise serializers.ValidationError('A data de nascimento nao pode estar no futuro.')
        return value


class PerfilUsuarioSerializer(serializers.ModelSerializer):
    """Dados que um usuario pode consultar e atualizar no proprio perfil."""
    idade = serializers.IntegerField(read_only=True)

    class Meta:
        model = Usuario
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'telefone', 'data_nascimento', 'idade']
        read_only_fields = ['id', 'username', 'idade']

    def validate_data_nascimento(self, value):
        if value and value > date.today():
            raise serializers.ValidationError('A data de nascimento nao pode estar no futuro.')
        return value


class UsuarioAdminSerializer(PerfilUsuarioSerializer):
    """Gestao de usuarios restrita a administradores Django (is_staff)."""

    class Meta(PerfilUsuarioSerializer.Meta):
        fields = PerfilUsuarioSerializer.Meta.fields + ['tipo', 'is_active']


class AlterarSenhaSerializer(serializers.Serializer):
    senha_atual = serializers.CharField(write_only=True, trim_whitespace=False)
    nova_senha = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate_senha_atual(self, value):
        if not self.context['request'].user.check_password(value):
            raise serializers.ValidationError('A senha atual esta incorreta.')
        return value

    def validate_nova_senha(self, value):
        password_validation.validate_password(value, self.context['request'].user)
        return value


class DentistaSerializer(serializers.ModelSerializer):
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
    email_paciente = serializers.EmailField(source='paciente.email', read_only=True)
    telefone_paciente = serializers.CharField(source='paciente.telefone', read_only=True)
    idade_paciente = serializers.IntegerField(source='paciente.idade', read_only=True)

    class Meta:
        model = Agendamento
        fields = ['id', 'dentista', 'nome_dentista', 'especialidade_dentista', 'paciente', 'nome_paciente', 'email_paciente', 'telefone_paciente', 'idade_paciente', 'procedimento', 'data_horario', 'status', 'criado_em']
        read_only_fields = ['criado_em']
        extra_kwargs = {'paciente': {'required': False}}
