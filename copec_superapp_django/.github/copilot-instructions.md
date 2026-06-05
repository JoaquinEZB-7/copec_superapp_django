Proyecto Django (app `superapp`) que simula una super app de movilidad de Copec con un modelo de "pisos" tipo Uber. Reglas:

- Todo en español (nombres de modelos, campos, variables y textos de UI).

- La base de datos guarda datos de ejemplo; no hay backend real ni pagos reales, todo es simulado.

- Formatea montos y números con los helpers de `superapp/utils.py`: `clp(n)` para miles ("$48.200") y `dec1(n)` para un decimal con coma ("13,2"). Agrega propiedades `_fmt` en los modelos en lugar de formatear en la plantilla.

- Cada "piso" es una plantilla en `superapp/templates/superapp/screens/` y se incluye desde `base.html`. La navegación entre pisos es client-side con la función `go(id)` de `superapp/static/superapp/js/app.js`. No rompas ese patrón.

- Los datos de demo se cargan con migraciones de datos (ver `0002_seed_demo.py`). Cuando agregues datos de ejemplo, hazlo en una nueva migración de datos con `RunPython`, no a mano.

- Modelos existentes: PerfilUsuario, Vehiculo, Mantencion, Estacion, Destino, EstacionRuta, Promocion, Mision. Vistas: `home` (renderiza `base.html`) y `calcular_viaje` (devuelve JSON). Registra en `admin.py` todo modelo nuevo.
