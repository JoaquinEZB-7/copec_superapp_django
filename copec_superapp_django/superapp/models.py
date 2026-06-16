from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from .utils import clp, dec1


TIPOS_CARROCERIA = [
    ("SUV", "SUV"),
    ("Sedán", "Sedán"),
    ("Hatchback", "Hatchback"),
    ("Camioneta", "Camioneta"),
    ("Station Wagon", "Station Wagon"),
    ("City Car", "City Car"),
]

MOTORES = [("1.2", "1.2"), ("1.4", "1.4"), ("1.6", "1.6"), ("1.7", "1.7"), ("1.8", "1.8"), ("2.0", "2.0"), ("2.5", "2.5")]

COMBUSTIBLES = [("Gasolina", "Gasolina"), ("Diésel", "Diésel"), ("Híbrido", "Híbrido"), ("Eléctrico", "Eléctrico")]


class PerfilUsuario(models.Model):
    nombre = models.CharField(max_length=60, default="Joaquín")
    saldo_copec_pay = models.IntegerField(default=48200)
    puntos_full = models.IntegerField(default=12540)
    cupo_combustible = models.IntegerField(default=90000)
    nivel = models.CharField(max_length=30, default="Full Oro")

    class Meta:
        verbose_name = "Perfil de usuario"
        verbose_name_plural = "Perfiles de usuario"

    def __str__(self): return self.nombre
    @property
    def saldo_fmt(self): return "$" + clp(self.saldo_copec_pay)
    @property
    def puntos_fmt(self): return clp(self.puntos_full)
    @property
    def canje_fmt(self): return "$" + clp(self.puntos_full / 2)
    @property
    def cupo_fmt(self): return "$" + clp(self.cupo_combustible)

    def recalcular_saldo_y_puntos(self):
        totales = self.transacciones.aggregate(
            saldo=models.Sum("monto"),
            puntos=models.Sum("puntos_ganados"),
        )
        self.saldo_copec_pay = totales["saldo"] or 0
        self.puntos_full = totales["puntos"] or 0
        self.save(update_fields=["saldo_copec_pay", "puntos_full"])
        return self.saldo_copec_pay, self.puntos_full


class Transaccion(models.Model):
    TIPOS = [
        ("carga", "Carga"),
        ("pronto", "Pronto"),
        ("lavado", "Lavado"),
        ("mantencion", "Mantención"),
        ("carga_electrica", "Carga eléctrica"),
    ]

    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="transacciones")
    tipo = models.CharField(max_length=20, choices=TIPOS)
    descripcion = models.CharField(max_length=120)
    monto = models.IntegerField(default=0)
    puntos_ganados = models.IntegerField(default=0)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-id"]

    def __str__(self): return f"{self.get_tipo_display()} · {self.descripcion}"
    @property
    def monto_fmt(self): return ("-$" if self.monto < 0 else "$") + clp(abs(self.monto))


class Notificacion(models.Model):
    TIPOS = [
        ("vehiculo", "Vehículo"),
        ("promo", "Promo"),
        ("mision", "Misión"),
        ("carga", "Carga"),
        ("sistema", "Sistema"),
    ]

    perfil = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="notificaciones")
    tipo = models.CharField(max_length=20, choices=TIPOS)
    titulo = models.CharField(max_length=120)
    detalle = models.CharField(max_length=180)
    icono = models.CharField(max_length=40, blank=True, null=True)
    leida = models.BooleanField(default=False)
    fecha = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "-id"]

    def __str__(self): return f"{self.get_tipo_display()} · {self.titulo}"


class Vehiculo(models.Model):
    propietario = models.ForeignKey(PerfilUsuario, on_delete=models.CASCADE, related_name="vehiculos", null=True, blank=True)
    marca = models.CharField(max_length=40, default="Toyota")
    modelo = models.CharField(max_length=40, default="RAV4")
    anio = models.IntegerField(default=2022)
    tipo_carroceria = models.CharField(max_length=20, choices=TIPOS_CARROCERIA, default="SUV")
    motor = models.CharField(max_length=4, choices=MOTORES, default="2.0")
    traccion = models.CharField(max_length=20, default="4x4")
    combustible = models.CharField(max_length=20, choices=COMBUSTIBLES, default="Gasolina")
    patente = models.CharField(max_length=10, default="KJ·PR·45")
    kilometraje = models.IntegerField(default=42760)
    rendimiento_kml = models.FloatField("Rendimiento (km/L)", default=13.2)
    nivel_combustible = models.IntegerField(default=50, validators=[MinValueValidator(0), MaxValueValidator(100)])
    capacidad_estanque_l = models.IntegerField(default=55)
    aceite_actual = models.CharField(max_length=80, default="Mobil 1 5W-30 sintético (10.02.2025)")
    presion_del = models.IntegerField("Presión delantera (psi)", default=33)
    presion_tra = models.IntegerField("Presión trasera (psi)", default=32)
    km_prox_mantencion = models.IntegerField(default=1240)
    prox_servicio = models.CharField(max_length=60, default="Cambio de aceite")
    medida_neumatico = models.CharField(max_length=20, default="225/65 R17")

    def __str__(self): return f"{self.marca} {self.modelo} {self.anio}"
    @property
    def nombre_completo(self): return f"{self.marca} {self.modelo} {self.anio} · {self.motor}"
    @property
    def ficha(self): return f"{self.marca} · {self.combustible} {self.motor} · {self.traccion}"
    @property
    def rendimiento_fmt(self): return dec1(self.rendimiento_kml)
    @property
    def km_fmt(self): return clp(self.kilometraje)
    @property
    def km_prox_fmt(self): return clp(self.km_prox_mantencion)
    @property
    def autonomia_km(self): return round(self.capacidad_estanque_l * (self.nivel_combustible / 100) * self.rendimiento_kml)
    @property
    def alerta_baja(self): return self.nivel_combustible < 20


class Mantencion(models.Model):
    COLORES = [("orange","Naranjo"),("blue","Azul"),("green","Verde"),("navy","Azul marino")]
    vehiculo = models.ForeignKey(Vehiculo, on_delete=models.CASCADE, related_name="mantenciones")
    tipo = models.CharField(max_length=80)
    detalle = models.CharField(max_length=120)
    color = models.CharField(max_length=10, choices=COLORES, default="blue")
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ["orden"]
        verbose_name_plural = "Mantenciones / historial"

    def __str__(self): return self.tipo


class Estacion(models.Model):
    nombre = models.CharField(max_length=60)
    servicios = models.CharField(max_length=160)
    precio_93 = models.IntegerField(default=1149)
    distancia_km = models.FloatField(default=1.0)
    destacada = models.BooleanField("Mejor precio", default=False)
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ["orden"]

    def __str__(self): return self.nombre
    @property
    def precio_fmt(self): return "$" + clp(self.precio_93)
    @property
    def distancia_fmt(self): return dec1(self.distancia_km)


class Destino(models.Model):
    nombre = models.CharField(max_length=60)
    distancia_km = models.IntegerField()

    def __str__(self): return f"{self.nombre} ({self.distancia_km} km)"


class EstacionRuta(models.Model):
    destino = models.ForeignKey(Destino, on_delete=models.CASCADE, related_name="estaciones_ruta")
    nombre = models.CharField(max_length=60)
    km_punto = models.IntegerField()
    servicios = models.CharField(max_length=120)
    orden = models.IntegerField(default=0)

    class Meta:
        ordering = ["orden"]
        verbose_name_plural = "Estaciones en ruta"

    def __str__(self): return f"{self.nombre} @ {self.km_punto}km"


class Promocion(models.Model):
    titulo = models.CharField(max_length=60)
    detalle = models.CharField(max_length=80)
    puntos = models.IntegerField(default=0)
    def __str__(self): return self.titulo


class Mision(models.Model):
    titulo = models.CharField(max_length=80)
    detalle = models.CharField(max_length=120)
    progreso = models.IntegerField("Progreso (%)", default=0)
    class Meta:
        verbose_name_plural = "Misiones Full"
    def __str__(self): return self.titulo
