# -*- coding: utf-8 -*-
"""Carga transacciones de ejemplo y ajusta el saldo agregado."""
from django.db import migrations
from django.db.models import Sum


def cargar(apps, schema_editor):
    Perfil = apps.get_model("superapp", "PerfilUsuario")
    Transaccion = apps.get_model("superapp", "Transaccion")

    perfil = Perfil.objects.first()
    if not perfil:
        return

    Transaccion.objects.bulk_create([
        Transaccion(
            perfil=perfil,
            tipo="carga",
            descripcion="Carga de combustible en Copec Providencia",
            monto=72000,
            puntos_ganados=11200,
        ),
        Transaccion(
            perfil=perfil,
            tipo="pronto",
            descripcion="Café Pronto doble + pan de queso",
            monto=-3800,
            puntos_ganados=140,
        ),
        Transaccion(
            perfil=perfil,
            tipo="lavado",
            descripcion="Lavado exterior premium",
            monto=-9200,
            puntos_ganados=180,
        ),
        Transaccion(
            perfil=perfil,
            tipo="mantencion",
            descripcion="Cambio de aceite y filtro",
            monto=-4600,
            puntos_ganados=200,
        ),
        Transaccion(
            perfil=perfil,
            tipo="carga_electrica",
            descripcion="Carga eléctrica nocturna",
            monto=-6200,
            puntos_ganados=820,
        ),
    ])

    totales = Transaccion.objects.filter(perfil=perfil).aggregate(
        saldo=Sum("monto"),
        puntos=Sum("puntos_ganados"),
    )
    perfil.saldo_copec_pay = totales["saldo"] or 0
    perfil.puntos_full = totales["puntos"] or 0
    perfil.save(update_fields=["saldo_copec_pay", "puntos_full"])


def borrar(apps, schema_editor):
    apps.get_model("superapp", "Transaccion").objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("superapp", "0003_transaccion")]
    operations = [migrations.RunPython(cargar, borrar)]