# -*- coding: utf-8 -*-
from django.db import migrations


FORWARD = [
    ("Cambio de aceite + filtro", "Cambio de aceite + filtro", "12 feb 2026 · 41.500 km · MobilTec", "orange"),
    ("Viaje Santiago → La Serena", "Viaje a Santiago", "18 abr 2026 · ~500 km", "blue"),
    ("Rotación de neumáticos", "Rotación de neumáticos", "20 dic 2025 · 39.800 km", "green"),
    ("Revisión técnica al día", "Revisión técnica al día", "Vence 09 / 2026", "navy"),
]

REVERSE = [
    ("Cambio de aceite + filtro", "Cambio de aceite + filtro", "10 feb 2025 · 41.500 km · Copec Mantención", "orange"),
    ("Viaje a Santiago", "Viaje Santiago → La Serena", "18 ene 2025 · 472 km · 36,1 L consumidos", "blue"),
    ("Rotación de neumáticos", "Rotación de neumáticos", "04 dic 2024 · 38.900 km", "green"),
    ("Revisión técnica al día", "Revisión técnica al día", "Vence 09 / 2025", "navy"),
]


def aplicar(apps, schema_editor, rows):
    Mantencion = apps.get_model("superapp", "Mantencion")
    for old_tipo, new_tipo, new_detalle, color in rows:
        Mantencion.objects.filter(tipo=old_tipo).update(tipo=new_tipo, detalle=new_detalle, color=color)


def cargar(apps, schema_editor):
    aplicar(apps, schema_editor, FORWARD)


def borrar(apps, schema_editor):
    aplicar(apps, schema_editor, REVERSE)


class Migration(migrations.Migration):
    dependencies = [("superapp", "0012_seed_gran_concepcion")]

    operations = [migrations.RunPython(cargar, borrar)]