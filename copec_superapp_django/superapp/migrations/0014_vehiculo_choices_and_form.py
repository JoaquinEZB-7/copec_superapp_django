# -*- coding: utf-8 -*-
from django.db import migrations, models


def normalizar_vehiculos(apps, schema_editor):
    Vehiculo = apps.get_model("superapp", "Vehiculo")
    Vehiculo.objects.filter(motor="2.0L").update(motor="2.0", tipo_carroceria="SUV", combustible="Gasolina")


def desnormalizar_vehiculos(apps, schema_editor):
    Vehiculo = apps.get_model("superapp", "Vehiculo")
    Vehiculo.objects.filter(motor="2.0").update(motor="2.0L", combustible="Gasolina", tipo_carroceria="SUV")


class Migration(migrations.Migration):
    dependencies = [("superapp", "0013_seed_mantenciones_2026")]

    operations = [
        migrations.AddField(
            model_name="vehiculo",
            name="tipo_carroceria",
            field=models.CharField(choices=[("SUV", "SUV"), ("Sedán", "Sedán"), ("Hatchback", "Hatchback"), ("Camioneta", "Camioneta"), ("Station Wagon", "Station Wagon"), ("City Car", "City Car")], default="SUV", max_length=20),
        ),
        migrations.AlterField(
            model_name="vehiculo",
            name="motor",
            field=models.CharField(choices=[("1.2", "1.2"), ("1.4", "1.4"), ("1.6", "1.6"), ("1.7", "1.7"), ("1.8", "1.8"), ("2.0", "2.0"), ("2.5", "2.5")], default="2.0", max_length=4),
        ),
        migrations.AlterField(
            model_name="vehiculo",
            name="combustible",
            field=models.CharField(choices=[("Gasolina", "Gasolina"), ("Diésel", "Diésel"), ("Híbrido", "Híbrido"), ("Eléctrico", "Eléctrico")], default="Gasolina", max_length=20),
        ),
        migrations.RunPython(normalizar_vehiculos, desnormalizar_vehiculos),
    ]