from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AgendamentoViewSet,
    ArquivoClinicoViewSet,
    BloqueioAgendaClinicaViewSet,
    ClinicaViewSet,
    ConsentimentoPacienteViewSet,
    ConviteCadastroPacienteViewSet,
    DentistaViewSet,
    EvolucaoClinicaViewSet,
    HorarioFuncionamentoClinicaViewSet,
    IndisponibilidadeDentistaViewSet,
    ItemOrcamentoViewSet,
    ItemPlanoTratamentoViewSet,
    NotificacaoViewSet,
    OdontogramaViewSet,
    OrcamentoViewSet,
    PagamentoViewSet,
    ParcelaViewSet,
    PlanoTratamentoViewSet,
    PreferenciaComunicacaoViewSet,
    ProcedimentoViewSet,
    ProntuarioPacienteViewSet,
    RegistroOdontogramaViewSet,
    TemplateMensagemViewSet,
    TermoConsentimentoViewSet,
    UsuarioViewSet,
)
from .views_reports import (
    DashboardResumoView,
    RelatorioAgendamentosCsvView,
    RelatorioAgendamentosView,
    RelatorioFinanceiroCsvView,
    RelatorioFinanceiroView,
    RelatorioPacientesView,
    RelatorioProcedimentosView,
)

router = DefaultRouter()

router.register(r'clinicas', ClinicaViewSet, basename='clinica')
router.register(r'horarios-funcionamento', HorarioFuncionamentoClinicaViewSet, basename='horario-funcionamento')
router.register(r'bloqueios-agenda', BloqueioAgendaClinicaViewSet, basename='bloqueio-agenda')
router.register(
    r'indisponibilidades-dentistas', IndisponibilidadeDentistaViewSet, basename='indisponibilidade-dentista'
)
router.register(r'convites-pacientes', ConviteCadastroPacienteViewSet, basename='convite-paciente')
router.register(r'usuarios', UsuarioViewSet)
router.register(r'dentistas', DentistaViewSet, basename='dentista')
router.register(r'procedimentos', ProcedimentoViewSet, basename='procedimento')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamento')
router.register(r'prontuarios', ProntuarioPacienteViewSet, basename='prontuario')
router.register(r'evolucoes-clinicas', EvolucaoClinicaViewSet, basename='evolucao-clinica')
router.register(r'odontogramas', OdontogramaViewSet, basename='odontograma')
router.register(r'registros-odontograma', RegistroOdontogramaViewSet, basename='registro-odontograma')
router.register(r'planos-tratamento', PlanoTratamentoViewSet, basename='plano-tratamento')
router.register(r'itens-plano-tratamento', ItemPlanoTratamentoViewSet, basename='item-plano-tratamento')
router.register(r'orcamentos', OrcamentoViewSet, basename='orcamento')
router.register(r'itens-orcamento', ItemOrcamentoViewSet, basename='item-orcamento')
router.register(r'parcelas', ParcelaViewSet, basename='parcela')
router.register(r'pagamentos', PagamentoViewSet, basename='pagamento')
router.register(r'arquivos-clinicos', ArquivoClinicoViewSet, basename='arquivo-clinico')
router.register(r'termos-consentimento', TermoConsentimentoViewSet, basename='termo-consentimento')
router.register(r'consentimentos', ConsentimentoPacienteViewSet, basename='consentimento')
router.register(r'templates-mensagem', TemplateMensagemViewSet, basename='template-mensagem')
router.register(r'notificacoes', NotificacaoViewSet, basename='notificacao')
router.register(r'preferencias-comunicacao', PreferenciaComunicacaoViewSet, basename='preferencia-comunicacao')

urlpatterns = [
    path('dashboard/resumo/', DashboardResumoView.as_view(), name='dashboard-resumo'),
    path('relatorios/agendamentos/', RelatorioAgendamentosView.as_view(), name='relatorio-agendamentos'),
    path('relatorios/agendamentos/exportar.csv', RelatorioAgendamentosCsvView.as_view(), name='relatorio-agendamentos-csv'),
    path('relatorios/financeiro/', RelatorioFinanceiroView.as_view(), name='relatorio-financeiro'),
    path('relatorios/financeiro/exportar.csv', RelatorioFinanceiroCsvView.as_view(), name='relatorio-financeiro-csv'),
    path('relatorios/pacientes/', RelatorioPacientesView.as_view(), name='relatorio-pacientes'),
    path('relatorios/procedimentos/', RelatorioProcedimentosView.as_view(), name='relatorio-procedimentos'),
    path('', include(router.urls)),
]
