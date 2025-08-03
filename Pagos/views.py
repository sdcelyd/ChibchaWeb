from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
import re
from .models import Direccion, TarjetaCredito, Pais
from Clientes.models import Cliente
from .validators import validar_tarjeta, VALIDADORES_DIRECCIONES
from ChibchaWeb.decorators import cliente_required


@cliente_required
def registrar_direccion(request):
    cliente = request.cliente  # Disponible automáticamente
    
    if request.method == 'POST':
        ubicacion = request.POST.get('ubicacion')
        codigo_postal = request.POST.get('codigoPostal')
        pais_id = request.POST.get('pais')
        
        if ubicacion and codigo_postal and pais_id:
            try:
                pais = get_object_or_404(Pais, paisId=pais_id)
                
                # Validar la dirección según el país
                validador = VALIDADORES_DIRECCIONES.get(pais.nombre.lower())
                if validador:
                    try:
                        validador(ubicacion)
                    except ValidationError as e:
                        messages.error(request, str(e))
                        paises = Pais.objects.all()
                        return render(request, 'pagos/registrar_direccion.html', {'paises': paises})
                
                direccion = Direccion.objects.create(
                    ubicacion=ubicacion,
                    codigoPostal=codigo_postal,
                    pais=pais,
                    cliente=cliente
                )
                messages.success(request, "Dirección registrada exitosamente.")
                return redirect('clientes:detalle_cliente')
            except Exception as e:
                messages.error(request, f"Error al registrar la dirección: {str(e)}")
        else:
            messages.error(request, "Por favor completa todos los campos requeridos.")
    
    paises = Pais.objects.all()
    return render(request, 'pagos/registrar_direccion.html', {'paises': paises})


@cliente_required
def registrar_tarjeta(request):
    cliente = request.cliente  # Disponible automáticamente
    
    if request.method == 'POST':
        numero = request.POST.get('numero', '').replace(' ', '')  # Remover espacios
        nombre_titular = request.POST.get('nombre_titular')
        fecha_expiracion = request.POST.get('fecha_expiracion')
        cvv = request.POST.get('cvv')
        
        if numero and nombre_titular and fecha_expiracion and cvv:
            try:
                # Validar el número de tarjeta usando el validador
                validar_tarjeta(numero)
                
                # Validar formato de fecha (MM/AA)
                if not re.match(r'^\d{2}/\d{2}$', fecha_expiracion):
                    messages.error(request, "El formato de fecha debe ser MM/AA")
                    return render(request, 'pagos/registrar_tarjeta.html')
                
                # Validar CVV (3 o 4 dígitos)
                if not re.match(r'^\d{3,4}$', cvv):
                    messages.error(request, "El CVV debe tener 3 o 4 dígitos")
                    return render(request, 'pagos/registrar_tarjeta.html')
                
                tarjeta = TarjetaCredito.objects.create(
                    numero=numero,
                    nombre_titular=nombre_titular.upper(),
                    fecha_expiracion=fecha_expiracion,
                    cvv=cvv,
                    cliente=cliente
                )
                
                # Actualizar que el cliente tiene método de pago
                cliente.metodoPago = True
                cliente.save()
                
                messages.success(request, "Tarjeta de crédito registrada exitosamente.")
                return redirect('clientes:detalle_cliente')
            except ValidationError as e:
                messages.error(request, str(e))
                return render(request, 'pagos/registrar_tarjeta.html')
            except Exception as e:
                messages.error(request, f"Error al registrar la tarjeta: {str(e)}")
        else:
            messages.error(request, "Por favor completa todos los campos requeridos.")
    
    return render(request, 'pagos/registrar_tarjeta.html')


@cliente_required
def eliminar_direccion(request, direccion_id):
    try:
        cliente = request.cliente
        direccion = get_object_or_404(Direccion, direccionId=direccion_id, cliente=cliente)
        direccion.delete()
        messages.success(request, "Dirección eliminada exitosamente.")
    except Exception as e:
        messages.error(request, f"Error al eliminar la dirección: {str(e)}")
    
    return redirect('clientes:detalle_cliente')


@cliente_required
def eliminar_tarjeta(request, tarjeta_id):
    try:
        cliente = request.cliente
        tarjeta = get_object_or_404(TarjetaCredito, id=tarjeta_id, cliente=cliente)
        tarjeta.delete()
        
        # Verificar si quedan tarjetas
        if not cliente.tarjetas.exists():
            cliente.metodoPago = False
            cliente.save()
        
        messages.success(request, "Tarjeta eliminada exitosamente.")
    except Exception as e:
        messages.error(request, f"Error al eliminar la tarjeta: {str(e)}")
    
    return redirect('clientes:detalle_cliente')
