# -*- coding: utf-8 -*-
"""Carga datos de demostración para presentar la super app."""
from django.db import migrations


def cargar(apps, schema_editor):
    Perfil = apps.get_model("superapp", "PerfilUsuario")
    Vehiculo = apps.get_model("superapp", "Vehiculo")
    Mantencion = apps.get_model("superapp", "Mantencion")
    Estacion = apps.get_model("superapp", "Estacion")
    Destino = apps.get_model("superapp", "Destino")
    EstacionRuta = apps.get_model("superapp", "EstacionRuta")
    Promocion = apps.get_model("superapp", "Promocion")
    Mision = apps.get_model("superapp", "Mision")

    perfil = Perfil.objects.create(nombre="Joaquín", saldo_copec_pay=48200,
                                   puntos_full=12540, nivel="Full Oro")

    v = Vehiculo.objects.create(
        propietario=perfil, marca="Toyota", modelo="RAV4", anio=2022, motor="2.0L",
        traccion="4x4", combustible="Gasolina", patente="KJ·PR·45", kilometraje=42760,
        rendimiento_kml=13.2, aceite_actual="Mobil 1 5W-30 sintético (10.02.2025)",
        presion_del=33, presion_tra=32, km_prox_mantencion=1240,
        prox_servicio="Cambio de aceite", medida_neumatico="225/65 R17")

    mant = [
        ("Cambio de aceite + filtro", "10 feb 2025 · 41.500 km · Copec Mantención", "orange"),
        ("Viaje Santiago → La Serena", "18 ene 2025 · 472 km · 36,1 L consumidos", "blue"),
        ("Rotación de neumáticos", "04 dic 2024 · 38.900 km", "green"),
        ("Revisión técnica al día", "Vence 09 / 2025", "navy"),
    ]
    for i, (t, d, c) in enumerate(mant):
        Mantencion.objects.create(vehiculo=v, tipo=t, detalle=d, color=c, orden=i)

    est = [
        ("Copec Providencia", "93 · 95 · 97 · Diésel · Pronto · Carga eléctrica", 1149, 0.9, True),
        ("Copec Tobalaba", "93 · 95 · 97 · Diésel · Pronto · Aire", 1168, 1.7, False),
        ("Copec Bilbao", "93 · 95 · 97 · Lavado · Mantención", 1172, 2.3, False),
    ]
    for i, (n, s, p, dist, dest) in enumerate(est):
        Estacion.objects.create(nombre=n, servicios=s, precio_93=p,
                                distancia_km=dist, destacada=dest, orden=i)

    rutas = {
        ("La Serena", 472): [
            ("Copec Til Til", 45, "Baño · Pronto"),
            ("Copec Los Vilos", 230, "Pronto · Comida ★"),
            ("Copec Ovalle", 380, "Carga rápida"),
        ],
        ("Pichilemu", 335): [
            ("Copec Angostura", 55, "Pronto · Baño"),
            ("Copec San Fernando", 140, "Comida ★ · Aire"),
            ("Copec Santa Cruz", 270, "Pronto"),
        ],
        ("Pucón", 780): [
            ("Copec Talca", 255, "Comida ★ · Pronto"),
            ("Copec Chillán", 400, "Carga rápida"),
            ("Copec Temuco", 675, "Pronto · Comida ★"),
        ],
    }
    for (nombre, km), paradas in rutas.items():
        d = Destino.objects.create(nombre=nombre, distancia_km=km)
        for i, (n, kmp, s) in enumerate(paradas):
            EstacionRuta.objects.create(destino=d, nombre=n, km_punto=kmp,
                                        servicios=s, orden=i)

    for t, det, p in [
        ("Café Pronto 2x1", "Todos los días antes de las 11:00 hrs", 0),
        ("Puntos Full x1.5", "Cargando con Copec Pay este fin de semana", 0),
        ("Carga eléctrica", "$120/kWh en estaciones seleccionadas", 0),
    ]:
        Promocion.objects.create(titulo=t, detalle=det, puntos=p)

    Mision.objects.create(titulo="Carga 3 veces este mes", detalle="2 de 3 · +500 puntos al completar", progreso=66)
    Mision.objects.create(titulo="Café Pronto x3", detalle="1 de 3 · +200 puntos", progreso=33)


def borrar(apps, schema_editor):
    for m in ["Mantencion","EstacionRuta","Vehiculo","Destino","Estacion",
              "Promocion","Mision","PerfilUsuario"]:
        apps.get_model("superapp", m).objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("superapp", "0001_initial")]
    operations = [migrations.RunPython(cargar, borrar)]
