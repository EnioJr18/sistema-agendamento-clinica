from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import AgendamentoViewSet, ClinicaViewSet, DentistaViewSet, ProcedimentoViewSet, UsuarioViewSet

router = DefaultRouter()

router.register(r'clinicas', ClinicaViewSet, basename='clinica')
router.register(r'usuarios', UsuarioViewSet)
router.register(r'dentistas', DentistaViewSet, basename='dentista')
router.register(r'procedimentos', ProcedimentoViewSet, basename='procedimento')
router.register(r'agendamentos', AgendamentoViewSet, basename='agendamento')

urlpatterns = [
    path('', include(router.urls)),
]
