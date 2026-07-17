from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AgendamentoViewSet,
    BloqueioAgendaClinicaViewSet,
    ClinicaViewSet,
    ConviteCadastroPacienteViewSet,
    DentistaViewSet,
    EvolucaoClinicaViewSet,
    HorarioFuncionamentoClinicaViewSet,
    IndisponibilidadeDentistaViewSet,
    ProcedimentoViewSet,
    ProntuarioPacienteViewSet,
    UsuarioViewSet,
)

router = DefaultRouter()

router.register(r'clinicas', ClinicaViewSet, basename='clinica')
router.register(r'horarios-funcionamento', HorarioFuncionamentoClinicaViewSet, basename='horario-funcionamento')
router.register(r'bloqueios-agenda', BloqueioAgendaClinicaViewSet, basename='bloqueio-agenda')
router.register(r'indisponibilidades-dentistas', IndisponibilidadeDentistaViewSet, basename='indisponibilidade-dentista')
router.register(r'convites-pacientes', ConviteCadastroPacienteViewSet, basename='convite-paciente')
router.register(r'usuarios', UsuarioViewSet)
router.register(r'dentistas', DentistaViewSet, basename='dentista')
router.register(r'procedimentos', ProcedimentoViewSet, basename='procedimento')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamento')
router.register(r'prontuarios', ProntuarioPacienteViewSet, basename='prontuario')
router.register(r'evolucoes-clinicas', EvolucaoClinicaViewSet, basename='evolucao-clinica')

urlpatterns = [
    path('', include(router.urls)),
]
