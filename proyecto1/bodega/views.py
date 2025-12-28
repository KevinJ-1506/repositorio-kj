from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from .models import Producto, Cliente, Distribuidor, Marca, LecturaRFID
from .forms import ProductoForm, ClienteForm, DistribuidorForm, MarcaForm
import serial
import time
import serial.tools.list_ports
import re
from django.contrib import messages



def menu_principal(request):
    return render(request, 'menu_principal.html')

def bodega_index(request):
    return render(request, 'bodega/index.html')

def gestion_productos(request):
    productos = Producto.objects.all().order_by('-fecha_ingreso')
    marcas = Marca.objects.all().order_by('nombre')
    distribuidores = Distribuidor.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        form = ProductoForm(request.POST)
        if form.is_valid():
            try:
                producto = form.save()
                messages.success(request, f'Producto "{producto.nombre}" guardado correctamente.')
                return redirect('gestion_productos')
            except Exception as e:
                messages.error(request, f'Error al guardar el producto: {str(e)}')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario.')
    else:
        form = ProductoForm()
    
    return render(request, 'bodega/productos.html', {
        'productos': productos,
        'form': form,
        'marcas': marcas,
        'distribuidores': distribuidores
    })


def editar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    marcas = Marca.objects.all()
    distribuidores = Distribuidor.objects.all()
    
    if request.method == 'POST':
        form = ProductoForm(request.POST, instance=producto)
        if form.is_valid():
            producto_editado = form.save()
            messages.success(request, f'Producto "{producto_editado.nombre}" actualizado exitosamente')
            return redirect('gestion_productos')
        else:
            messages.error(request, 'Por favor corrige los errores en el formulario')
    else:
        form = ProductoForm(instance=producto)
    
    context = {
        'producto': producto,
        'marcas': marcas,
        'distribuidores': distribuidores,
        'form': form
    }
    return render(request, 'bodega/editar_producto.html', context)

def eliminar_producto(request, producto_id):
    producto = get_object_or_404(Producto, id=producto_id)
    
    if request.method == 'POST':
        nombre_producto = producto.nombre
        producto.delete()
        messages.success(request, f'Producto "{nombre_producto}" eliminado exitosamente')
        return redirect('gestion_productos')
    
    # Si no es POST, redirigir a la edición
    return redirect('editar_producto', producto_id=producto_id)
########################################
def gestion_clientes(request):
    clientes = Cliente.objects.all()
    
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_clientes')
    else:
        form = ClienteForm()
    
    return render(request, 'bodega/clientes.html', {
        'clientes': clientes,
        'form': form
    })

def gestion_distribuidores(request):
    distribuidores = Distribuidor.objects.all()
    
    if request.method == 'POST':
        form = DistribuidorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_distribuidores')
    else:
        form = DistribuidorForm()
    
    return render(request, 'bodega/distribuidores.html', {
        'distribuidores': distribuidores,
        'form': form
    })


###############################################
def procesar_respuesta_lector(respuesta):
    """
    Procesa la respuesta del lector RFID que tiene formato:
    🏷️ Etiquetas detectadas:
      1. E280689400005031A1C90D86
      2. AABB0000C209870000000000
    ✅ Total de etiquetas únicas: 2
    """
    epcs = []
    
    # Buscar líneas que contengan EPCs (números seguidos de punto y luego el código)
    lineas = respuesta.split('\n')
    
    for linea in lineas:
        # Buscar patrones como "1. E280689400005031A1C90D86"
        patron_epc = r'\d+\.\s*([0-9A-Fa-f]{24})'
        coincidencias = re.findall(patron_epc, linea)
        
        if coincidencias:
            epcs.extend([epc.upper() for epc in coincidencias])
    
    # Si no encontramos con el primer patrón, buscar cualquier EPC de 24 caracteres hex
    if not epcs:
        patron_directo = r'[0-9A-Fa-f]{24}'
        epcs = re.findall(patron_directo, respuesta)
        epcs = [epc.upper() for epc in epcs]
    
    # Eliminar duplicados manteniendo el orden
    epcs_unicos = []
    for epc in epcs:
        if epc not in epcs_unicos:
            epcs_unicos.append(epc)
    
    return epcs_unicos

def leer_rfid(request):
    """Función para leer etiquetas RFID desde el lector"""
    if request.method == 'POST':
        try:
            # Obtener puerto desde el request o usar default
            puerto = request.POST.get('puerto', 'COM3')
            baudrate = 115200
            timeout = 10
            
            # Abrir conexión serial
            ser = serial.Serial(
                port=puerto,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=timeout
            )
            
            # Limpiar buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Enviar comando 'R' para leer
            comando = 'R\n'  # Tu lector parece usar este formato
            ser.write(comando.encode('utf-8'))
            
            # Esperar y leer toda la respuesta
            time.sleep(5)  # Dar tiempo para que el lector responda
            
            respuesta_completa = ""
            while ser.in_waiting > 0:
                linea = ser.readline().decode('utf-8', errors='ignore')
                respuesta_completa += linea + "\n"
                # Si detectamos el marcador de fin, salir
                if "Total de etiquetas únicas:" in linea:
                    break
            
            ser.close()
            
            # Procesar la respuesta para extraer EPCs
            epcs = procesar_respuesta_lector(respuesta_completa)
            
            if epcs:
                # Para lectura simple, tomar el primer EPC
                epc_principal = epcs[0]
                
                # Verificar si el producto ya existe
                from .models import Producto
                producto_existente = Producto.objects.filter(epc=epc_principal).first()
                
                return JsonResponse({
                    'success': True,
                    'epc': epc_principal,
                    'epcs_todos': epcs,  # Para debugging
                    'total_etiquetas': len(epcs),
                    'respuesta_cruda': respuesta_completa,  # Para debugging
                    'existe': producto_existente is not None,
                    'producto': {
                        'nombre': producto_existente.nombre if producto_existente else None,
                        'id': producto_existente.id if producto_existente else None
                    }
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'error': 'No se detectaron etiquetas en la respuesta',
                    'respuesta_cruda': respuesta_completa,
                    'sugerencia': 'Verifique que las etiquetas estén en el área de lectura'
                })
                
        except serial.SerialException as e:
            return JsonResponse({
                'success': False, 
                'error': f'Error de conexión serial: {str(e)}',
                'sugerencia': f'Verifica que el puerto {puerto} exista y no esté en uso'
            })
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': f'Error inesperado: {str(e)}'
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def leer_multiple_rfid(request):
    """Función para leer múltiples etiquetas RFID"""
    if request.method == 'POST':
        try:
            puerto = request.POST.get('puerto', 'COM3')
            cantidad_deseada = int(request.POST.get('cantidad', 1))
            
            baudrate = 115200
            timeout = 10
            
            # Abrir conexión serial
            ser = serial.Serial(
                port=puerto,
                baudrate=baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=timeout
            )
            
            # Limpiar buffers
            ser.reset_input_buffer()
            ser.reset_output_buffer()
            
            # Enviar comando 'R' para leer
            comando = 'R\n'
            ser.write(comando.encode('utf-8'))
            
            # Esperar y leer toda la respuesta
            time.sleep(5)
            
            respuesta_completa = ""
            while ser.in_waiting > 0:
                linea = ser.readline().decode('utf-8', errors='ignore')
                respuesta_completa += linea + "\n"
                if "Total de etiquetas únicas:" in linea:
                    break
            
            ser.close()
            
            # Procesar la respuesta para extraer EPCs
            epcs = procesar_respuesta_lector(respuesta_completa)
            
            if epcs:
                # Limitar a la cantidad deseada
                epcs_limite = epcs[:cantidad_deseada]
                
                return JsonResponse({
                    'success': True,
                    'epcs': epcs_limite,
                    'total': len(epcs_limite),
                    'total_detectadas': len(epcs),
                    'respuesta_cruda': respuesta_completa
                })
            else:
                return JsonResponse({
                    'success': False, 
                    'error': 'No se detectaron etiquetas',
                    'respuesta_cruda': respuesta_completa
                })
                
        except Exception as e:
            return JsonResponse({
                'success': False, 
                'error': str(e)
            })
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def detectar_puertos_seriales(request):
    """Función para detectar puertos seriales disponibles"""
    puertos = []
    try:
        puertos_disponibles = serial.tools.list_ports.comports()
        for puerto in puertos_disponibles:
            puertos.append({
                'dispositivo': puerto.device,
                'descripcion': puerto.description,
                'hwid': puerto.hwid,
                'vid': puerto.vid if puerto.vid else 'N/A',
                'pid': puerto.pid if puerto.pid else 'N/A'
            })
        
        return JsonResponse({
            'success': True,
            'puertos': puertos
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        })
    
    # bodega/views.py - Agregar estas funciones

def gestion_marcas(request):
    """Vista para gestionar marcas"""
    marcas = Marca.objects.all().order_by('nombre')
    
    if request.method == 'POST':
        form = MarcaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_marcas')
    else:
        form = MarcaForm()
    
    return render(request, 'bodega/marcas.html', {
        'marcas': marcas,
        'form': form
    })

def editar_marca(request, marca_id):
    """Vista para editar una marca via AJAX"""
    if request.method == 'POST':
        try:
            import json
            data = json.loads(request.body)
            marca = Marca.objects.get(id=marca_id)
            marca.nombre = data.get('nombre')
            marca.descripcion = data.get('descripcion', '')
            marca.save()
            
            return JsonResponse({'success': True})
        except Marca.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Marca no encontrada'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})

def eliminar_marca(request, marca_id):
    """Vista para eliminar una marca via AJAX"""
    if request.method == 'POST':
        try:
            marca = Marca.objects.get(id=marca_id)
            # Verificar si hay productos usando esta marca
            from .models import Producto
            productos_con_marca = Producto.objects.filter(marca=marca).count()
            
            if productos_con_marca > 0:
                return JsonResponse({
                    'success': False, 
                    'error': f'No se puede eliminar. Hay {productos_con_marca} producto(s) usando esta marca.'
                })
            
            marca.delete()
            return JsonResponse({'success': True})
        except Marca.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Marca no encontrada'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Método no permitido'})