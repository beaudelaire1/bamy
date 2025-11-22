from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("userauths", "0004_alter_emailchangerequest_id"),
    ]

    operations = [
        migrations.AddField(
            model_name="user",
            name="client_type",
            field=models.CharField(
                max_length=20,
                choices=[
                    ("wholesaler", "Grossiste"),
                    ("big_retail", "Grande distribution"),
                    ("small_retail", "Petite distribution"),
                    ("regular", "Utilisateur lambda"),
                ],
                default="regular",
                verbose_name="Type de client",
                help_text="Détermine les conditions tarifaires appliquées aux prix affichés.",
            ),
        ),
    ]
