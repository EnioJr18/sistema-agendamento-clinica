import csv

from django.http import HttpResponse
from drf_spectacular.utils import OpenApiTypes, extend_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .services_reports import (
    dashboard_resumo,
    escopo_para_usuario,
    filtro_periodo,
    relatorio_agendamentos,
    relatorio_financeiro,
    relatorio_pacientes,
    relatorio_procedimentos,
)


class RelatorioBaseView(APIView):
    permission_classes = [IsAuthenticated]
    somente_staff = False

    def contexto(self, request):
        if self.somente_staff and not request.user.is_staff:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied('Este relatorio e restrito a staff/admin.')
        escopo = escopo_para_usuario(request.user)
        return escopo, filtro_periodo(request.query_params, escopo.timezone)


class DashboardResumoView(RelatorioBaseView):
    somente_staff = True

    @extend_schema(description='Resumo administrativo. Periodo padrao: 30d. Apenas staff/admin.', responses=OpenApiTypes.OBJECT)
    def get(self, request):
        escopo, filtro = self.contexto(request)
        return Response(dashboard_resumo(escopo, filtro))


class RelatorioAgendamentosView(RelatorioBaseView):
    @extend_schema(description='Indicadores agregados de agenda, filtrados pelo contexto autenticado.', responses=OpenApiTypes.OBJECT)
    def get(self, request):
        escopo, filtro = self.contexto(request)
        return Response(relatorio_agendamentos(escopo, filtro, request.query_params))


class RelatorioFinanceiroView(RelatorioBaseView):
    somente_staff = True

    @extend_schema(description='Indicadores financeiros agregados. Apenas staff/admin.', responses=OpenApiTypes.OBJECT)
    def get(self, request):
        escopo, filtro = self.contexto(request)
        return Response(relatorio_financeiro(escopo, filtro, request.query_params))


class RelatorioPacientesView(RelatorioBaseView):
    @extend_schema(description='Indicadores agregados de pacientes, sem dados pessoais desnecessarios.', responses=OpenApiTypes.OBJECT)
    def get(self, request):
        escopo, filtro = self.contexto(request)
        return Response(relatorio_pacientes(escopo, filtro))


class RelatorioProcedimentosView(RelatorioBaseView):
    @extend_schema(description='Frequencia agregada de procedimentos por periodo.', responses=OpenApiTypes.OBJECT)
    def get(self, request):
        escopo, filtro = self.contexto(request)
        return Response(relatorio_procedimentos(escopo, filtro))


def _csv_response(nome, cabecalho, linhas):
    resposta = HttpResponse(content_type='text/csv; charset=utf-8')
    resposta['Content-Disposition'] = f'attachment; filename="{nome}.csv"'
    resposta.write('\ufeff')
    writer = csv.writer(resposta)
    writer.writerow(cabecalho)
    for linha in linhas:
        writer.writerow([f"'{valor}" if isinstance(valor, str) and valor[:1] in '=+-@' else valor for valor in linha])
    return resposta


class RelatorioAgendamentosCsvView(RelatorioAgendamentosView):
    @extend_schema(responses=OpenApiTypes.BINARY)
    def get(self, request):
        escopo, filtro = self.contexto(request)
        dados = relatorio_agendamentos(escopo, filtro, request.query_params)
        return _csv_response('relatorio-agendamentos', ['status', 'quantidade'], [(item['status'], item['quantidade']) for item in dados['por_status']])


class RelatorioFinanceiroCsvView(RelatorioFinanceiroView):
    @extend_schema(responses=OpenApiTypes.BINARY)
    def get(self, request):
        escopo, filtro = self.contexto(request)
        dados = relatorio_financeiro(escopo, filtro, request.query_params)
        return _csv_response('relatorio-financeiro', ['forma_pagamento', 'quantidade', 'total'], [(item['forma_pagamento'], item['quantidade'], item['total']) for item in dados['pagamentos_por_forma']])
