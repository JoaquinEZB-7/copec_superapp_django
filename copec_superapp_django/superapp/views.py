import random
import time

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Avg, Sum
from django.db.models.functions import TruncMonth
from .models import (PerfilUsuario, Vehiculo, Mantencion, Estacion,
                     Destino, Promocion, Mision)
from .forms import VehiculoForm, estimar_rendimiento
from .utils import clp, dec1

HISTORIALES_PRESET = [
    [   # Conductor urbano
        {"tipo": "Cambio de aceite", "detalle": "Mobil 1 5W-30 sintético · 42.000 km", "color": "blue", "orden": 1},
        {"tipo": "Revisión neumáticos", "detalle": "Presión y desgaste · 38.500 km", "color": "green", "orden": 2},
        {"tipo": "Lavado completo", "detalle": "Interior y exterior · 35.000 km", "color": "navy", "orden": 3},
        {"tipo": "Filtro de aire", "detalle": "Reemplazo · 30.000 km", "color": "orange", "orden": 4},
    ],
    [   # Conductor de ruta
        {"tipo": "Revisión 40.000 km", "detalle": "Completa en taller Copec · 40.000 km", "color": "blue", "orden": 1},
        {"tipo": "Cambio de neumáticos", "detalle": "4× Bridgestone 225/65 R17 · 38.000 km", "color": "orange", "orden": 2},
        {"tipo": "Filtro de combustible", "detalle": "Reemplazo · 35.000 km", "color": "green", "orden": 3},
        {"tipo": "Alineación y balanceo", "detalle": "Ajuste completo · 30.000 km", "color": "navy", "orden": 4},
    ],
    [   # Auto con historial extenso
        {"tipo": "Pastillas de freno", "detalle": "Eje delantero · 41.000 km", "color": "orange", "orden": 1},
        {"tipo": "Batería", "detalle": "Reemplazo Bosch 60 Ah · 39.000 km", "color": "blue", "orden": 2},
        {"tipo": "Cambio de aceite", "detalle": "Shell Helix 10W-40 · 35.000 km", "color": "navy", "orden": 3},
        {"tipo": "Revisión suspensión", "detalle": "Amortiguadores delanteros · 28.000 km", "color": "green", "orden": 4},
    ],
    [   # Dueño cuidadoso / auto nuevo
        {"tipo": "Primera revisión", "detalle": "Revisión técnica · 10.000 km", "color": "green", "orden": 1},
        {"tipo": "Cambio de aceite", "detalle": "Castrol Edge 5W-30 · 10.000 km", "color": "blue", "orden": 2},
        {"tipo": "Inspección técnica", "detalle": "CITV aprobada · 12.000 km", "color": "navy", "orden": 3},
        {"tipo": "Detailing completo", "detalle": "Nano cerámica exterior · 15.000 km", "color": "orange", "orden": 4},
    ],
]


def calcular_cupo_sugerido(perfil):
    cargas = perfil.transacciones.filter(tipo="carga", monto__gt=0)
    promedio_mensual = (
        cargas.annotate(mes=TruncMonth("fecha"))
        .values("mes")
        .annotate(total=Sum("monto"))
        .aggregate(promedio=Avg("total"))["promedio"]
    )
    base = promedio_mensual or 60000
    cupo = round((base * 1.5) / 1000) * 1000
    return cupo


def build_context(active_screen="home", extra=None):
    perfil = PerfilUsuario.objects.first()
    vehiculo = Vehiculo.objects.last()
    servicios_app = [
        {"clave": "combustible", "nombre": "Combustible", "icono": "blue", "piso_destino": "mapa", "sugerido": False},
        {"clave": "vehiculo", "nombre": "Mi Vehículo", "icono": "green", "piso_destino": "vehiculo", "sugerido": False},
        {"clave": "mantencion", "nombre": "Mantención", "icono": "orange", "piso_destino": "mantencion", "sugerido": False},
        {"clave": "market", "nombre": "Pronto Market", "icono": "orange", "piso_destino": "market", "sugerido": False},
        {"clave": "full", "nombre": "Beneficios Full", "icono": "amber", "piso_destino": "full", "sugerido": False},
    ]
    cupo_sugerido = 0
    if perfil:
        perfil.recalcular_saldo_y_puntos()
        cupo_sugerido = calcular_cupo_sugerido(perfil)
    if vehiculo and vehiculo.km_prox_mantencion <= 1500:
        for servicio in servicios_app:
            if servicio["clave"] == "mantencion":
                servicio["sugerido"] = True

    recomendaciones = []
    if vehiculo:
        recomendaciones.append({
            "texto": f"Tu {vehiculo.modelo} rinde mejor con 95 octanos",
            "detalle": f"Según tu auto {vehiculo.motor} y uso actual, te conviene ese octanaje.",
            "piso_destino": "mapa",
            "tono": "blue",
        })

    if Promocion.objects.filter(titulo__icontains="Puntos Full x1.5").exists():
        recomendaciones.append({
            "texto": "Te conviene cargar hoy: promo de puntos x1.5",
            "detalle": "Hay una promo activa que mejora tu acumulación de puntos Full.",
            "piso_destino": "market",
            "tono": "orange",
        })

    if vehiculo:
        lavados = Mantencion.objects.filter(vehiculo=vehiculo, tipo__icontains="lavado")
        if not lavados.exists():
            recomendaciones.append({
                "texto": "Llevas 3 meses sin lavado, agéndalo",
                "detalle": "Tu historial no muestra un lavado reciente y conviene ponerlo al día.",
                "piso_destino": "mantencion",
                "tono": "green",
            })
    _rng = random.Random(int(time.time()) // 600)
    _estados = [
        ("Libre",    "var(--green)"),
        ("Moderada", "var(--amber)"),
        ("Llena",    "#e03131"),
    ]
    estaciones = list(Estacion.objects.all())
    for e in estaciones:
        st = _rng.choices(_estados, weights=[0.5, 0.35, 0.15])[0]
        e.ocupacion_label = st[0]
        e.ocupacion_color = st[1]

    resumen_valor = None
    if perfil:
        n_inter = perfil.transacciones.count()
        n_svc = perfil.transacciones.values("tipo").distinct().count()
        resumen_valor = {
            "n_interacciones": n_inter,
            "n_servicios": n_svc,
            "valor_puntos_clp": "$" + clp(perfil.puntos_full // 2),
        }

    contexto = {
        "perfil": perfil,
        "vehiculo": vehiculo,
        "mantenciones": Mantencion.objects.filter(vehiculo=vehiculo) if vehiculo else [],
        "estaciones": estaciones,
        "destinos": Destino.objects.all(),
        "promociones": Promocion.objects.all(),
        "misiones": Mision.objects.all(),
        "transacciones_recientes": perfil.transacciones.all()[:5] if perfil else [],
        "notificaciones_recientes": perfil.notificaciones.all()[:5] if perfil else [],
        "cupo_sugerido": cupo_sugerido,
        "cupo_sugerido_fmt": "$" + clp(cupo_sugerido) if perfil else "$0",
        "servicios_app": servicios_app,
        "recomendaciones": recomendaciones,
        "resumen_valor": resumen_valor,
        "active_screen": active_screen,
    }
    if extra:
        contexto.update(extra)
    return contexto


def home(request):
    active_screen = request.GET.get("screen", "home")
    return render(request, "superapp/base.html", build_context(active_screen))


def agregar_vehiculo(request):
    if request.method == "POST":
        form = VehiculoForm(request.POST)
        if form.is_valid():
            vehiculo = form.save(commit=False)
            perfil = PerfilUsuario.objects.first()
            vehiculo.propietario = perfil
            rendimiento = form.cleaned_data.get("rendimiento_kml")
            if rendimiento in (None, ""):
                rendimiento = estimar_rendimiento(form.cleaned_data["combustible"])
            vehiculo.rendimiento_kml = rendimiento
            vehiculo.save()
            for item in random.choice(HISTORIALES_PRESET):
                Mantencion.objects.create(vehiculo=vehiculo, **item)
            return redirect("/?screen=vehiculo")
    else:
        form = VehiculoForm(initial={"rendimiento_kml": estimar_rendimiento("Gasolina")})

    contexto = build_context("agregar_vehiculo", {"form": form})
    return render(request, "superapp/base.html", contexto)


def calcular_viaje(request):
    """LÓGICA DE NEGOCIO EN EL BACKEND (Modo Viaje Largo).
    Usa el rendimiento real del vehículo guardado en la BD para estimar
    combustible y costo, y devuelve las Copec recomendadas en ruta."""
    destino_id = request.GET.get("destino")
    vehiculo = Vehiculo.objects.first()
    destino = Destino.objects.filter(pk=destino_id).first()
    if not (vehiculo and destino):
        return JsonResponse({"error": "Datos no disponibles"}, status=400)

    precio_litro = 1149  # 93 oct; en producción vendría de Estacion
    km = destino.distancia_km
    litros = km / vehiculo.rendimiento_kml
    costo = round(litros * precio_litro / 1000) * 1000  # redondeo a mil

    estaciones = [
        {"km": f"{e.km_punto} km", "nombre": e.nombre, "servicios": e.servicios}
        for e in destino.estaciones_ruta.all()
    ]
    return JsonResponse({
        "km": f"{clp(km)} km",
        "litros": f"{round(litros)} L",
        "costo": "$" + clp(costo),
        "tip": (f"Calculado con tu rendimiento real de <b>{dec1(vehiculo.rendimiento_kml)} km/L</b> "
                f"({vehiculo.modelo} {vehiculo.motor}). Necesitas ≈ <b>{round(litros)} L</b> de 93 oct."),
        "estaciones": estaciones,
    })
