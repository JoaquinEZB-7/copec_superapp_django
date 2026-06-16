from django import forms

from .models import Vehiculo, TIPOS_CARROCERIA, MOTORES, COMBUSTIBLES


MARCAS = [
    ("Toyota", "Toyota"),
    ("Chevrolet", "Chevrolet"),
    ("Hyundai", "Hyundai"),
    ("Kia", "Kia"),
    ("Nissan", "Nissan"),
    ("Suzuki", "Suzuki"),
    ("Mazda", "Mazda"),
    ("Volkswagen", "Volkswagen"),
    ("Peugeot", "Peugeot"),
]

ANIOS = [(anio, str(anio)) for anio in range(2026, 2014, -1)]

ESTILO_CAMPO = "width:100%;border:1px solid var(--line);border-radius:14px;padding:12px 14px;font:600 14px 'Hanken Grotesk';color:var(--ink);background:#fff;outline:none"


def estimar_rendimiento(combustible):
    return {
        "Gasolina": 13.0,
        "Diésel": 16.0,
        "Híbrido": 22.0,
        "Eléctrico": 0.0,
    }.get(combustible, 13.0)


class VehiculoForm(forms.ModelForm):
    marca = forms.ChoiceField(choices=MARCAS)
    anio = forms.TypedChoiceField(choices=ANIOS, coerce=int)
    rendimiento_kml = forms.DecimalField(
        label="Rendimiento (km/L)",
        required=False,
        max_digits=5,
        decimal_places=1,
        widget=forms.NumberInput(attrs={"step": "0.1", "min": "0", "placeholder": "Se estima automáticamente"}),
        help_text="Si lo dejas vacío, se estima según el combustible.",
    )

    class Meta:
        model = Vehiculo
        fields = ["modelo", "anio", "tipo_carroceria", "motor", "combustible", "patente", "kilometraje", "rendimiento_kml"]
        widgets = {
            "modelo": forms.TextInput(attrs={"placeholder": "RAV4", "style": ESTILO_CAMPO}),
            "anio": forms.NumberInput(attrs={"min": 1990, "max": 2035, "style": ESTILO_CAMPO}),
            "patente": forms.TextInput(attrs={"placeholder": "ABCD12", "style": ESTILO_CAMPO}),
            "kilometraje": forms.NumberInput(attrs={"min": 0, "style": ESTILO_CAMPO}),
            "rendimiento_kml": forms.NumberInput(attrs={"step": "0.1", "min": "0", "style": ESTILO_CAMPO}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name in ["marca", "anio", "tipo_carroceria", "motor", "combustible"]:
            self.fields[field_name].widget.attrs.setdefault("style", ESTILO_CAMPO)
        self.fields["rendimiento_kml"].widget.attrs.setdefault("placeholder", "Se estima automáticamente")
        self.fields["rendimiento_kml"].help_text = "Si lo dejas vacío, se estima según el combustible."

    def clean_patente(self):
        return self.cleaned_data["patente"].strip().upper()
