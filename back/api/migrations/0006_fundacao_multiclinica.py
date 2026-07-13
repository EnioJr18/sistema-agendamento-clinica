import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def criar_clinica_padrao(apps, schema_editor):
    Clinica = apps.get_model('api', 'Clinica')
    Usuario = apps.get_model('api', 'Usuario')
    Dentista = apps.get_model('api', 'Dentista')
    Agendamento = apps.get_model('api', 'Agendamento')

    clinica_padrao, _ = Clinica.objects.get_or_create(
        nome='Clinica Padrao',
        defaults={
            'telefone': 'Nao informado',
            'email': 'clinica-padrao@legacy.invalid',
            'ativa': True,
        },
    )

    Usuario.objects.filter(clinica__isnull=True, is_staff=False).update(clinica=clinica_padrao)

    for dentista in Dentista.objects.select_related('usuario').filter(clinica__isnull=True):
        dentista.clinica = dentista.usuario.clinica or clinica_padrao
        dentista.save(update_fields=['clinica'])

    for agendamento in Agendamento.objects.select_related('dentista', 'paciente').filter(clinica__isnull=True):
        agendamento.clinica = agendamento.dentista.clinica or agendamento.paciente.clinica or clinica_padrao
        agendamento.save(update_fields=['clinica'])


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_padroniza_usuario_e_endereco'),
    ]

    operations = [
        migrations.CreateModel(
            name='Clinica',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=255)),
                ('cnpj', models.CharField(blank=True, max_length=18, null=True, unique=True)),
                ('telefone', models.CharField(blank=True, max_length=20)),
                ('email', models.EmailField(blank=True, max_length=254)),
                ('ativa', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['nome'],
            },
        ),
        migrations.AddField(
            model_name='usuario',
            name='clinica',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='usuarios', to='api.clinica'),
        ),
        migrations.AddField(
            model_name='dentista',
            name='clinica',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='dentistas', to='api.clinica'),
        ),
        migrations.AddField(
            model_name='agendamento',
            name='clinica',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='agendamentos', to='api.clinica'),
        ),
        migrations.CreateModel(
            name='Procedimento',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=150)),
                ('descricao', models.TextField(blank=True)),
                ('duracao_minutos', models.PositiveSmallIntegerField(default=30)),
                ('ativo', models.BooleanField(default=True)),
                ('criado_em', models.DateTimeField(auto_now_add=True)),
                ('atualizado_em', models.DateTimeField(auto_now=True)),
                ('clinica', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='procedimentos', to='api.clinica')),
            ],
            options={
                'ordering': ['nome'],
            },
        ),
        migrations.AddField(
            model_name='agendamento',
            name='procedimento_ref',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='agendamentos', to='api.procedimento'),
        ),
        migrations.RunPython(criar_clinica_padrao, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='dentista',
            name='clinica',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='dentistas', to='api.clinica'),
        ),
        migrations.AlterField(
            model_name='agendamento',
            name='clinica',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='agendamentos', to='api.clinica'),
        ),
        migrations.AddConstraint(
            model_name='procedimento',
            constraint=models.UniqueConstraint(fields=('clinica', 'nome'), name='procedimento_nome_unico_por_clinica'),
        ),
    ]
