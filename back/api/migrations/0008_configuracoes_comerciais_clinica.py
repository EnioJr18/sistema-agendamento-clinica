from datetime import time

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models
from django.utils.text import slugify


def gerar_slug_unico(clinica, usados):
    base = slugify(clinica.nome) or f'clinica-{clinica.pk}'
    candidato = base[:120]
    contador = 2
    while candidato in usados:
        sufixo = f'-{contador}'
        candidato = f'{base[:120 - len(sufixo)]}{sufixo}'
        contador += 1
    usados.add(candidato)
    return candidato


def preencher_slugs_e_horarios(apps, schema_editor):
    Clinica = apps.get_model('api', 'Clinica')
    HorarioFuncionamentoClinica = apps.get_model('api', 'HorarioFuncionamentoClinica')

    usados = set()
    for clinica in Clinica.objects.order_by('pk'):
        clinica.slug = gerar_slug_unico(clinica, usados)
        clinica.save(update_fields=['slug'])

        for dia_semana in range(5):
            HorarioFuncionamentoClinica.objects.get_or_create(
                clinica=clinica,
                dia_semana=dia_semana,
                horario_inicio=time(8, 0),
                horario_fim=time(18, 0),
                defaults={'ativo': True},
            )


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_refatora_agenda_status_duracao'),
    ]

    operations = [
        migrations.AddField(
            model_name='clinica',
            name='slug',
            field=models.SlugField(blank=True, max_length=120, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='clinica',
            name='timezone',
            field=models.CharField(default='America/Maceio', max_length=64),
        ),
        migrations.AddField(
            model_name='clinica',
            name='antecedencia_minima_cancelamento_horas',
            field=models.PositiveSmallIntegerField(default=24),
        ),
        migrations.AddField(
            model_name='clinica',
            name='duracao_padrao_consulta_minutos',
            field=models.PositiveSmallIntegerField(default=30, validators=[django.core.validators.MinValueValidator(1)]),
        ),
        migrations.CreateModel(
            name='HorarioFuncionamentoClinica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('dia_semana', models.PositiveSmallIntegerField(choices=[(0, 'Segunda-feira'), (1, 'Terca-feira'), (2, 'Quarta-feira'), (3, 'Quinta-feira'), (4, 'Sexta-feira'), (5, 'Sabado'), (6, 'Domingo')])),
                ('horario_inicio', models.TimeField()),
                ('horario_fim', models.TimeField()),
                ('ativo', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('clinica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='horarios_funcionamento', to='api.clinica')),
            ],
            options={
                'ordering': ['clinica', 'dia_semana', 'horario_inicio'],
            },
        ),
        migrations.RunPython(preencher_slugs_e_horarios, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='clinica',
            name='slug',
            field=models.SlugField(blank=True, max_length=120, unique=True),
        ),
        migrations.AddConstraint(
            model_name='horariofuncionamentoclinica',
            constraint=models.UniqueConstraint(fields=('clinica', 'dia_semana', 'horario_inicio', 'horario_fim'), name='horario_funcionamento_unico_por_intervalo'),
        ),
        migrations.AddIndex(
            model_name='horariofuncionamentoclinica',
            index=models.Index(fields=['clinica', 'dia_semana', 'ativo'], name='api_horario_clinica_c061ad_idx'),
        ),
    ]
