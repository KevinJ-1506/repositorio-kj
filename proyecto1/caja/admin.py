from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Venta, DetalleVenta

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ['id', 'cliente', 'fecha_venta', 'total', 'estado']
    list_filter = ['fecha_venta', 'estado']
    search_fields = ['cliente__nombre', 'nit_factura']

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ['venta', 'producto', 'cantidad', 'precio_unitario', 'subtotal']
    list_filter = ['venta__fecha_venta']