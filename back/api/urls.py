from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    AgendamentoViewSet,
    ClinicaViewSet,
    DentistaViewSet,
    HorarioFuncionamentoClinicaViewSet,
    ProcedimentoViewSet,
    UsuarioViewSet,
)

router = DefaultRouter()

router.register(r'clinicas', ClinicaViewSet, basename='clinica')
router.register(r'horarios-funcionamento', HorarioFuncionamentoClinicaViewSet, basename='horario-funcionamento')
router.register(r'usuarios', UsuarioViewSet)
router.register(r'dentistas', DentistaViewSet, basename='dentista')
router.register(r'procedimentos', ProcedimentoViewSet, basename='procedimento')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamento')

urlpatterns = [
    path('', include(router.urls)),
]
