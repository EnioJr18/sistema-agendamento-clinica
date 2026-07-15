from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Agendamento, Clinica, Dentista, Endereco, HorarioFuncionamentoClinica, Procedimento, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    fieldsets = UserAdmin.fieldsets + (
        (
            'Informacoes cadastrais',
            {'fields': ('nome_completo', 'nome_preferido', 'cpf', 'telefone', 'data_nascimento', 'tipo', 'clinica')},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'Informacoes cadastrais',
            {'fields': ('nome_completo', 'nome_preferido', 'email', 'cpf', 'telefone', 'data_nascimento', 'tipo', 'clinica')},
        ),
    )
    list_display = ('username', 'nome_completo', 'email', 'cpf', 'tipo', 'clinica', 'is_staff', 'is_active')
    list_filter = ('tipo', 'clinica', 'is_staff', 'is_active')


@admin.register(Clinica)
class ClinicaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'slug', 'timezone', 'antecedencia_minima_cancelamento_horas', 'duracao_padrao_consulta_minutos', 'ativa')
    list_filter = ('ativa', 'timezone')
    search_fields = ('nome', 'slug', 'cnpj', 'email')


@admin.register(HorarioFuncionamentoClinica)
class HorarioFuncionamentoClinicaAdmin(admin.ModelAdmin):
    list_display = ('clinica', 'dia_semana', 'horario_inicio', 'horario_fim', 'ativo')
    list_filter = ('clinica', 'dia_semana', 'ativo')


@admin.register(Dentista)
class DentistaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'clinica', 'especialidade', 'cro', 'ativo')
    list_filter = ('clinica', 'ativo', 'especialidade')
    search_fields = ('usuario__nome_completo', 'cro', 'especialidade')


@admin.register(Procedimento)
class ProcedimentoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'clinica', 'duracao_minutos', 'ativo')
    list_filter = ('clinica', 'ativo')
    search_fields = ('nome', 'clinica__nome')


@admin.register(Agendamento)
class AgendamentoAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'dentista', 'clinica', 'procedimento', 'data_horario', 'status')
    list_filter = ('clinica', 'status', 'dentista')
    search_fields = ('paciente__nome_completo', 'dentista__usuario__nome_completo', 'procedimento')


admin.site.register(Endereco)
