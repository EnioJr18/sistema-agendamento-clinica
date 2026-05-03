from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UsuarioViewSet, DentistaViewSet, AgendamentoViewSet

router = DefaultRouter()

router.register(r'usuarios', UsuarioViewSet)
router.register(r'dentistas', DentistaViewSet)
router.register(r'agendamentos', AgendamentoViewSet)

urlpatterns = [
    path('', include(router.urls)),
]