from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Venta, DetalleVenta
from bodega.models import Producto, Cliente

def escanear_productos(request):
    return render(request, 'caja/escanear.html')

def index(request):
    """Vista principal del módulo de caja"""
    return render(request, 'caja/index.html')

def punto_venta_autoservicio(request):
    """Vista para el punto de venta de autoservicio"""
    return render(request, 'caja/caja.html')


@method_decorator(csrf_exempt, name='dispatch')
class RegistrarVentaView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            print("Datos recibidos:", data)  # Para debug
            
            # Obtener o crear cliente
            nit = data['cliente']['nit']
            nombre = data['cliente']['nombre']
            direccion = data['cliente']['direccion']
            email = data['cliente'].get('email', '')
            
            cliente, created = Cliente.objects.get_or_create(
                nit=nit,
                defaults={
                    'nombre': nombre,
                    'direccion': direccion,
                    'email': email
                }
            )
            
            # Si el cliente ya existe, actualizar datos si es necesario
            if not created:
                cliente.nombre = nombre
                cliente.direccion = direccion
                if email:
                    cliente.email = email
                cliente.save()
            
            # Crear venta
            venta = Venta.objects.create(
                cliente=cliente,
                subtotal=data['subtotal'],
                iva=data['iva'],
                total=data['total'],
                nit_factura=nit
            )
            
            # Crear detalles de venta
            for producto_data in data['productos']:
                try:
                    producto = Producto.objects.get(id=producto_data['id'])
                    
                    DetalleVenta.objects.create(
                        venta=venta,
                        producto=producto,
                        cantidad=producto_data['cantidad'],
                        precio_unitario=producto_data['precio']
                    )
                    
                    # Actualizar stock del producto
                    producto.stock -= producto_data['cantidad']
                    producto.save()
                    
                except Producto.DoesNotExist:
                    print(f"Producto con id {producto_data['id']} no encontrado")
                    continue
            
            return JsonResponse({
                'success': True, 
                'venta_id': venta.id,
                'mensaje': 'Venta registrada exitosamente'
            })
            
        except Exception as e:
            print("Error al registrar venta:", str(e))
            return JsonResponse({
                'success': False, 
                'error': str(e)
            }, status=400)

def ventas_lista(request):
    """Vista para listar ventas (opcional, para administración)"""
    ventas = Venta.objects.all().order_by('-fecha_venta')
    return render(request, 'caja/lista_ventas.html', {'ventas': ventas})