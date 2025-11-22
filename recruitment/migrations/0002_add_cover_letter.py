from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("recruitment", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="jobapplication",
            name="cover_letter",
            field=models.FileField(
                upload_to="applications/cover_letters/",
                blank=True,
                null=True,
                verbose_name="Lettre de motivation",
            ),
        ),
    ]