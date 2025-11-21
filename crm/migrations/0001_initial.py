from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name='Customer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('first_name', models.CharField(blank=True, max_length=100, verbose_name='Prénom')),
                ('last_name', models.CharField(blank=True, max_length=100, verbose_name='Nom')),
                ('company', models.CharField(blank=True, max_length=200, verbose_name='Entreprise')),
                ('phone', models.CharField(blank=True, max_length=50, verbose_name='Téléphone')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('notes', models.TextField(blank=True, verbose_name='Notes')),
            ],
            options={
                'verbose_name': 'client',
                'verbose_name_plural': 'clients',
                'ordering': ['-created_at'],
            },
        ),
    ]