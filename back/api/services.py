from datetime import timedelta

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError

from .models import Agendamento


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


def calcular_duracao_minutos(procedimento_ref=None, duracao_minutos=None):
    if procedimento_ref and procedimento_ref.duracao_minutos:
        return procedimento_ref.duracao_minutos
    return duracao_minutos or 30


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


def preparar_janela_agendamento(data_horario, procedimento_ref=None, duracao_minutos=None):
    duracao = calcular_duracao_minutos(procedimento_ref, duracao_minutos)
    return duracao, calcular_data_hora_fim(data_horario, duracao)


def validar_agendamento_criacao_ou_reagendamento(
    *,
    dentista,
    data_horario,
    procedimento_ref=None,
    duracao_minutos=None,
    agendamento_atual=None,
):
    validar_data_futura(data_horario)
    validar_recursos_ativos(dentista, procedimento_ref)
    duracao, fim = preparar_janela_agendamento(data_horario, procedimento_ref, duracao_minutos)
    validar_sobreposicao(dentista, data_horario, fim, agendamento_atual)
    return duracao, fim


def cancelar_agendamento(agendamento):
    if agendamento.status in {Agendamento.STATUS_CANCELADA, Agendamento.STATUS_CONCLUIDA}:
        raise ValidationError({'status': 'Agendamento concluido ou cancelado nao pode ser cancelado.'})
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
