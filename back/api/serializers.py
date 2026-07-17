import re
from datetime import date
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from django.contrib.auth import password_validation
from django.utils import timezone
from drf_spectacular.utils import OpenApiExample, extend_schema_field, extend_schema_serializer
from rest_framework import serializers

from .models import (
    Agendamento,
    Anamnese,
    BloqueioAgendaClinica,
    Clinica,
    ConviteCadastroPaciente,
    Dentista,
    Endereco,
    EvolucaoClinica,
    HorarioFuncionamentoClinica,
    IndisponibilidadeDentista,
    ItemPlanoTratamento,
    Odontograma,
    PlanoTratamento,
    Procedimento,
    ProntuarioPaciente,
    RegistroOdontograma,
    Usuario,
)
from .services import validar_agendamento_criacao_ou_reagendamento, validar_dente


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Clinica',
            value={
                'id': 1,
                'nome': 'Clinica Sorriso',
                'slug': 'clinica-sorriso',
                'cnpj': '12.345.678/0001-99',
                'telefone': '82999999999',
                'email': 'contato@clinica.test',
                'timezone': 'America/Maceio',
                'antecedencia_minima_cancelamento_horas': 24,
                'duracao_padrao_consulta_minutos': 30,
                'ativa': True,
            },
        )
    ]
)
class ClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Clinica
        fields = [
            'id',
            'nome',
            'slug',
            'cnpj',
            'telefone',
            'email',
            'timezone',
            'antecedencia_minima_cancelamento_horas',
            'duracao_padrao_consulta_minutos',
            'ativa',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def validate_slug(self, value):
        return value.strip().lower()

    def validate_timezone(self, value):
        timezone_name = value.strip()
        try:
            ZoneInfo(timezone_name)
        except ZoneInfoNotFoundError as exc:
            raise serializers.ValidationError('Timezone invalida.') from exc
        return timezone_name

    def validate_antecedencia_minima_cancelamento_horas(self, value):
        if value < 0:
            raise serializers.ValidationError('Antecedencia minima nao pode ser negativa.')
        return value

    def validate_duracao_padrao_consulta_minutos(self, value):
        if value <= 0:
            raise serializers.ValidationError('Duracao padrao deve ser maior que zero.')
        return value


class HorarioFuncionamentoClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = HorarioFuncionamentoClinica
        fields = [
            'id',
            'clinica',
            'dia_semana',
            'horario_inicio',
            'horario_fim',
            'ativo',
            'criado_em',
            'atualizado_em',
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def validate(self, attrs):
        clinica = attrs.get('clinica') or getattr(self.instance, 'clinica', None)
        dia_semana = attrs.get('dia_semana', getattr(self.instance, 'dia_semana', None))
        horario_inicio = attrs.get('horario_inicio', getattr(self.instance, 'horario_inicio', None))
        horario_fim = attrs.get('horario_fim', getattr(self.instance, 'horario_fim', None))
        ativo = attrs.get('ativo', getattr(self.instance, 'ativo', True))

        if horario_inicio and horario_fim and horario_fim <= horario_inicio:
            raise serializers.ValidationError({'horario_fim': 'Horario fim deve ser maior que horario inicio.'})

        if clinica and dia_semana is not None and horario_inicio and horario_fim and ativo:
            sobrepostos = HorarioFuncionamentoClinica.objects.filter(
                clinica=clinica,
                dia_semana=dia_semana,
                ativo=True,
                horario_inicio__lt=horario_fim,
                horario_fim__gt=horario_inicio,
            )
            if self.instance:
                sobrepostos = sobrepostos.exclude(pk=self.instance.pk)
            if sobrepostos.exists():
                raise serializers.ValidationError({'horario_inicio': 'Intervalo se sobrepoe a outro horario ativo da clinica.'})

        return attrs


class BloqueioAgendaClinicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = BloqueioAgendaClinica
        fields = ['id', 'clinica', 'inicio', 'fim', 'motivo', 'ativo', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def validate(self, attrs):
        inicio = attrs.get('inicio', getattr(self.instance, 'inicio', None))
        fim = attrs.get('fim', getattr(self.instance, 'fim', None))

        if inicio and fim and fim <= inicio:
            raise serializers.ValidationError({'fim': 'Fim deve ser maior que inicio.'})

        return attrs


class IndisponibilidadeDentistaSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndisponibilidadeDentista
        fields = ['id', 'clinica', 'dentista', 'inicio', 'fim', 'motivo', 'ativo', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def validate(self, attrs):
        clinica = attrs.get('clinica') or getattr(self.instance, 'clinica', None)
        dentista = attrs.get('dentista') or getattr(self.instance, 'dentista', None)
        inicio = attrs.get('inicio', getattr(self.instance, 'inicio', None))
        fim = attrs.get('fim', getattr(self.instance, 'fim', None))

        if inicio and fim and fim <= inicio:
            raise serializers.ValidationError({'fim': 'Fim deve ser maior que inicio.'})
        if dentista and clinica and dentista.clinica_id != clinica.id:
            raise serializers.ValidationError({'dentista': 'Dentista pertence a outra clinica.'})

        return attrs


class EnderecoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Endereco
        fields = ['cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado']


class UsuarioBaseSerializer(serializers.ModelSerializer):
    idade = serializers.IntegerField(read_only=True)
    endereco = EnderecoSerializer(required=False, allow_null=True)

    class Meta:
        model = Usuario
        fields = [
            'id',
            'username',
            'nome_completo',
            'nome_preferido',
            'first_name',
            'last_name',
            'email',
            'cpf',
            'clinica',
            'telefone',
            'data_nascimento',
            'idade',
            'endereco',
        ]
        read_only_fields = ['id', 'username', 'idade', 'clinica']

    def validate_email(self, value):
        email = value.strip().lower()
        queryset = Usuario.objects.filter(email__iexact=email)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('Ja existe um usuario com este email.')
        return email

    def validate_cpf(self, value):
        cpf = re.sub(r'\D', '', value or '')
        if len(cpf) != 11:
            raise serializers.ValidationError('CPF deve conter 11 digitos.')
        queryset = Usuario.objects.filter(cpf=cpf)
        if self.instance:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise serializers.ValidationError('Ja existe um usuario com este CPF.')
        return cpf

    def validate_data_nascimento(self, value):
        if not value:
            raise serializers.ValidationError('A data de nascimento e obrigatoria.')
        if value > date.today():
            raise serializers.ValidationError('A data de nascimento nao pode estar no futuro.')
        return value

    def _save_endereco(self, usuario, endereco_data):
        if endereco_data is serializers.empty:
            return
        if endereco_data is None:
            Endereco.objects.filter(usuario=usuario).delete()
            return
        Endereco.objects.update_or_create(usuario=usuario, defaults=endereco_data)

    def update(self, instance, validated_data):
        endereco_data = validated_data.pop('endereco', serializers.empty)
        instance = super().update(instance, validated_data)
        self._save_endereco(instance, endereco_data)
        return instance


class RegistroUsuarioSerializer(UsuarioBaseSerializer):
    """Serializer do cadastro publico: cria exclusivamente pacientes."""
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    class Meta(UsuarioBaseSerializer.Meta):
        fields = UsuarioBaseSerializer.Meta.fields + ['password']
        read_only_fields = ['id', 'idade', 'clinica']
        extra_kwargs = {
            'nome_completo': {'required': False, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'cpf': {'required': True, 'allow_blank': False},
            'telefone': {'required': True, 'allow_blank': False},
            'data_nascimento': {'required': True},
        }

    def validate(self, attrs):
        nome_completo = attrs.get('nome_completo')
        if not nome_completo:
            nome_compat = f"{attrs.get('first_name', '')} {attrs.get('last_name', '')}".strip()
            attrs['nome_completo'] = nome_compat or attrs.get('username', '')
        return attrs

    def validate_password(self, value):
        password_validation.validate_password(value)
        return value

    def create(self, validated_data):
        endereco_data = validated_data.pop('endereco', serializers.empty)
        password = validated_data.pop('password')
        user = Usuario(tipo='PACIENTE', **validated_data)
        user.set_password(password)
        user.save()
        self._save_endereco(user, endereco_data)
        return user


class CadastroViaConviteSerializer(RegistroUsuarioSerializer):
    """Cadastro publico de paciente consumindo um convite valido."""


class ConviteCadastroPacienteSerializer(serializers.ModelSerializer):
    pode_ser_consumido = serializers.SerializerMethodField()

    class Meta:
        model = ConviteCadastroPaciente
        fields = [
            'id',
            'clinica',
            'telefone_destino',
            'email_destino',
            'nome_destino',
            'expira_em',
            'usado_em',
            'ativo',
            'criado_por',
            'criado_em',
            'atualizado_em',
            'pode_ser_consumido',
        ]
        read_only_fields = [
            'id',
            'usado_em',
            'criado_por',
            'criado_em',
            'atualizado_em',
            'pode_ser_consumido',
        ]

    @extend_schema_field(serializers.BooleanField)
    def get_pode_ser_consumido(self, convite):
        return convite.ativo and convite.usado_em is None and convite.expira_em > timezone.now() and convite.clinica.ativa

    def validate(self, attrs):
        clinica = attrs.get('clinica') or getattr(self.instance, 'clinica', None)
        expira_em = attrs.get('expira_em') or getattr(self.instance, 'expira_em', None)

        if self.instance is None:
            if clinica and not clinica.ativa:
                raise serializers.ValidationError({'clinica': 'Clinica inativa nao permite gerar convites.'})
            if expira_em and expira_em <= timezone.now():
                raise serializers.ValidationError({'expira_em': 'A expiracao deve estar no futuro.'})

        return attrs


class PerfilUsuarioSerializer(UsuarioBaseSerializer):
    """Dados que um usuario pode consultar e atualizar no proprio perfil."""

    class Meta(UsuarioBaseSerializer.Meta):
        read_only_fields = UsuarioBaseSerializer.Meta.read_only_fields + ['cpf']
        extra_kwargs = {
            'nome_completo': {'required': True, 'allow_blank': False},
            'email': {'required': True, 'allow_blank': False},
            'telefone': {'required': True, 'allow_blank': False},
            'data_nascimento': {'required': True},
        }


class UsuarioAdminSerializer(PerfilUsuarioSerializer):
    """Gestao de usuarios restrita a administradores Django (is_staff)."""

    class Meta(PerfilUsuarioSerializer.Meta):
        fields = PerfilUsuarioSerializer.Meta.fields + ['tipo', 'is_active']
        read_only_fields = ['id', 'username', 'idade']


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


class ReagendarAgendamentoSerializer(serializers.Serializer):
    data_horario = serializers.DateTimeField()


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Dentista',
            value={'id': 1, 'clinica': 1, 'usuario': 3, 'nome': 'Dra. Ana Silva', 'especialidade': 'Ortodontia', 'cro': '12345-AL', 'ativo': True},
        )
    ]
)
class DentistaSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='usuario.get_full_name', read_only=True)
    email = serializers.EmailField(source='usuario.email', read_only=True)
    telefone = serializers.CharField(source='usuario.telefone', read_only=True)

    class Meta:
        model = Dentista
        fields = ['id', 'clinica', 'usuario', 'nome', 'especialidade', 'cro', 'email', 'telefone', 'disponibilidade', 'ativo']

    def validate_cro(self, value):
        cro = value.strip().upper()
        if not re.match(r'^\d{4,6}-[A-Z]{2}$', cro):
            raise serializers.ValidationError('CRO deve estar no formato 12345-UF.')
        return cro

    def validate(self, attrs):
        if 'crm' in self.initial_data:
            raise serializers.ValidationError({'crm': 'Use o campo odontologico cro.'})
        usuario = attrs.get('usuario') or getattr(self.instance, 'usuario', None)
        clinica = attrs.get('clinica') or getattr(self.instance, 'clinica', None)
        if usuario and not clinica and usuario.clinica_id:
            attrs['clinica'] = usuario.clinica
            clinica = usuario.clinica
        if usuario and clinica and usuario.clinica_id and usuario.clinica_id != clinica.id:
            raise serializers.ValidationError({'usuario': 'O usuario dentista pertence a outra clinica.'})
        if not clinica:
            raise serializers.ValidationError({'clinica': 'A clinica e obrigatoria para o dentista.'})
        return attrs


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Procedimento',
            value={'id': 1, 'clinica': 1, 'nome': 'Limpeza', 'descricao': 'Profilaxia odontologica', 'duracao_minutos': 30, 'ativo': True},
        )
    ]
)
class ProcedimentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Procedimento
        fields = ['id', 'clinica', 'nome', 'descricao', 'duracao_minutos', 'ativo', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'criado_em', 'atualizado_em']


@extend_schema_serializer(
    examples=[
        OpenApiExample(
            'Agendamento',
            value={'id': 1, 'clinica': 1, 'dentista': 2, 'nome_dentista': 'Dra. Ana Silva', 'procedimento': 'Limpeza', 'data_horario': '2030-01-13T10:00:00Z', 'status': 'AGENDADA'},
        )
    ]
)
class AgendamentoSerializer(serializers.ModelSerializer):
    dentista = serializers.PrimaryKeyRelatedField(queryset=Dentista.objects.all(), required=False)
    nome_dentista = serializers.CharField(source='dentista.usuario.get_full_name', read_only=True)
    especialidade_dentista = serializers.CharField(source='dentista.especialidade', read_only=True)
    procedimento = serializers.CharField(required=False, allow_blank=False)
    nome_paciente = serializers.CharField(source='paciente.get_full_name', read_only=True)
    email_paciente = serializers.EmailField(source='paciente.email', read_only=True)
    telefone_paciente = serializers.CharField(source='paciente.telefone', read_only=True)
    idade_paciente = serializers.IntegerField(source='paciente.idade', read_only=True)

    class Meta:
        model = Agendamento
        fields = ['id', 'clinica', 'dentista', 'nome_dentista', 'especialidade_dentista', 'paciente', 'nome_paciente', 'email_paciente', 'telefone_paciente', 'idade_paciente', 'procedimento', 'procedimento_ref', 'data_horario', 'data_hora_fim', 'duracao_minutos', 'status', 'criado_em']
        read_only_fields = ['criado_em', 'data_hora_fim']
        extra_kwargs = {'paciente': {'required': False}, 'clinica': {'required': False}, 'dentista': {'required': False}}
        validators = []

    def validate(self, attrs):
        campos_legados = {'medico', 'nome_medico', 'crm'} & set(self.initial_data)
        if campos_legados:
            erros = {campo: 'Use o contrato odontologico oficial.' for campo in campos_legados}
            raise serializers.ValidationError(erros)

        request = self.context.get('request')
        usuario = getattr(request, 'user', None)

        dentista = attrs.get('dentista') or getattr(self.instance, 'dentista', None)
        paciente = attrs.get('paciente') or getattr(self.instance, 'paciente', None)
        procedimento_ref = attrs.get('procedimento_ref') or getattr(self.instance, 'procedimento_ref', None)
        clinica = attrs.get('clinica') or getattr(self.instance, 'clinica', None)
        data_horario = attrs.get('data_horario') or getattr(self.instance, 'data_horario', None)
        duracao_minutos = attrs.get('duracao_minutos') or getattr(self.instance, 'duracao_minutos', None)
        status_agendamento = attrs.get('status')

        if usuario and usuario.is_authenticated and not usuario.is_staff:
            if not usuario.clinica_id:
                raise serializers.ValidationError({'clinica': 'Usuario sem clinica vinculada.'})
            if status_agendamento and status_agendamento != Agendamento.STATUS_AGENDADA:
                raise serializers.ValidationError({'status': 'Usuario comum nao pode definir status do agendamento.'})
            clinica = usuario.clinica
            attrs['clinica'] = clinica
            paciente = usuario

        if not clinica:
            for recurso in (dentista, paciente, procedimento_ref):
                if recurso and getattr(recurso, 'clinica_id', None):
                    clinica = recurso.clinica
                    attrs['clinica'] = clinica
                    break

        if not clinica:
            raise serializers.ValidationError({'clinica': 'A clinica e obrigatoria para o agendamento.'})

        if not dentista:
            raise serializers.ValidationError({'dentista': 'Informe o dentista.'})
        if dentista and dentista.clinica_id != clinica.id:
            raise serializers.ValidationError({'dentista': 'Dentista pertence a outra clinica.'})
        if paciente and paciente.clinica_id and paciente.clinica_id != clinica.id:
            raise serializers.ValidationError({'paciente': 'Paciente pertence a outra clinica.'})
        if procedimento_ref and procedimento_ref.clinica_id != clinica.id:
            raise serializers.ValidationError({'procedimento_ref': 'Procedimento pertence a outra clinica.'})

        if procedimento_ref and not attrs.get('procedimento'):
            attrs['procedimento'] = procedimento_ref.nome
        if not attrs.get('procedimento') and not getattr(self.instance, 'procedimento', None):
            raise serializers.ValidationError({'procedimento': 'Informe o procedimento.'})

        if data_horario:
            duracao, fim = validar_agendamento_criacao_ou_reagendamento(
                clinica=clinica,
                dentista=dentista,
                data_horario=data_horario,
                procedimento_ref=procedimento_ref,
                duracao_minutos=duracao_minutos,
                agendamento_atual=self.instance,
            )
            attrs['duracao_minutos'] = duracao
            attrs['data_hora_fim'] = fim

        return attrs


class ProntuarioPacienteSerializer(serializers.ModelSerializer):
    nome_paciente = serializers.CharField(source='paciente.get_full_name', read_only=True)

    class Meta:
        model = ProntuarioPaciente
        fields = [
            'id', 'clinica', 'paciente', 'nome_paciente', 'criado_em', 'atualizado_em',
            'criado_por', 'atualizado_por', 'ativo',
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em', 'criado_por', 'atualizado_por']

    def validate(self, attrs):
        clinica = attrs.get('clinica') or getattr(self.instance, 'clinica', None)
        paciente = attrs.get('paciente') or getattr(self.instance, 'paciente', None)
        if not paciente:
            raise serializers.ValidationError({'paciente': 'Informe o paciente.'})
        if not clinica:
            raise serializers.ValidationError({'clinica': 'Informe a clinica.'})
        if paciente.clinica_id != clinica.id:
            raise serializers.ValidationError({'paciente': 'Paciente pertence a outra clinica.'})
        return attrs


class AnamneseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Anamnese
        fields = [
            'id', 'prontuario', 'alergias', 'medicamentos_em_uso', 'condicoes_medicas',
            'cirurgias_anteriores', 'historico_familiar', 'gestante', 'fumante',
            'consumo_alcool', 'observacoes', 'preenchida_em', 'preenchida_por',
            'atualizada_em', 'atualizada_por',
        ]
        read_only_fields = [
            'id', 'prontuario', 'preenchida_em', 'preenchida_por', 'atualizada_em', 'atualizada_por',
        ]


class EvolucaoClinicaSerializer(serializers.ModelSerializer):
    nome_dentista = serializers.CharField(source='dentista.usuario.get_full_name', read_only=True)

    class Meta:
        model = EvolucaoClinica
        fields = [
            'id', 'prontuario', 'agendamento', 'dentista', 'nome_dentista', 'descricao',
            'criado_em', 'atualizado_em', 'criado_por',
        ]
        read_only_fields = ['id', 'criado_em', 'atualizado_em', 'criado_por']
        extra_kwargs = {'dentista': {'required': False}}

    def validate_descricao(self, value):
        if not value.strip():
            raise serializers.ValidationError('Descricao e obrigatoria.')
        return value.strip()


class OdontogramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Odontograma
        fields = ['id', 'clinica', 'prontuario', 'criado_em', 'atualizado_em', 'criado_por', 'atualizado_por', 'ativo']
        read_only_fields = ['id', 'clinica', 'criado_em', 'atualizado_em', 'criado_por', 'atualizado_por']


class RegistroOdontogramaSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegistroOdontograma
        fields = ['id', 'odontograma', 'numero_dente', 'face', 'condicao', 'observacao', 'dentista', 'criado_por', 'criado_em', 'atualizado_em', 'ativo']
        read_only_fields = ['id', 'dentista', 'criado_por', 'criado_em', 'atualizado_em']

    def validate_numero_dente(self, value):
        validar_dente(value)
        return value


class PlanoTratamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlanoTratamento
        fields = ['id', 'clinica', 'prontuario', 'titulo', 'descricao', 'status', 'criado_por', 'aprovado_em', 'concluido_em', 'criado_em', 'atualizado_em', 'ativo']
        read_only_fields = ['id', 'clinica', 'status', 'criado_por', 'aprovado_em', 'concluido_em', 'criado_em', 'atualizado_em']


class ItemPlanoTratamentoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemPlanoTratamento
        fields = ['id', 'plano', 'procedimento_ref', 'descricao', 'numero_dente', 'face', 'prioridade', 'status', 'quantidade', 'valor_estimado', 'ordem', 'criado_em', 'atualizado_em']
        read_only_fields = ['id', 'criado_em', 'atualizado_em']

    def validate_numero_dente(self, value):
        if value is not None:
            validar_dente(value)
        return value

    def validate_quantidade(self, value):
        if value <= 0:
            raise serializers.ValidationError('Quantidade deve ser maior que zero.')
        return value

    def validate_valor_estimado(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError('Valor estimado nao pode ser negativo.')
        return value
