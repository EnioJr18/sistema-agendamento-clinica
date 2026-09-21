"""Database-backed selectors for dashboard and administrative reports."""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from django.db.models import Avg, Count, DecimalField, Q, Sum, Value
from django.db.models.functions import Coalesce, TruncDay, TruncMonth
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework.exceptions import NotFound, PermissionDenied, ValidationError

from .models import Agendamento, Dentista, Orcamento, Pagamento, PlanoTratamento, Procedimento, Usuario

ZERO = Decimal('0.00')
PERIODOS = {'7d': 7, '30d': 30, '90d': 90, '12m': 365}


@dataclass(frozen=True)
class EscopoRelatorio:
    clinica_id: int | None
    timezone: ZoneInfo


@dataclass(frozen=True)
class FiltroPeriodo:
    inicio: date
    fim: date
    inicio_dt: datetime
    fim_dt_exclusivo: datetime
    granularidade: str


def escopo_para_usuario(usuario):
    if usuario.is_staff:
        return EscopoRelatorio(None, ZoneInfo('UTC'))
    if usuario.tipo == 'PACIENTE':
        raise PermissionDenied('Paciente nao acessa indicadores administrativos.')
    if usuario.tipo != 'DENTISTA' or not usuario.clinica_id:
        raise PermissionDenied('Usuario sem permissao para relatorios.')
    return EscopoRelatorio(usuario.clinica_id, ZoneInfo(usuario.clinica.timezone))


def filtro_periodo(params, timezone_clinica):
    periodo = params.get('periodo')
    inicio_raw, fim_raw = params.get('data_inicial'), params.get('data_final')
    if periodo and (inicio_raw or fim_raw):
        raise ValidationError({'periodo': 'Use periodo ou datas personalizadas, nao ambos.'})
    if bool(inicio_raw) != bool(fim_raw):
        raise ValidationError({'data_inicial': 'Informe data_inicial e data_final juntas.'})
    hoje = timezone.localtime(timezone.now(), timezone_clinica).date()
    if inicio_raw:
        inicio, fim = parse_date(inicio_raw), parse_date(fim_raw)
        if not inicio or not fim:
            raise ValidationError({'data_inicial': 'Datas devem usar o formato YYYY-MM-DD.'})
        if inicio > fim:
            raise ValidationError({'data_inicial': 'data_inicial deve ser anterior ou igual a data_final.'})
        if (fim - inicio).days > 366:
            raise ValidationError({'data_final': 'Intervalo maximo para relatorios e de 366 dias.'})
    else:
        if periodo is None:
            periodo = '30d'
        if periodo not in PERIODOS:
            raise ValidationError({'periodo': 'Periodo deve ser 7d, 30d, 90d ou 12m.'})
        fim, inicio = hoje, hoje - timedelta(days=PERIODOS[periodo] - 1)
    inicio_dt = timezone.make_aware(datetime.combine(inicio, time.min), timezone_clinica)
    fim_dt = timezone.make_aware(datetime.combine(fim + timedelta(days=1), time.min), timezone_clinica)
    granularidade = 'mes' if (fim - inicio).days >= 90 else 'dia'
    return FiltroPeriodo(inicio, fim, inicio_dt, fim_dt, granularidade)


def _periodo_qs(queryset, campo, filtro):
    return queryset.filter(**{f'{campo}__gte': filtro.inicio_dt, f'{campo}__lt': filtro.fim_dt_exclusivo})


def _escopo_qs(queryset, escopo):
    return queryset if escopo.clinica_id is None else queryset.filter(clinica_id=escopo.clinica_id)


def _valor(expressao):
    return Coalesce(expressao, Value(ZERO), output_field=DecimalField(max_digits=14, decimal_places=2))


def _percentual(parte, total):
    return Decimal('0.00') if not total else (Decimal(parte) * Decimal('100') / Decimal(total)).quantize(Decimal('0.01'))


def _serie(queryset, campo, filtro, tz):
    trunc = TruncMonth(campo, tzinfo=tz) if filtro.granularidade == 'mes' else TruncDay(campo, tzinfo=tz)
    por_periodo = {item['periodo'].date(): item['quantidade'] for item in queryset.annotate(periodo=trunc).values('periodo').annotate(quantidade=Count('id'))}
    atual = filtro.inicio.replace(day=1) if filtro.granularidade == 'mes' else filtro.inicio
    limite = filtro.fim.replace(day=1) if filtro.granularidade == 'mes' else filtro.fim
    saida = []
    while atual <= limite:
        saida.append({'periodo': atual.isoformat(), 'quantidade': por_periodo.get(atual, 0)})
        if filtro.granularidade == 'mes':
            atual = (atual.replace(day=28) + timedelta(days=4)).replace(day=1)
        else:
            atual += timedelta(days=1)
    return saida


def _filtros_agendamento(queryset, params, escopo):
    for nome, model, campo in [('dentista', Dentista, 'dentista_id'), ('procedimento', Procedimento, 'procedimento_ref_id'), ('paciente', Usuario, 'paciente_id')]:
        valor = params.get(nome)
        if valor is None:
            continue
        try:
            objeto = model.objects.get(pk=valor)
        except (ValueError, model.DoesNotExist) as exc:
            raise NotFound(f'{nome.title()} nao encontrado.') from exc
        if escopo.clinica_id and getattr(objeto, 'clinica_id', None) != escopo.clinica_id:
            raise NotFound(f'{nome.title()} nao encontrado.')
        queryset = queryset.filter(**{campo: objeto.pk})
    status = params.get('status')
    if status:
        if status not in dict(Agendamento.STATUS_CHOICES):
            raise ValidationError({'status': 'Status de agendamento invalido.'})
        queryset = queryset.filter(status=status)
    return queryset


def dashboard_resumo(escopo, filtro):
    agenda = _periodo_qs(_escopo_qs(Agendamento.objects.all(), escopo), 'data_horario', filtro)
    agenda_agg = agenda.aggregate(
        total=Count('id'),
        agendadas=Count('id', filter=Q(status='AGENDADA')),
        confirmadas=Count('id', filter=Q(status='CONFIRMADA')),
        em_atendimento=Count('id', filter=Q(status='EM_ATENDIMENTO')),
        concluidas=Count('id', filter=Q(status='CONCLUIDA')),
        canceladas=Count('id', filter=Q(status='CANCELADA')),
        faltas=Count('id', filter=Q(status='NAO_COMPARECEU')),
    )
    pacientes = _escopo_qs(Usuario.objects.filter(tipo='PACIENTE'), escopo)
    orcamentos = _periodo_qs(_escopo_qs(Orcamento.objects.filter(ativo=True), escopo), 'criado_em', filtro)
    pagamentos = _periodo_qs(_escopo_qs(Pagamento.objects.filter(ativo=True), escopo), 'pago_em', filtro)
    planos = _periodo_qs(_escopo_qs(PlanoTratamento.objects.filter(ativo=True), escopo), 'criado_em', filtro)
    total = agenda_agg['total']
    return {
        'periodo': {'data_inicial': filtro.inicio, 'data_final': filtro.fim, 'granularidade': filtro.granularidade},
        'agendamentos': {
            'total_agendamentos': total, 'agendadas': agenda_agg['agendadas'], 'confirmadas': agenda_agg['confirmadas'],
            'em_atendimento': agenda_agg['em_atendimento'], 'concluidas': agenda_agg['concluidas'],
            'canceladas': agenda_agg['canceladas'], 'nao_compareceu': agenda_agg['faltas'],
            'taxa_cancelamento': _percentual(agenda_agg['canceladas'], total),
            'taxa_nao_comparecimento': _percentual(agenda_agg['faltas'], total),
            'taxa_conclusao': _percentual(agenda_agg['concluidas'], total),
        },
        'pacientes': {'total_pacientes': pacientes.count(), 'novos_pacientes_no_periodo': _periodo_qs(pacientes, 'date_joined', filtro).count()},
        'financeiro': {
            'total_orcado_aprovado': orcamentos.filter(status='APROVADO').aggregate(v=_valor(Sum('total')))['v'],
            'total_recebido': pagamentos.aggregate(v=_valor(Sum('valor')))['v'],
            'total_em_aberto': orcamentos.filter(status='APROVADO').aggregate(v=_valor(Sum('saldo')))['v'],
            'total_vencido': orcamentos.filter(status='VENCIDO').aggregate(v=_valor(Sum('saldo')))['v'],
            'quantidade_pagamentos': pagamentos.count(),
        },
        'tratamento': {
            'quantidade_planos': planos.count(), 'planos_aprovados': planos.filter(status='APROVADO').count(),
            'planos_em_andamento': planos.filter(status='EM_ANDAMENTO').count(), 'planos_concluidos': planos.filter(status='CONCLUIDO').count(),
        },
        'evolucao': {
            'agendamentos': _serie(agenda, 'data_horario', filtro, escopo.timezone),
            'recebimentos': _serie(pagamentos, 'pago_em', filtro, escopo.timezone),
            'novos_pacientes': _serie(_periodo_qs(pacientes, 'date_joined', filtro), 'date_joined', filtro, escopo.timezone),
        },
    }


def relatorio_agendamentos(escopo, filtro, params):
    agenda = _filtros_agendamento(_periodo_qs(_escopo_qs(Agendamento.objects.select_related('dentista__usuario', 'procedimento_ref'), escopo), 'data_horario', filtro), params, escopo)
    return {
        'total': agenda.count(),
        'por_status': list(agenda.values('status').annotate(quantidade=Count('id')).order_by('status')),
        'por_dentista': list(agenda.values('dentista_id', 'dentista__usuario__nome_completo').annotate(quantidade=Count('id'), tempo_total_minutos=Sum('duracao_minutos')).order_by('dentista__usuario__nome_completo')),
        'por_procedimento': list(agenda.values('procedimento').annotate(quantidade=Count('id')).order_by('procedimento')),
        'por_periodo': _serie(agenda, 'data_horario', filtro, escopo.timezone),
        'cancelamentos': agenda.filter(status='CANCELADA').count(), 'faltas': agenda.filter(status='NAO_COMPARECEU').count(), 'concluidas': agenda.filter(status='CONCLUIDA').count(),
    }


def relatorio_financeiro(escopo, filtro, params):
    if params.get('dentista'):
        raise ValidationError({'dentista': 'A modelagem financeira atual nao vincula orcamento a dentista.'})
    orcamentos = _periodo_qs(_escopo_qs(Orcamento.objects.filter(ativo=True), escopo), 'criado_em', filtro)
    pagamentos = _periodo_qs(_escopo_qs(Pagamento.objects.filter(ativo=True), escopo), 'pago_em', filtro)
    if params.get('status'):
        if params['status'] not in dict(Orcamento.STATUS_CHOICES):
            raise ValidationError({'status': 'Status de orcamento invalido.'})
        orcamentos = orcamentos.filter(status=params['status'])
    if params.get('forma_pagamento'):
        if params['forma_pagamento'] not in dict(Pagamento.FORMAS_CHOICES):
            raise ValidationError({'forma_pagamento': 'Forma de pagamento invalida.'})
        pagamentos = pagamentos.filter(forma_pagamento=params['forma_pagamento'])
    if params.get('paciente'):
        try:
            paciente = Usuario.objects.get(pk=params['paciente'], tipo='PACIENTE')
        except (ValueError, Usuario.DoesNotExist) as exc:
            raise NotFound('Paciente nao encontrado.') from exc
        if escopo.clinica_id and paciente.clinica_id != escopo.clinica_id:
            raise NotFound('Paciente nao encontrado.')
        orcamentos, pagamentos = orcamentos.filter(paciente=paciente), pagamentos.filter(paciente=paciente)
    recebidos = pagamentos.aggregate(v=_valor(Sum('valor')), media=Avg('valor'))
    return {
        'total_orcamentos_aprovados': orcamentos.filter(status='APROVADO').aggregate(v=_valor(Sum('total')))['v'],
        'total_recebido': recebidos['v'],
        'total_pendente': orcamentos.filter(status='APROVADO').aggregate(v=_valor(Sum('saldo')))['v'],
        'total_vencido': orcamentos.filter(status='VENCIDO').aggregate(v=_valor(Sum('saldo')))['v'],
        'pagamentos_por_forma': list(pagamentos.values('forma_pagamento').annotate(total=_valor(Sum('valor')), quantidade=Count('id')).order_by('forma_pagamento')),
        'pagamentos_por_periodo': _serie(pagamentos, 'pago_em', filtro, escopo.timezone),
        'quantidade_pagamentos': pagamentos.count(), 'ticket_medio': recebidos['media'] or ZERO,
    }


def relatorio_pacientes(escopo, filtro):
    pacientes = _escopo_qs(Usuario.objects.filter(tipo='PACIENTE'), escopo)
    agenda = _periodo_qs(_escopo_qs(Agendamento.objects.all(), escopo), 'data_horario', filtro)
    envolvidos = agenda.values('paciente_id').distinct()
    return {
        'total_pacientes': pacientes.count(), 'novos_pacientes_no_periodo': _periodo_qs(pacientes, 'date_joined', filtro).count(),
        'pacientes_com_consulta_concluida': agenda.filter(status='CONCLUIDA').values('paciente_id').distinct().count(),
        'pacientes_com_consulta_cancelada': agenda.filter(status='CANCELADA').values('paciente_id').distinct().count(),
        'pacientes_com_falta': agenda.filter(status='NAO_COMPARECEU').values('paciente_id').distinct().count(),
        'pacientes_sem_consulta_no_periodo': pacientes.exclude(pk__in=envolvidos).count(),
        'distribuicao_por_periodo': _serie(_periodo_qs(pacientes, 'date_joined', filtro), 'date_joined', filtro, escopo.timezone),
    }


def relatorio_procedimentos(escopo, filtro):
    agenda = _periodo_qs(_escopo_qs(Agendamento.objects.filter(procedimento_ref__isnull=False), escopo), 'data_horario', filtro)
    return {
        'por_procedimento': list(agenda.values('procedimento_ref_id', 'procedimento').annotate(quantidade_agendamentos=Count('id'), quantidade_concluida=Count('id', filter=Q(status='CONCLUIDA'))).order_by('procedimento')),
        'frequencia_por_periodo': _serie(agenda, 'data_horario', filtro, escopo.timezone),
        'limitacao_valor_associado': 'Valores por procedimento usam itens de orcamento e nao possuem data de execucao; nao sao agregados neste relatorio.',
    }
