from datetime import timedelta

from django.db import migrations, models


def migrar_agendamentos(apps, schema_editor):
    Agendamento = apps.get_model('api', 'Agendamento')
    mapa_status = {
        'AGENDADO': 'AGENDADA',
        'CANCELADO': 'CANCELADA',
        'CONCLUIDO': 'CONCLUIDA',
    }

    for agendamento in Agendamento.objects.select_related('procedimento_ref').all():
        agendamento.status = mapa_status.get(agendamento.status, agendamento.status)
        duracao = 30
        if agendamento.procedimento_ref_id and agendamento.procedimento_ref.duracao_minutos:
            duracao = agendamento.procedimento_ref.duracao_minutos
        agendamento.duracao_minutos = duracao
        agendamento.data_hora_fim = agendamento.data_horario + timedelta(minutes=duracao)
        agendamento.save(update_fields=['status', 'duracao_minutos', 'data_hora_fim'])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0006_fundacao_multiclinica'),
    ]

    operations = [
        migrations.AddField(
            model_name='agendamento',
            name='data_hora_fim',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='agendamento',
            name='duracao_minutos',
            field=models.PositiveSmallIntegerField(default=30),
        ),
        migrations.RunPython(migrar_agendamentos, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='agendamento',
            name='status',
            field=models.CharField(
                choices=[
                    ('AGENDADA', 'Agendada'),
                    ('CONFIRMADA', 'Confirmada'),
                    ('EM_ATENDIMENTO', 'Em atendimento'),
                    ('CONCLUIDA', 'Concluida'),
                    ('CANCELADA', 'Cancelada'),
                    ('NAO_COMPARECEU', 'Nao compareceu'),
                ],
                default='AGENDADA',
                max_length=20,
            ),
        ),
        migrations.AlterUniqueTogether(
            name='agendamento',
            unique_together=set(),
        ),
        migrations.AddIndex(
            model_name='agendamento',
            index=models.Index(fields=['dentista', 'data_horario'], name='api_agendam_dentist_d90bc9_idx'),
        ),
        migrations.AddIndex(
            model_name='agendamento',
            index=models.Index(fields=['clinica', 'status'], name='api_agendam_clinica_2d39c1_idx'),
        ),
    ]
