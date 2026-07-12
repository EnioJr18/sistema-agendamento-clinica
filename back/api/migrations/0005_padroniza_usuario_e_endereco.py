import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def preencher_dados_cadastrais(apps, schema_editor):
    Usuario = apps.get_model('api', 'Usuario')
    emails_usados = set()
    cpfs_usados = set()

    for usuario in Usuario.objects.order_by('pk'):
        nome = f"{usuario.first_name} {usuario.last_name}".strip()
        if not usuario.nome_completo:
            usuario.nome_completo = nome or usuario.username or f"Usuario {usuario.pk}"

        if not usuario.nome_preferido and usuario.first_name:
            usuario.nome_preferido = usuario.first_name

        email = (usuario.email or '').strip().lower()
        if not email or email in emails_usados:
            email = f"usuario-{usuario.pk}@legacy.invalid"
        usuario.email = email
        emails_usados.add(email)

        cpf = (usuario.cpf or '').strip()
        if not cpf or cpf in cpfs_usados:
            cpf = f"LEGACY{usuario.pk:011d}"
        usuario.cpf = cpf
        cpfs_usados.add(cpf)

        if not usuario.telefone:
            usuario.telefone = 'Nao informado'

        usuario.save(
            update_fields=[
                'nome_completo',
                'nome_preferido',
                'email',
                'cpf',
                'telefone',
            ]
        )


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_agendamento_procedimento_alter_usuario_tipo_dentista_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='usuario',
            name='nome_completo',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name='usuario',
            name='nome_preferido',
            field=models.CharField(blank=True, max_length=150),
        ),
        migrations.AddField(
            model_name='usuario',
            name='cpf',
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.RunPython(preencher_dados_cadastrais, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='usuario',
            name='nome_completo',
            field=models.CharField(max_length=255),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='cpf',
            field=models.CharField(max_length=20, unique=True),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='telefone',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='data_nascimento',
            field=models.DateField(null=True),
        ),
        migrations.CreateModel(
            name='Endereco',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cep', models.CharField(blank=True, max_length=9)),
                ('logradouro', models.CharField(blank=True, max_length=255)),
                ('numero', models.CharField(blank=True, max_length=20)),
                ('complemento', models.CharField(blank=True, max_length=100)),
                ('bairro', models.CharField(blank=True, max_length=100)),
                ('cidade', models.CharField(blank=True, max_length=100)),
                ('estado', models.CharField(blank=True, max_length=2)),
                ('usuario', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='endereco', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
