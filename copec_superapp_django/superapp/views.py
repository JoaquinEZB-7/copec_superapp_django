import random
import re
import time
import unicodedata

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Avg, Sum
from django.db.models.functions import TruncMonth
from .models import (PerfilUsuario, Vehiculo, Mantencion, Estacion,
                     Destino, Promocion, Mision)
from .forms import VehiculoForm, estimar_rendimiento
from .utils import clp, dec1

# km_offset = km antes del kilometraje actual en que se hizo la mantención
HISTORIALES_PRESET = [
    [   # Conductor urbano — aceite reciente, neumáticos algo pendientes
        {"tipo": "Cambio de aceite", "detalle": "Mobil 1 5W-30 sintético", "color": "blue", "orden": 1, "km_offset": 1260},
        {"tipo": "Revisión neumáticos", "detalle": "Presión y desgaste", "color": "green", "orden": 2, "km_offset": 4800},
        {"tipo": "Lavado completo", "detalle": "Interior y exterior", "color": "navy", "orden": 3, "km_offset": 8200},
        {"tipo": "Filtro de aire", "detalle": "Reemplazo estándar", "color": "orange", "orden": 4, "km_offset": 13400},
    ],
    [   # Conductor de ruta — servicio grande reciente, todo al día
        {"tipo": "Revisión 40.000 km", "detalle": "Completa en taller Copec", "color": "blue", "orden": 1, "km_offset": 2760},
        {"tipo": "Cambio de neumáticos", "detalle": "4× Bridgestone 225/65 R17", "color": "orange", "orden": 2, "km_offset": 5200},
        {"tipo": "Filtro de combustible", "detalle": "Reemplazo", "color": "green", "orden": 3, "km_offset": 8400},
        {"tipo": "Alineación y balanceo", "detalle": "Ajuste completo", "color": "navy", "orden": 4, "km_offset": 13200},
    ],
    [   # Historial extenso — frenos y batería recientes
        {"tipo": "Pastillas de freno", "detalle": "Eje delantero", "color": "orange", "orden": 1, "km_offset": 1760},
        {"tipo": "Batería", "detalle": "Reemplazo Bosch 60 Ah", "color": "blue", "orden": 2, "km_offset": 3800},
        {"tipo": "Cambio de aceite", "detalle": "Shell Helix 10W-40", "color": "navy", "orden": 3, "km_offset": 7800},
        {"tipo": "Revisión suspensión", "detalle": "Amortiguadores delanteros", "color": "green", "orden": 4, "km_offset": 15200},
    ],
    [   # Dueño cuidadoso — auto más nuevo, primera revisión reciente
        {"tipo": "Primera revisión", "detalle": "Revisión técnica completa", "color": "green", "orden": 1, "km_offset": 760},
        {"tipo": "Cambio de aceite", "detalle": "Castrol Edge 5W-30", "color": "blue", "orden": 2, "km_offset": 760},
        {"tipo": "Inspección técnica", "detalle": "CITV aprobada", "color": "navy", "orden": 3, "km_offset": 3800},
        {"tipo": "Detailing completo", "detalle": "Nano cerámica exterior", "color": "orange", "orden": 4, "km_offset": 7200},
    ],
]

# Orden importa: claves específicas antes que genéricas ("revision" al final)
_INTERVALOS = [
    ("neumatico",  {"km": 30000, "desc": "cada 30.000 km"}),
    ("pastilla",   {"km": 30000, "desc": "cada 30.000 km"}),
    ("suspension", {"km": 50000, "desc": "cada 50.000 km"}),
    ("alineacion", {"km": 10000, "desc": "cada 10.000 km"}),
    ("balanceo",   {"km": 10000, "desc": "cada 10.000 km"}),
    ("bateria",    {"km": 60000, "desc": "cada 60.000 km"}),
    ("inspeccion", {"km": 15000, "desc": "anual (~15.000 km)"}),
    ("detailing",  {"km": 20000, "desc": "cada 20.000 km"}),
    ("lavado",     {"km": 5000,  "desc": "cada 5.000 km"}),
    ("filtro",     {"km": 15000, "desc": "cada 15.000 km"}),
    ("freno",      {"km": 30000, "desc": "cada 30.000 km"}),
    ("aceite",     {"km": 10000, "desc": "cada 10.000 km"}),
    ("primera",    {"km": 10000, "desc": "próxima a los 20.000 km"}),
    ("revision",   {"km": 15000, "desc": "anual (~15.000 km)"}),
]


def _sin_tildes(s):
    return unicodedata.normalize("NFD", s).encode("ascii", "ignore").decode("ascii").lower()


def _extraer_km(m):
    if m.km_realizado > 0:
        return m.km_realizado
    match = re.search(r'(\d{2,3})[.,](\d{3})\s*km', m.detalle)
    return int(match.group(1) + match.group(2)) if match else 0


def calcular_alertas_vehiculo(vehiculo, mantenciones, estacion_cercana):
    km = vehiculo.kilometraje
    alertas = []
    for m in mantenciones:
        km_hecho = _extraer_km(m)
        if not km_hecho:
            continue
        tipo_norm = _sin_tildes(m.tipo)
        intervalo = next((d for c, d in _INTERVALOS if c in tipo_norm), None)
        if not intervalo:
            continue
        km_desde = km - km_hecho
        km_siguiente = km_hecho + intervalo["km"]
        km_falta = km_siguiente - km
        if km_falta <= 0:
            estado, color_estado = "vencido", "#e03131"
        elif km_falta <= 2000:
            estado, color_estado = "urgente", "var(--orange)"
        elif km_falta <= 5000:
            estado, color_estado = "pronto", "var(--amber)"
        else:
            estado, color_estado = "ok", "var(--green)"
        alertas.append({
            "tipo": m.tipo,
            "detalle": m.detalle,
            "color": m.color,
            "km_desde": clp(abs(km_desde)),
            "km_siguiente_fmt": clp(km_siguiente),
            "km_falta": clp(abs(km_falta)),
            "estado": estado,
            "color_estado": color_estado,
            "desc": intervalo["desc"],
            "estacion": estacion_cercana,
            "vencido": km_falta <= 0,
            "mostrar_copec": estado in ("urgente", "vencido"),
        })
    prioridad = {"vencido": 0, "urgente": 1, "pronto": 2, "ok": 3}
    alertas.sort(key=lambda a: prioridad[a["estado"]])
    return alertas


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

    mantenciones = list(Mantencion.objects.filter(vehiculo=vehiculo)) if vehiculo else []
    estacion_cercana = estaciones[0] if estaciones else None
    alertas_vehiculo = calcular_alertas_vehiculo(vehiculo, mantenciones, estacion_cercana) if vehiculo else []

    contexto = {
        "perfil": perfil,
        "vehiculo": vehiculo,
        "mantenciones": mantenciones,
        "alertas_vehiculo": alertas_vehiculo,
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
            km_actual = vehiculo.kilometraje
            preset = random.choice(HISTORIALES_PRESET)
            max_offset = max(p["km_offset"] for p in preset)
            escala = min(1.0, km_actual / (max_offset + 1000)) if max_offset else 1.0
            for item in preset:
                item_copy = dict(item)
                km_offset = item_copy.pop("km_offset")
                item_copy["km_realizado"] = max(200, km_actual - int(km_offset * escala))
                Mantencion.objects.create(vehiculo=vehiculo, **item_copy)
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
