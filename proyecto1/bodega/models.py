from django.db import models

class Marca(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Distribuidor(models.Model):
    nombre = models.CharField(max_length=200)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    nit = models.CharField(max_length=20, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Cliente(models.Model):
    nit = models.CharField(max_length=20, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=100)
    direccion = models.TextField(blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    tarjeta_credito = models.CharField(max_length=100, blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

class Producto(models.Model):
    epc = models.CharField(max_length=24, unique=True)
    codigo_barras = models.CharField(max_length=50, unique=True, blank=True, null=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    marca = models.ForeignKey(Marca, on_delete=models.SET_NULL, blank=True, null=True)
    distribuidor = models.ForeignKey(Distribuidor, on_delete=models.SET_NULL, blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    fecha_ingreso = models.DateTimeField(auto_now_add=True)
    peso = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    precio_compra = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    precio_venta = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)
    ubicacion = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class LecturaRFID(models.Model):
    TIPO_LECTURA_CHOICES = [
        ('INGRESO', 'Ingreso'),
        ('SALIDA', 'Salida'),
        ('INVENTARIO', 'Inventario'),
        ('CONTEO', 'Conteo'),
    ]
    epc = models.CharField(max_length=24)
    producto = models.ForeignKey(Producto, on_delete=models.SET_NULL, blank=True, null=True)
    ubicacion = models.CharField(max_length=100)
    tipo_lectura = models.CharField(max_length=50, choices=TIPO_LECTURA_CHOICES)
    fecha_lectura = models.DateTimeField(auto_now_add=True)
    lecturador_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.epc} - {self.tipo_lectura}"