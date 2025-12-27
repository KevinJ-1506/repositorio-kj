# caja/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('escanear/', views.escanear_productos, name='escanear_productos'),
    path('', views.index, name='caja_index'),
    path('autoservicio/', views.punto_venta_autoservicio, name='punto_venta_autoservicio'),  # Corrige "names" por "name"
    #path('', views.index_caja, name='index_caja'),
    path('registrar_venta/', views.RegistrarVentaView.as_view(), name='registrar_venta'),
    path('ventas/', views.ventas_lista, name='lista_ventas'),
]