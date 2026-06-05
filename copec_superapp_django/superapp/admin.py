from django.contrib import admin
from . import models

@admin.register(models.PerfilUsuario)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ("nombre", "saldo_copec_pay", "puntos_full", "cupo_combustible", "nivel")


@admin.register(models.Transaccion)
class TransaccionAdmin(admin.ModelAdmin):
    list_display = ("fecha", "perfil", "tipo", "descripcion", "monto", "puntos_ganados")
    list_filter = ("tipo", "fecha")
    search_fields = ("descripcion", "perfil__nombre")


@admin.register(models.Notificacion)
class NotificacionAdmin(admin.ModelAdmin):
    list_display = ("fecha", "perfil", "tipo", "titulo", "leida")
    list_filter = ("tipo", "leida", "fecha")
    search_fields = ("titulo", "detalle", "perfil__nombre")

class MantencionInline(admin.TabularInline):
    model = models.Mantencion
    extra = 1

@admin.register(models.Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ("marca", "modelo", "anio", "patente", "rendimiento_kml", "kilometraje")
    inlines = [MantencionInline]

@admin.register(models.Estacion)
class EstacionAdmin(admin.ModelAdmin):
    list_display = ("nombre", "precio_93", "distancia_km", "destacada")

class EstacionRutaInline(admin.TabularInline):
    model = models.EstacionRuta
    extra = 1

@admin.register(models.Destino)
class DestinoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "distancia_km")
    inlines = [EstacionRutaInline]

admin.site.register(models.Promocion)
admin.site.register(models.Mision)
admin.site.site_header = "Copec Super App · Administración"
