# -*- coding: utf-8 -*-
"""Carga notificaciones de ejemplo coherentes con la app."""
from django.db import migrations


def cargar(apps, schema_editor):
    Perfil = apps.get_model("superapp", "PerfilUsuario")
    Notificacion = apps.get_model("superapp", "Notificacion")

    perfil = Perfil.objects.first()
    if not perfil:
        return

    Notificacion.objects.bulk_create([
        Notificacion(
            perfil=perfil,
            tipo="vehiculo",
            titulo="Tu RAV4 pide cambio de aceite en 1.240 km",
            detalle="El próximo servicio sigue programado para el kilometraje estimado del vehículo.",
            icono="vehicle",
            leida=False,
        ),
        Notificacion(
            perfil=perfil,
            tipo="carga",
            titulo="Carga completada · +120 puntos Full",
            detalle="La sesión de carga quedó registrada y tus puntos ya fueron acreditados.",
            icono="bolt",
            leida=False,
        ),
        Notificacion(
            perfil=perfil,
            tipo="promo",
            titulo="Café Pronto 2x1 hasta las 11:00",
            detalle="La promo diaria sigue activa en locales seleccionados.",
            icono="coffee",
            leida=False,
        ),
        Notificacion(
            perfil=perfil,
            tipo="mision",
            titulo="Misión 'Carga 3 veces' al 66%",
            detalle="Llevas 2 de 3 cargas este mes y vas camino al premio.",
            icono="star",
            leida=False,
        ),
        Notificacion(
            perfil=perfil,
            tipo="sistema",
            titulo="Saldo Copec Pay actualizado",
            detalle="Tu billetera se sincronizó con los últimos movimientos registrados.",
            icono="wallet",
            leida=True,
        ),
    ])


def borrar(apps, schema_editor):
    apps.get_model("superapp", "Notificacion").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("superapp", "0005_notificacion")]
    operations = [migrations.RunPython(cargar, borrar)]