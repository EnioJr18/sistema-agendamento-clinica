from django.contrib import admin
from .models import Usuario, Medico, Agendamento
from django.contrib.auth.admin import UserAdmin

@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('tipo', 'telefone')}),
    )


admin.site.register(Medico)
admin.site.register(Agendamento)