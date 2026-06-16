# -*- coding: utf-8 -*-
from django.db import migrations


ESTACIONES_GRAN_CONCEPCION = [
    ("Copec Talcahuano (Autopista Concepción-Talcahuano)", "93·95·97·Diésel·Pronto·Lavado", 1149, 1.1, True),
    ("Copec Hualpén", "93·95·97·Diésel·Pronto·Carga eléctrica", 1156, 1.8, False),
    ("Copec Concepción (Pedro de Valdivia)", "93·95·97·Diésel·Pronto·MobilTec", 1168, 5.2, False),
    ("Copec San Pedro de la Paz", "93·95·97·Lavado·Aire", 1172, 8.0, False),
    ("Copec Chiguayante", "93·95·97·Pronto", 1175, 10.4, False),
]

DESTINOS_GRAN_CONCEPCION = [
    (
        "Santiago",
        500,
        [
            ("Copec Chillán", 110, "Pronto·Comida ★"),
            ("Copec Talca", 255, "Comida ★·Aire"),
            ("Copec Rancagua", 430, "Carga rápida"),
        ],
    ),
    (
        "Pucón",
        340,
        [
            ("Copec Los Ángeles", 135, "Pronto·Baño"),
            ("Copec Victoria", 250, "Comida ★"),
            ("Copec Temuco", 290, "Pronto·Carga rápida"),
        ],
    ),
    (
        "Los Ángeles",
        135,
        [
            ("Copec Cabrero", 70, "Baño·Pronto"),
            ("Copec Los Ángeles", 130, "Comida ★"),
        ],
    ),
    (
        "Valdivia",
        270,
        [
            ("Copec Collipulli", 170, "Pronto"),
            ("Copec Temuco", 240, "Comida ★·Carga rápida"),
        ],
    ),
]

ESTACIONES_ANTERIORES = [
    ("Copec Providencia", "93 · 95 · 97 · Diésel · Pronto · Carga eléctrica", 1149, 0.9, True),
    ("Copec Tobalaba", "93 · 95 · 97 · Diésel · Pronto · Aire", 1168, 1.7, False),
    ("Copec Bilbao", "93 · 95 · 97 · Lavado · Mantención", 1172, 2.3, False),
]

DESTINOS_ANTERIORES = [
    (
        "La Serena",
        472,
        [
            ("Copec Til Til", 45, "Baño · Pronto"),
            ("Copec Los Vilos", 230, "Pronto · Comida ★"),
            ("Copec Ovalle", 380, "Carga rápida"),
        ],
    ),
    (
        "Pichilemu",
        335,
        [
            ("Copec Angostura", 55, "Pronto · Baño"),
            ("Copec San Fernando", 140, "Comida ★ · Aire"),
            ("Copec Santa Cruz", 270, "Pronto"),
        ],
    ),
    (
        "Pucón",
        780,
        [
            ("Copec Talca", 255, "Comida ★ · Pronto"),
            ("Copec Chillán", 400, "Carga rápida"),
            ("Copec Temuco", 675, "Pronto · Comida ★"),
        ],
    ),
]


def seed_geo(apps, estaciones, destinos):
    Estacion = apps.get_model("superapp", "Estacion")
    Destino = apps.get_model("superapp", "Destino")
    EstacionRuta = apps.get_model("superapp", "EstacionRuta")

    EstacionRuta.objects.all().delete()
    Destino.objects.all().delete()
    Estacion.objects.all().delete()

    for orden, (nombre, servicios, precio_93, distancia_km, destacada) in enumerate(estaciones):
        Estacion.objects.create(
            nombre=nombre,
            servicios=servicios,
            precio_93=precio_93,
            distancia_km=distancia_km,
            destacada=destacada,
            orden=orden,
        )

    for orden, (nombre, distancia_km, paradas) in enumerate(destinos):
        destino = Destino.objects.create(nombre=nombre, distancia_km=distancia_km)
        for orden_ruta, (ruta_nombre, km_punto, servicios) in enumerate(paradas):
            EstacionRuta.objects.create(
                destino=destino,
                nombre=ruta_nombre,
                km_punto=km_punto,
                servicios=servicios,
                orden=orden_ruta,
            )


def cargar(apps, schema_editor):
    seed_geo(apps, ESTACIONES_GRAN_CONCEPCION, DESTINOS_GRAN_CONCEPCION)


def borrar(apps, schema_editor):
    seed_geo(apps, ESTACIONES_ANTERIORES, DESTINOS_ANTERIORES)


class Migration(migrations.Migration):
    dependencies = [("superapp", "0011_seed_profile_fuel_quota")]

    operations = [migrations.RunPython(cargar, borrar)]