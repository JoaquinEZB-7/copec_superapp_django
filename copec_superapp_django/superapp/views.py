from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Avg, Sum
from django.db.models.functions import TruncMonth
from .models import (PerfilUsuario, Vehiculo, Mantencion, Estacion,
                     Destino, Promocion, Mision)
from .utils import clp, dec1


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


def home(request):
    """Renderiza la super app con todos los datos reales desde la base de datos."""
    perfil = PerfilUsuario.objects.first()
    vehiculo = Vehiculo.objects.first()
    servicios_app = [
        {"clave": "combustible", "nombre": "Combustible", "icono": "blue", "piso_destino": "mapa", "sugerido": False},
        {"clave": "vehiculo", "nombre": "Mi Vehículo", "icono": "green", "piso_destino": "vehiculo", "sugerido": False},
        {"clave": "mantencion", "nombre": "Mantención", "icono": "orange", "piso_destino": "mantencion", "sugerido": False},
        {"clave": "market", "nombre": "Pronto Market", "icono": "orange", "piso_destino": "market", "sugerido": False},
        {"clave": "full", "nombre": "Beneficios Full", "icono": "amber", "piso_destino": "full", "sugerido": False},
    ]
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
    contexto = {
        "perfil": perfil,
        "vehiculo": vehiculo,
        "mantenciones": Mantencion.objects.filter(vehiculo=vehiculo) if vehiculo else [],
        "estaciones": Estacion.objects.all(),
        "destinos": Destino.objects.all(),
        "promociones": Promocion.objects.all(),
        "misiones": Mision.objects.all(),
        "transacciones_recientes": perfil.transacciones.all()[:5] if perfil else [],
        "notificaciones_recientes": perfil.notificaciones.all()[:5] if perfil else [],
        "cupo_sugerido": cupo_sugerido if perfil else 0,
        "cupo_sugerido_fmt": "$" + clp(cupo_sugerido) if perfil else "$0",
        "servicios_app": servicios_app,
        "recomendaciones": recomendaciones,
    }
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
