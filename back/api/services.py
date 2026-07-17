from datetime import timedelta
from zoneinfo import ZoneInfo

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError

from .models import Agendamento, BloqueioAgendaClinica, HorarioFuncionamentoClinica, IndisponibilidadeDentista


class ConflitoAgenda(APIException):
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'Horario indisponivel para este dentista.'
    default_code = 'conflito_agenda'


STATUS_BLOQUEIAM_HORARIO = {
    Agendamento.STATUS_AGENDADA,
    Agendamento.STATUS_CONFIRMADA,
    Agendamento.STATUS_EM_ATENDIMENTO,
    Agendamento.STATUS_CONCLUIDA,
}

STATUS_FINAIS = {
    Agendamento.STATUS_CANCELADA,
    Agendamento.STATUS_CONCLUIDA,
    Agendamento.STATUS_NAO_COMPARECEU,
}


def calcular_duracao_minutos(clinica=None, procedimento_ref=None, duracao_minutos=None):
    if procedimento_ref and procedimento_ref.duracao_minutos:
        return procedimento_ref.duracao_minutos
    if duracao_minutos:
        return duracao_minutos
    if clinica and clinica.duracao_padrao_consulta_minutos:
        return clinica.duracao_padrao_consulta_minutos
    return 30


def calcular_data_hora_fim(data_horario, duracao_minutos):
    return data_horario + timedelta(minutes=duracao_minutos)


def validar_data_futura(data_horario):
    if not data_horario:
        raise ValidationError({'data_horario': 'Informe a data e hora do agendamento.'})
    if data_horario <= timezone.now():
        raise ValidationError({'data_horario': 'Agendamento nao pode ser criado ou reagendado no passado.'})


def validar_recursos_ativos(dentista, procedimento_ref=None):
    if dentista and not dentista.ativo:
        raise ValidationError({'dentista': 'Dentista inativo nao pode receber agendamentos.'})
    if procedimento_ref and not procedimento_ref.ativo:
        raise ValidationError({'procedimento_ref': 'Procedimento inativo nao pode ser usado em agendamentos.'})


def validar_sobreposicao(dentista, inicio, fim, agendamento_atual=None):
    conflitos = (
        Agendamento.objects.select_for_update()
        .filter(dentista=dentista, status__in=STATUS_BLOQUEIAM_HORARIO)
        .order_by('data_horario')
    )
    if agendamento_atual:
        conflitos = conflitos.exclude(pk=agendamento_atual.pk)

    for agendamento in conflitos:
        fim_existente = agendamento.data_hora_fim or calcular_data_hora_fim(
            agendamento.data_horario,
            agendamento.duracao_minutos,
        )
        if agendamento.data_horario < fim and fim_existente > inicio:
            raise ConflitoAgenda('Horario se sobrepoe a outro agendamento deste dentista.')


def preparar_janela_agendamento(data_horario, clinica=None, procedimento_ref=None, duracao_minutos=None):
    duracao = calcular_duracao_minutos(clinica, procedimento_ref, duracao_minutos)
    return duracao, calcular_data_hora_fim(data_horario, duracao)


def validar_horario_funcionamento(clinica, inicio, fim):
    if not clinica:
        raise ValidationError({'clinica': 'A clinica e obrigatoria para validar o horario de funcionamento.'})

    timezone_clinica = ZoneInfo(clinica.timezone)
    inicio_local = timezone.localtime(inicio, timezone_clinica)
    fim_local = timezone.localtime(fim, timezone_clinica)

    if inicio_local.date() != fim_local.date():
        raise ValidationError({'data_horario': 'Agendamento deve iniciar e terminar no mesmo dia local da clinica.'})

    horarios = HorarioFuncionamentoClinica.objects.filter(
        clinica=clinica,
        dia_semana=inicio_local.weekday(),
        ativo=True,
    )

    if not horarios.exists():
        raise ValidationError({'data_horario': 'Clinica nao possui expediente ativo neste dia.'})

    inicio_hora = inicio_local.time()
    fim_hora = fim_local.time()
    for horario in horarios:
        if horario.horario_inicio <= inicio_hora and fim_hora <= horario.horario_fim:
            return

    raise ValidationError({'data_horario': 'Agendamento fora do horario de funcionamento da clinica.'})


def validar_bloqueios_e_indisponibilidades(clinica, dentista, inicio, fim):
    bloqueio = BloqueioAgendaClinica.objects.filter(
        clinica=clinica,
        ativo=True,
        inicio__lt=fim,
        fim__gt=inicio,
    ).exists()
    if bloqueio:
        raise ConflitoAgenda('Horario bloqueado para esta clinica.')

    indisponibilidade = IndisponibilidadeDentista.objects.filter(
        clinica=clinica,
        dentista=dentista,
        ativo=True,
        inicio__lt=fim,
        fim__gt=inicio,
    ).exists()
    if indisponibilidade:
        raise ConflitoAgenda('Dentista indisponivel neste horario.')


def validar_agendamento_criacao_ou_reagendamento(
    *,
    clinica,
    dentista,
    data_horario,
    procedimento_ref=None,
    duracao_minutos=None,
    agendamento_atual=None,
):
    validar_data_futura(data_horario)
    validar_recursos_ativos(dentista, procedimento_ref)
    duracao, fim = preparar_janela_agendamento(data_horario, clinica, procedimento_ref, duracao_minutos)
    validar_horario_funcionamento(clinica, data_horario, fim)
    validar_bloqueios_e_indisponibilidades(clinica, dentista, data_horario, fim)
    validar_sobreposicao(dentista, data_horario, fim, agendamento_atual)
    return duracao, fim


def cancelar_agendamento(agendamento, usuario=None):
    if agendamento.status in {Agendamento.STATUS_CANCELADA, Agendamento.STATUS_CONCLUIDA}:
        raise ValidationError({'status': 'Agendamento concluido ou cancelado nao pode ser cancelado.'})
    if usuario and not usuario.is_staff and usuario.tipo == 'PACIENTE':
        antecedencia = agendamento.clinica.antecedencia_minima_cancelamento_horas
        limite_cancelamento = timezone.now() + timedelta(hours=antecedencia)
        if agendamento.data_horario < limite_cancelamento:
            raise ValidationError({'data_horario': 'Cancelamento fora da antecedencia minima da clinica.'})
    agendamento.status = Agendamento.STATUS_CANCELADA
    agendamento.save(update_fields=['status'])
    return agendamento


def confirmar_agendamento(agendamento):
    if agendamento.status in STATUS_FINAIS:
        raise ValidationError({'status': 'Agendamento finalizado nao pode ser confirmado.'})
    agendamento.status = Agendamento.STATUS_CONFIRMADA
    agendamento.save(update_fields=['status'])
    return agendamento


def concluir_agendamento(agendamento):
    if agendamento.status == Agendamento.STATUS_CANCELADA:
        raise ValidationError({'status': 'Agendamento cancelado nao pode ser concluido.'})
    if agendamento.status == Agendamento.STATUS_CONCLUIDA:
        raise ValidationError({'status': 'Agendamento ja esta concluido.'})
    agendamento.status = Agendamento.STATUS_CONCLUIDA
    agendamento.save(update_fields=['status'])
    return agendamento


def marcar_falta_agendamento(agendamento):
    if agendamento.status in {Agendamento.STATUS_CANCELADA, Agendamento.STATUS_CONCLUIDA}:
        raise ValidationError({'status': 'Agendamento cancelado ou concluido nao pode ser marcado como falta.'})
    agendamento.status = Agendamento.STATUS_NAO_COMPARECEU
    agendamento.save(update_fields=['status'])
    return agendamento


def reagendar_agendamento(agendamento, nova_data_horario):
    if agendamento.status in {Agendamento.STATUS_CANCELADA, Agendamento.STATUS_CONCLUIDA}:
        raise ValidationError({'status': 'Agendamento cancelado ou concluido nao pode ser reagendado.'})
    with transaction.atomic():
        duracao, fim = validar_agendamento_criacao_ou_reagendamento(
            clinica=agendamento.clinica,
            dentista=agendamento.dentista,
            data_horario=nova_data_horario,
            procedimento_ref=agendamento.procedimento_ref,
            duracao_minutos=agendamento.duracao_minutos,
            agendamento_atual=agendamento,
        )
        agendamento.data_horario = nova_data_horario
        agendamento.duracao_minutos = duracao
        agendamento.data_hora_fim = fim
        agendamento.save(update_fields=['data_horario', 'duracao_minutos', 'data_hora_fim'])
    return agendamento


def validar_criacao_evolucao(*, prontuario, agendamento, dentista):
    """Protege os vinculos que formam o registro clinico historico."""
    if prontuario.clinica_id != agendamento.clinica_id:
        raise ValidationError({'agendamento': 'Agendamento pertence a outra clinica.'})
    if dentista.clinica_id != prontuario.clinica_id:
        raise ValidationError({'dentista': 'Dentista pertence a outra clinica.'})
    if agendamento.dentista_id != dentista.id:
        raise ValidationError({'dentista': 'Dentista deve ser o vinculado ao atendimento.'})
    if agendamento.paciente_id != prontuario.paciente_id:
        raise ValidationError({'agendamento': 'Agendamento pertence a outro paciente.'})
    if agendamento.status not in {Agendamento.STATUS_EM_ATENDIMENTO, Agendamento.STATUS_CONCLUIDA}:
        raise ValidationError(
            {'agendamento': 'Evolucao clinica so pode ser registrada em atendimento ou consulta concluida.'}
        )


NUMEROS_DENTES_FDI = set(range(11, 19)) | set(range(21, 29)) | set(range(31, 39)) | set(range(41, 49))
TRANSICOES_PLANO = {
    'RASCUNHO': {'PROPOSTO'}, 'PROPOSTO': {'APROVADO', 'CANCELADO'},
    'APROVADO': {'EM_ANDAMENTO', 'CANCELADO'}, 'EM_ANDAMENTO': {'CONCLUIDO', 'CANCELADO'},
}


def validar_dente(numero_dente):
    if numero_dente not in NUMEROS_DENTES_FDI:
        raise ValidationError({'numero_dente': 'Numero de dente deve usar a numeracao FDI permanente valida.'})


def validar_contexto_odontologico(*, prontuario, clinica, dentista=None):
    if prontuario.clinica_id != clinica.id:
        raise ValidationError({'prontuario': 'Prontuario pertence a outra clinica.'})
    if dentista and dentista.clinica_id != clinica.id:
        raise ValidationError({'dentista': 'Dentista pertence a outra clinica.'})


def transicionar_plano(plano, novo_status):
    if novo_status not in TRANSICOES_PLANO.get(plano.status, set()):
        raise ValidationError({'status': f'Transicao de {plano.status} para {novo_status} nao permitida.'})
    plano.status = novo_status
    agora = timezone.now()
    if novo_status == 'APROVADO':
        plano.aprovado_em = agora
    if novo_status == 'CONCLUIDO':
        plano.concluido_em = agora
    plano.save()
    return plano
