import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0008_configuracoes_comerciais_clinica'),
    ]

    operations = [
        migrations.CreateModel(
            name='BloqueioAgendaClinica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicio', models.DateTimeField()),
                ('fim', models.DateTimeField()),
                ('motivo', models.CharField(blank=True, max_length=255)),
                ('ativo', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('clinica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bloqueios_agenda', to='api.clinica')),
            ],
            options={
                'ordering': ['inicio'],
            },
        ),
        migrations.CreateModel(
            name='IndisponibilidadeDentista',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inicio', models.DateTimeField()),
                ('fim', models.DateTimeField()),
                ('motivo', models.CharField(blank=True, max_length=255)),
                ('ativo', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('clinica', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indisponibilidades_dentistas', to='api.clinica')),
                ('dentista', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='indisponibilidades', to='api.dentista')),
            ],
            options={
                'ordering': ['inicio'],
            },
        ),
        migrations.AddIndex(
            model_name='bloqueioagendaclinica',
            index=models.Index(fields=['clinica', 'ativo', 'inicio', 'fim'], name='api_bloquei_clinica_bd1f4f_idx'),
        ),
        migrations.AddIndex(
            model_name='indisponibilidadedentista',
            index=models.Index(fields=['clinica', 'dentista', 'ativo', 'inicio', 'fim'], name='api_indispo_clinica_31c1e0_idx'),
        ),
    ]
