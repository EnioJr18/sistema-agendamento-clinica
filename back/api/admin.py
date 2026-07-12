from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Agendamento, Dentista, Endereco, Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    fieldsets = UserAdmin.fieldsets + (
        (
            'Informacoes cadastrais',
            {'fields': ('nome_completo', 'nome_preferido', 'cpf', 'telefone', 'data_nascimento', 'tipo')},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'Informacoes cadastrais',
            {'fields': ('nome_completo', 'nome_preferido', 'email', 'cpf', 'telefone', 'data_nascimento', 'tipo')},
        ),
    )
    list_display = ('username', 'nome_completo', 'email', 'cpf', 'tipo', 'is_staff', 'is_active')


admin.site.register(Dentista)
admin.site.register(Agendamento)
admin.site.register(Endereco)
