from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("superapp", "0014_vehiculo_choices_and_form")]

    operations = [
        migrations.AddField(
            model_name="mantencion",
            name="km_realizado",
            field=models.IntegerField(default=0, verbose_name="Km al realizar"),
        ),
    ]
