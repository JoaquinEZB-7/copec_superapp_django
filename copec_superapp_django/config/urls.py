from django.contrib import admin
from django.urls import path
from superapp import views
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('agregar-vehiculo/', views.agregar_vehiculo, name='agregar_vehiculo'),
    path('api/viaje/', views.calcular_viaje, name='calcular_viaje'),
]
