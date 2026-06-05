# -*- coding: utf-8 -*-
"""Deja un cupo de combustible de ejemplo en el perfil del usuario."""
from django.db import migrations


def cargar(apps, schema_editor):
    Perfil = apps.get_model("superapp", "PerfilUsuario")
    Perfil.objects.filter(nombre="Joaquín").update(cupo_combustible=90000)


def borrar(apps, schema_editor):
    Perfil = apps.get_model("superapp", "PerfilUsuario")
    Perfil.objects.filter(nombre="Joaquín").update(cupo_combustible=90000)


class Migration(migrations.Migration):

    dependencies = [("superapp", "0010_profile_fuel_quota")]
    operations = [migrations.RunPython(cargar, borrar)]