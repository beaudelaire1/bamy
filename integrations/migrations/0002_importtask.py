"""
Migration for creating the ``ImportTask`` model.

This migration introduces a new model used to track asynchronous import
operations.  The ``user`` field references the swappable user model to
ensure compatibility with custom user implementations.  See
``integrations.models.ImportTask`` for full model documentation.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = False
    dependencies = [
        ('integrations', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ImportTask',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='imports/')),
                ('status', models.CharField(choices=[('pending', 'En attente'), ('processing', 'En traitement'), ('completed', 'Terminé'), ('failed', 'Échoué')], default='pending', max_length=20)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('completed_at', models.DateTimeField(blank=True, null=True)),
                ('errors', models.TextField(blank=True, null=True)),
                ('success_count', models.IntegerField(default=0)),
                ('failure_count', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, help_text='Utilisateur ayant lancé la tâche d\'import.')),
            ],
            options={
                'verbose_name': "tâche d'importation",
                'verbose_name_plural': "tâches d'importation",
                'ordering': ['-created_at'],
            },
        ),
    ]