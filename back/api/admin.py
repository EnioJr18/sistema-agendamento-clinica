from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Agendamento,
    Anamnese,
    BloqueioAgendaClinica,
    Clinica,
    ConviteCadastroPaciente,
    Dentista,
    Endereco,
    EvolucaoClinica,
    HorarioFuncionamentoClinica,
    IndisponibilidadeDentista,
    ItemOrcamento,
    ItemPlanoTratamento,
    Odontograma,
    Orcamento,
    Pagamento,
    Parcela,
    PlanoTratamento,
    Procedimento,
    ProntuarioPaciente,
    RegistroOdontograma,
    Usuario,
)


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


@admin.register(BloqueioAgendaClinica)
class BloqueioAgendaClinicaAdmin(admin.ModelAdmin):
    list_display = ('clinica', 'inicio', 'fim', 'motivo', 'ativo')
    list_filter = ('clinica', 'ativo', 'inicio', 'fim')
    search_fields = ('clinica__nome', 'motivo')


@admin.register(Dentista)
class DentistaAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'clinica', 'especialidade', 'cro', 'ativo')
    list_filter = ('clinica', 'ativo', 'especialidade')
    search_fields = ('usuario__nome_completo', 'cro', 'especialidade')


@admin.register(IndisponibilidadeDentista)
class IndisponibilidadeDentistaAdmin(admin.ModelAdmin):
    list_display = ('dentista', 'clinica', 'inicio', 'fim', 'motivo', 'ativo')
    list_filter = ('clinica', 'dentista', 'ativo', 'inicio', 'fim')
    search_fields = ('dentista__usuario__nome_completo', 'clinica__nome', 'motivo')


@admin.register(ConviteCadastroPaciente)
class ConviteCadastroPacienteAdmin(admin.ModelAdmin):
    list_display = ('clinica', 'nome_destino', 'telefone_destino', 'email_destino', 'expira_em', 'usado_em', 'ativo', 'criado_por')
    list_filter = ('clinica', 'ativo', 'expira_em', 'usado_em', 'criado_por')
    search_fields = ('nome_destino', 'telefone_destino', 'email_destino', 'clinica__nome', 'criado_por__username')
    readonly_fields = ('token', 'usado_em', 'criado_em', 'atualizado_em')


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


@admin.register(ProntuarioPaciente)
class ProntuarioPacienteAdmin(admin.ModelAdmin):
    list_display = ('paciente', 'clinica', 'ativo', 'criado_em', 'atualizado_em', 'criado_por')
    list_filter = ('clinica', 'ativo', 'criado_em')
    search_fields = ('paciente__nome_completo', 'paciente__cpf', 'clinica__nome')
    readonly_fields = ('criado_em', 'atualizado_em', 'criado_por', 'atualizado_por')


@admin.register(Anamnese)
class AnamneseAdmin(admin.ModelAdmin):
    list_display = ('prontuario', 'preenchida_em', 'preenchida_por', 'atualizada_em', 'atualizada_por')
    list_filter = ('prontuario__clinica', 'preenchida_em', 'atualizada_em')
    search_fields = ('prontuario__paciente__nome_completo', 'prontuario__paciente__cpf')
    readonly_fields = ('preenchida_em', 'preenchida_por', 'atualizada_em', 'atualizada_por')


@admin.register(EvolucaoClinica)
class EvolucaoClinicaAdmin(admin.ModelAdmin):
    list_display = ('prontuario', 'agendamento', 'dentista', 'criado_em', 'atualizado_em', 'criado_por')
    list_filter = ('prontuario__clinica', 'dentista', 'criado_em')
    search_fields = ('prontuario__paciente__nome_completo', 'dentista__usuario__nome_completo', 'descricao')
    readonly_fields = ('criado_em', 'atualizado_em', 'criado_por')


@admin.register(Odontograma)
class OdontogramaAdmin(admin.ModelAdmin):
    list_display = ('prontuario', 'clinica', 'ativo', 'criado_em', 'criado_por')
    list_filter = ('clinica', 'ativo', 'criado_em')
    search_fields = ('prontuario__paciente__nome_completo', 'prontuario__paciente__cpf')
    readonly_fields = ('clinica', 'prontuario', 'criado_em', 'atualizado_em', 'criado_por', 'atualizado_por')


@admin.register(RegistroOdontograma)
class RegistroOdontogramaAdmin(admin.ModelAdmin):
    list_display = ('odontograma', 'numero_dente', 'face', 'condicao', 'dentista', 'criado_em', 'ativo')
    list_filter = ('odontograma__clinica', 'condicao', 'face', 'dentista', 'ativo', 'criado_em')
    search_fields = ('odontograma__prontuario__paciente__nome_completo', 'numero_dente', 'observacao')
    readonly_fields = ('odontograma', 'numero_dente', 'face', 'condicao', 'dentista', 'criado_por', 'criado_em', 'atualizado_em')


@admin.register(PlanoTratamento)
class PlanoTratamentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'prontuario', 'clinica', 'status', 'criado_por', 'criado_em', 'ativo')
    list_filter = ('clinica', 'status', 'ativo', 'criado_em')
    search_fields = ('titulo', 'prontuario__paciente__nome_completo', 'descricao')
    readonly_fields = ('clinica', 'prontuario', 'criado_por', 'aprovado_em', 'concluido_em', 'criado_em', 'atualizado_em')


@admin.register(ItemPlanoTratamento)
class ItemPlanoTratamentoAdmin(admin.ModelAdmin):
    list_display = ('plano', 'descricao', 'numero_dente', 'prioridade', 'status', 'quantidade', 'ordem')
    list_filter = ('plano__clinica', 'prioridade', 'status', 'criado_em')
    search_fields = ('plano__titulo', 'plano__prontuario__paciente__nome_completo', 'descricao')
    readonly_fields = ('plano', 'criado_em', 'atualizado_em')


@admin.register(Orcamento)
class OrcamentoAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'clinica', 'paciente', 'status', 'total', 'valor_pago', 'saldo', 'validade_em', 'ativo')
    list_filter = ('clinica', 'status', 'ativo', 'validade_em', 'criado_em')
    search_fields = ('titulo', 'paciente__nome_completo', 'paciente__cpf', 'plano_tratamento__titulo')
    readonly_fields = ('clinica', 'subtotal', 'total', 'valor_pago', 'saldo', 'criado_por', 'aprovado_em', 'rejeitado_em', 'cancelado_em', 'criado_em', 'atualizado_em')


@admin.register(ItemOrcamento)
class ItemOrcamentoAdmin(admin.ModelAdmin):
    list_display = ('orcamento', 'descricao', 'quantidade', 'valor_unitario', 'subtotal', 'procedimento_ref', 'ativo')
    list_filter = ('orcamento__clinica', 'ativo', 'criado_em')
    search_fields = ('orcamento__titulo', 'orcamento__paciente__nome_completo', 'descricao')
    readonly_fields = ('subtotal', 'criado_em', 'atualizado_em')


@admin.register(Parcela)
class ParcelaAdmin(admin.ModelAdmin):
    list_display = ('orcamento', 'numero', 'clinica', 'valor', 'vencimento', 'status', 'paga_em', 'ativo')
    list_filter = ('clinica', 'status', 'ativo', 'vencimento', 'paga_em')
    search_fields = ('orcamento__titulo', 'orcamento__paciente__nome_completo')
    readonly_fields = ('clinica', 'orcamento', 'numero', 'valor', 'status', 'paga_em', 'criado_em', 'atualizado_em')


@admin.register(Pagamento)
class PagamentoAdmin(admin.ModelAdmin):
    list_display = ('orcamento', 'paciente', 'clinica', 'parcela', 'valor', 'forma_pagamento', 'pago_em', 'registrado_por', 'ativo')
    list_filter = ('clinica', 'forma_pagamento', 'ativo', 'pago_em', 'criado_em')
    search_fields = ('orcamento__titulo', 'paciente__nome_completo', 'referencia_externa', 'observacao')
    readonly_fields = ('clinica', 'paciente', 'orcamento', 'parcela', 'valor', 'forma_pagamento', 'pago_em', 'referencia_externa', 'registrado_por', 'criado_em')


admin.site.register(Endereco)
