from django.db import models
from bodega.models import Producto, Cliente

class Venta(models.Model):
    ESTADO_CHOICES = [
        ('PENDIENTE', 'Pendiente'),
        ('COMPLETADA', 'Completada'),
        ('CANCELADA', 'Cancelada'),
    ]
    
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha_venta = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='COMPLETADA')
    nit_factura = models.CharField(max_length=20, blank=True, null=True)
    
    def __str__(self):
        return f"Venta {self.id} - {self.cliente.nombre} - Q{self.total}"

class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE, related_name='detalles')
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
    cantidad = models.IntegerField(default=1)
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return f"{self.producto.nombre} x{self.cantidad} - Q{self.subtotal}"

    def save(self, *args, **kwargs):
        self.subtotal = self.precio_unitario * self.cantidad
        super().save(*args, **kwargs)