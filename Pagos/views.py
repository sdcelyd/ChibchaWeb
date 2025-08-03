from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
import re
from .models import Direccion, TarjetaCredito, Pais, Pago
from Clientes.models import Cliente
from .validators import validar_tarjeta, VALIDADORES_DIRECCIONES
from ChibchaWeb.planes import PLANES_DISPONIBLES
from datetime import timedelta
from django.utils import timezone
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

@login_required
def seleccionar_plan(request):
    if request.method == "POST":
        plan = request.POST.get("plan")
        modalidad = request.POST.get("modalidad")  # mensual, anual, etc.
        request.session["plan"] = plan
        request.session["modalidad"] = modalidad
        return redirect("pagos:direccion_facturacion")
    return render(request, "Pagos/seleccionar_plan.html", {"planes": PLANES_DISPONIBLES})

@login_required
def direccion_facturacion(request):
    if request.method == "POST":
        ubicacion = request.POST.get("ubicacion")
        codigo_postal = request.POST.get("codigo_postal")
        pais_id = request.POST.get("pais")

        direccion = Direccion.objects.create(
            ubicacion=ubicacion,
            codigoPostal=codigo_postal,
            pais_id=pais_id,
            cliente=request.user.cliente
        )
        request.session["direccion_id"] = direccion.direccionId
        return redirect("pagos:ingresar_tarjeta")

    paises = Pais.objects.all()
    return render(request, "pagos/direccion_facturacion.html", {"paises": paises})

@login_required
def ingresar_tarjeta(request):
    if request.method == "POST":
        request.session["numero_tarjeta"] = request.POST.get("numero")
        request.session["titular_tarjeta"] = request.POST.get("titular")
        request.session["expiracion_tarjeta"] = request.POST.get("expiracion")
        request.session["cvv_tarjeta"] = request.POST.get("cvv")
        return redirect("pagos:resumen_pago")

    return render(request, "pagos/ingresar_tarjeta.html")


def resumen_pago(request):
    if request.method == "POST":
        cliente = request.user.cliente

        # Crear tarjeta
        tarjeta = TarjetaCredito.objects.create(
            numero=request.session["numero_tarjeta"],
            nombre_titular=request.session["titular_tarjeta"],
            fecha_expiracion=request.session["expiracion_tarjeta"],
            cvv=request.session["cvv_tarjeta"],
            cliente=cliente
        )

        plan = request.session.get("plan")
        modalidad = request.session.get("modalidad")
        direccion_id = request.session.get("direccion_id")
        monto = PLANES_DISPONIBLES[plan][f"precio_{modalidad}"]

        # Crear pago
        Pago.objects.create(
            cliente=cliente,
            direccion_id=direccion_id,
            tarjeta_usada=tarjeta,
            monto=monto
        )

        # Actualizar estado de suscripción
        cliente.tiene_suscripcion = True
        cliente.plan = plan
        cliente.fecha_inicio_suscripcion = timezone.now()

        # Calcular fecha de fin de suscripción
        if modalidad == "mensual":
            cliente.fecha_fin_suscripcion = timezone.now() + timedelta(days=30)
        elif modalidad == "anual":
            cliente.fecha_fin_suscripcion = timezone.now() + timedelta(days=365)
        else:
            cliente.fecha_fin_suscripcion = None  # o manejar otra lógica

        cliente.save()

        return redirect("pagos:confirmacion_pago")

    # Mostrar resumen
    plan = request.session.get("plan")
    modalidad = request.session.get("modalidad")
    direccion_id = request.session.get("direccion_id")
    direccion = Direccion.objects.get(direccionId=direccion_id)
    monto = PLANES_DISPONIBLES[plan][f"precio_{modalidad}"]

    resumen = {
        "plan": plan,
        "modalidad": modalidad,
        "monto": monto,
        "direccion": direccion,
        "tarjeta": f"**** **** **** {request.session.get('numero_tarjeta')[-4:]}"
    }

    return render(request, "pagos/resumen_pago.html", resumen)

@login_required
def confirmacion_pago(request):
    # limpiar la sesión
    for key in ["plan", "modalidad", "direccion_id", "numero_tarjeta", "titular_tarjeta", "expiracion_tarjeta", "cvv_tarjeta"]:
        request.session.pop(key, None)

    return render(request, "pagos/confirmacion_pago.html")