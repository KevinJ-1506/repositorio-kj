# bodega/urls.py
from django.urls import path
from . import views

urlpatterns = [
     path('', views.menu_principal, name='menu_principal'),
    path('bodega/', views.bodega_index, name='bodega_index'),
    #path('bodega/productos/', views.gestion_productos, name='gestion_productos'),
    path('bodega/clientes/', views.gestion_clientes, name='gestion_clientes'),
    path('bodega/distribuidores/', views.gestion_distribuidores, name='gestion_distribuidores'),
    path('bodega/marcas/', views.gestion_marcas, name='gestion_marcas'),  # Nueva
    path('bodega/marcas/editar/<int:marca_id>/', views.editar_marca, name='editar_marca'),  # Nueva
    path('bodega/marcas/eliminar/<int:marca_id>/', views.eliminar_marca, name='eliminar_marca'),  # Nueva
    path('bodega/leer-rfid/', views.leer_rfid, name='leer_rfid'),
    path('bodega/leer-multiple-rfid/', views.leer_multiple_rfid, name='leer_multiple_rfid'),
    path('bodega/detectar-puertos/', views.detectar_puertos_seriales, name='detectar_puertos'),

    path('gestion-productos/', views.gestion_productos, name='gestion_productos'),
    path('editar-producto/<int:producto_id>/', views.editar_producto, name='editar_producto'),
    path('eliminar-producto/<int:producto_id>/', views.eliminar_producto, name='eliminar_producto'),
    
]
