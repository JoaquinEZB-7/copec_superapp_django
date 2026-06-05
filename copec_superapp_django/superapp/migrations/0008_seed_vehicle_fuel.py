# -*- coding: utf-8 -*-
"""Ajusta el RAV4 con tanque bajo para mostrar la alerta de combustible."""
from django.db import migrations


def cargar(apps, schema_editor):
    Vehiculo = apps.get_model("superapp", "Vehiculo")
    Vehiculo.objects.filter(marca="Toyota", modelo="RAV4").update(
        nivel_combustible=15,
        capacidad_estanque_l=55,
    )


def borrar(apps, schema_editor):
    Vehiculo = apps.get_model("superapp", "Vehiculo")
    Vehiculo.objects.filter(marca="Toyota", modelo="RAV4").update(
        nivel_combustible=50,
        capacidad_estanque_l=55,
    )


class Migration(migrations.Migration):

    dependencies = [("superapp", "0007_vehicle_fuel_fields")]
    operations = [migrations.RunPython(cargar, borrar)]