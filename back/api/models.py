from datetime import date

from django.contrib.auth.models import AbstractUser
from django.db import models


class Clinica(models.Model):
    nome = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18, unique=True, blank=True, null=True)
    telefone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    ativa = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']

    def __str__(self):
        return self.nome


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
    clinica = models.ForeignKey(Clinica, on_delete=models.PROTECT, related_name='usuarios', null=True, blank=True)
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
    clinica = models.ForeignKey(Clinica, on_delete=models.PROTECT, related_name='dentistas')
    usuario = models.OneToOneField(Usuario, on_delete=models.CASCADE, related_name='perfil_dentista')
    especialidade = models.CharField(max_length=100)
    cro = models.CharField(max_length=20, unique=True)
    ativo = models.BooleanField(default=True)
    disponibilidade = models.TextField(blank=True, null=True, help_text='Ex: Seg a Sex, 08h as 18h')

    def __str__(self):
        return f"Dr(a). {self.usuario.get_full_name()} - {self.especialidade}"


class Procedimento(models.Model):
    clinica = models.ForeignKey(Clinica, on_delete=models.PROTECT, related_name='procedimentos')
    nome = models.CharField(max_length=150)
    descricao = models.TextField(blank=True)
    duracao_minutos = models.PositiveSmallIntegerField(default=30)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['nome']
        constraints = [
            models.UniqueConstraint(fields=['clinica', 'nome'], name='procedimento_nome_unico_por_clinica'),
        ]

    def __str__(self):
        return self.nome


class Agendamento(models.Model):
    STATUS_AGENDADA = 'AGENDADA'
    STATUS_CONFIRMADA = 'CONFIRMADA'
    STATUS_EM_ATENDIMENTO = 'EM_ATENDIMENTO'
    STATUS_CONCLUIDA = 'CONCLUIDA'
    STATUS_CANCELADA = 'CANCELADA'
    STATUS_NAO_COMPARECEU = 'NAO_COMPARECEU'

    STATUS_CHOICES = (
        (STATUS_AGENDADA, 'Agendada'),
        (STATUS_CONFIRMADA, 'Confirmada'),
        (STATUS_EM_ATENDIMENTO, 'Em atendimento'),
        (STATUS_CONCLUIDA, 'Concluida'),
        (STATUS_CANCELADA, 'Cancelada'),
        (STATUS_NAO_COMPARECEU, 'Nao compareceu'),
    )

    clinica = models.ForeignKey(Clinica, on_delete=models.PROTECT, related_name='agendamentos')
    dentista = models.ForeignKey(Dentista, on_delete=models.CASCADE, related_name='agenda')
    paciente = models.ForeignKey(Usuario, on_delete=models.CASCADE, related_name='meus_agendamentos')
    procedimento = models.CharField(max_length=150)
    procedimento_ref = models.ForeignKey(Procedimento, on_delete=models.PROTECT, related_name='agendamentos', null=True, blank=True)

    data_horario = models.DateTimeField(help_text='Data e hora da consulta')
    data_hora_fim = models.DateTimeField(null=True, blank=True)
    duracao_minutos = models.PositiveSmallIntegerField(default=30)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_AGENDADA)

    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['data_horario']
        indexes = [
            models.Index(fields=['dentista', 'data_horario']),
            models.Index(fields=['clinica', 'status']),
        ]

    def __str__(self):
        return f"{self.paciente} com {self.dentista} em {self.data_horario}"
