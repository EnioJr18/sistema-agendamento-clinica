from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    TIPO_CHOICES = (
        ('DENTISTA', 'Dentista'),
        ('PACIENTE', 'Paciente'),
        ('ADMIN', 'Administrador'),
    )
    nome_completo = models.CharField(max_length=255)
    nome_preferido = models.CharField(max_length=150, blank=True)
    email = models.EmailField(unique=True)
    cpf = models.CharField(max_length=20, unique=True)
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, default='PACIENTE')
    telefone = models.CharField(max_length=20)
    data_nascimento = models.DateField(null=True)

    @property
    def idade(self):
        if self.data_nascimento:
            hoje = date.today()
            return hoje.year - self.data_nascimento.year - ((hoje.month, hoje.day) < (self.data_nascimento.month, self.data_nascimento.day))
        return None

    def get_full_name(self):
        return self.nome_completo or super().get_full_name()

    def get_short_name(self):
        return self.nome_preferido or self.nome_completo or self.username

    def __str__(self):
        return self.get_full_name() or self.username


class Endereco(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='endereco')
    cep = models.CharField(max_length=9, blank=True)
    logradouro = models.CharField(max_length=255, blank=True)
    numero = models.CharField(max_length=20, blank=True)
    complemento = models.CharField(max_length=100, blank=True)
    bairro = models.CharField(max_length=100, blank=True)
    cidade = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=2, blank=True)

    def __str__(self):
        partes = [self.logradouro, self.numero, self.cidade, self.estado]
        return ', '.join([parte for parte in partes if parte])


class Dentista(models.Model):
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_dentista')
    especialidade = models.CharField(max_length=100)
    cro = models.CharField(max_length=20, unique=True)
    ativo = models.BooleanField(default=True)
    disponibilidade = models.TextField(blank=True, null=True, help_text="Ex: Seg a Sex, 08h as 18h")

    def __str__(self):
        return f"Dr(a). {self.usuario.get_full_name()} - {self.especialidade}"
    

class Agendamento(models.Model):
    STATUS_CHOICES = (
        ('AGENDADO', 'Agendado'),
        ('CANCELADO', 'Cancelado'),
        ('CONCLUIDO', 'Concluído'),
    )

    dentista = models.ForeignKey(Dentista, on_delete=models.CASCADE, related_name='agenda')
    paciente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='meus_agendamentos')
    procedimento = models.CharField(max_length=150)

    data_horario = models.DateTimeField(help_text="Data e hora da consulta")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='AGENDADO')

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('dentista', 'data_horario')  # Garante que um dentista não tenha dois agendamentos no mesmo horário
        ordering = ['data_horario']

    def __str__(self):
        return f"{self.paciente} com {self.dentista} em {self.data_horario}"
