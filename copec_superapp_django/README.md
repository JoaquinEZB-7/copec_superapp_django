# Copec · Super App de Movilidad — Prototipo (Django)

Prototipo funcional de la propuesta del **Copec Omnichannel Challenge**: una super app
modelo Uber donde cada servicio es un "piso" independiente (BlueExpress, carga eléctrica,
mantención, Mi Vehículo, Pronto Market, Viaje Largo) dentro de un mismo "edificio" que
comparte perfil, billetera (Copec Pay) y lealtad (Full).

A diferencia de una maqueta estática, **los datos viven en una base de datos** y Django los
inyecta en las plantillas. El cálculo del *Modo Viaje Largo* se hace en el **backend** usando
el rendimiento real del vehículo.

## Requisitos
- Python 3.10 o superior

## Cómo ejecutarlo (Visual Studio Code)

Abre la carpeta del proyecto en VS Code y, en la terminal integrada:

```bash
# 1. Crear y activar un entorno virtual
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # macOS / Linux

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Crear la base de datos y cargar los datos de demo
python manage.py migrate

# 4. Levantar el servidor
python manage.py runserver
```

Abre http://127.0.0.1:8000 en el navegador. Para la presentación, usa la vista
responsive del navegador (F12 → modo móvil) o simplemente muestra el teléfono en pantalla.

> Tip VS Code: instala la extensión **Python** y selecciona el intérprete del `venv`
> (Ctrl+Shift+P → "Python: Select Interpreter").

## Panel de administración (editar datos sin tocar código)

```bash
python manage.py createsuperuser
```

Luego entra a http://127.0.0.1:8000/admin y edita el vehículo, las estaciones, las
promociones, las misiones y los destinos del Viaje Largo.

## Dónde está cada cosa

```
config/              Configuración del proyecto (settings, urls)
superapp/
  models.py          Los datos: Vehiculo, Mantencion, Estacion, Destino, etc.
  views.py           home() renderiza la app · calcular_viaje() = lógica de negocio
  admin.py           Panel para editar datos
  migrations/
    0002_seed_demo   Datos de demostración (se cargan solos con migrate)
  templates/superapp/
    base.html        El "edificio": frame del teléfono + navbar + incluye los pisos
    screens/         Un archivo por "piso" (home, vehiculo, viaje, ...)
  static/superapp/
    css/styles.css   Estilos
    js/app.js        Navegación entre pisos + llamada al cálculo de viaje
```

## El showcase técnico

`superapp/views.py → calcular_viaje()` recibe un destino, lee el rendimiento real del
vehículo desde la base de datos, estima litros y costo, y devuelve las Copec recomendadas
en ruta como JSON. El frontend (Modo Viaje Largo) consume ese endpoint con `fetch`.
Es el mejor punto para mostrar que hay backend de verdad.
