from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
import re
from .models import Direccion, TarjetaCredito, Pais, Pago, PagoDistribuidor
from Clientes.models import Cliente
from .validators import validar_tarjeta, VALIDADORES_DIRECCIONES
from ChibchaWeb.planes import PLANES_DISPONIBLES
from datetime import timedelta
from django.utils import timezone
from ChibchaWeb.decorators import cliente_required, distribuidor_required


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
                        context = {
                            'paises': paises,
                            'from_payment': 'from_payment' in request.GET,
                        }
                        return render(request, 'pagos/registrar_direccion.html', context)
                
                direccion = Direccion.objects.create(
                    ubicacion=ubicacion,
                    codigoPostal=codigo_postal,
                    pais=pais,
                    cliente=cliente
                )
                messages.success(request, "Dirección registrada exitosamente.")
                
                # Si viene del flujo de pago, redirigir de vuelta a selección de direcciones
                if 'from_payment' in request.GET:
                    return redirect('pagos:seleccionar_direccion')
                
                # Verificar si hay un plan pendiente
                plan_pendiente = request.session.get("plan_pendiente")
                modalidad_pendiente = request.session.get("modalidad_pendiente")
                
                if plan_pendiente and modalidad_pendiente:
                    # Verificar si ahora también tiene tarjeta
                    if cliente.tarjetas.exists():
                        # Tiene todo, continuar con el plan
                        request.session["plan"] = plan_pendiente
                        request.session["modalidad"] = modalidad_pendiente
                        # Limpiar pendientes
                        request.session.pop("plan_pendiente", None)
                        request.session.pop("modalidad_pendiente", None)
                        messages.success(request, f"¡Perfecto! Ahora puedes continuar con tu plan {plan_pendiente}.")
                        return redirect("pagos:seleccionar_direccion")
                    else:
                        # Aún falta la tarjeta
                        messages.info(request, "Ahora necesitas registrar una tarjeta de crédito para completar tu plan.")
                        return redirect("pagos:registrar_tarjeta")
                
                return redirect('clientes:detalle_cliente')
            except Exception as e:
                messages.error(request, f"Error al registrar la dirección: {str(e)}")
        else:
            messages.error(request, "Por favor completa todos los campos requeridos.")
    
    paises = Pais.objects.all()
    context = {
        'paises': paises,
        'from_payment': 'from_payment' in request.GET,
    }
    return render(request, 'pagos/registrar_direccion.html', context)


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
                
                # Si viene del flujo de pago, redirigir de vuelta a selección de tarjetas
                if 'from_payment' in request.GET:
                    return redirect('pagos:seleccionar_tarjeta')
                
                # Verificar si hay un plan pendiente
                plan_pendiente = request.session.get("plan_pendiente")
                modalidad_pendiente = request.session.get("modalidad_pendiente")
                
                if plan_pendiente and modalidad_pendiente:
                    # Verificar si ahora también tiene dirección
                    if cliente.direcciones.exists():
                        # Tiene todo, continuar con el plan
                        request.session["plan"] = plan_pendiente
                        request.session["modalidad"] = modalidad_pendiente
                        # Limpiar pendientes
                        request.session.pop("plan_pendiente", None)
                        request.session.pop("modalidad_pendiente", None)
                        messages.success(request, f"¡Perfecto! Ahora puedes continuar con tu plan {plan_pendiente}.")
                        return redirect("pagos:seleccionar_direccion")
                    else:
                        # Aún falta la dirección
                        messages.info(request, "Ahora necesitas registrar una dirección de facturación para completar tu plan.")
                        return redirect("pagos:registrar_direccion")
                
                return redirect('clientes:detalle_cliente')
            except ValidationError as e:
                messages.error(request, str(e))
                return render(request, 'pagos/registrar_tarjeta.html')
            except Exception as e:
                messages.error(request, f"Error al registrar la tarjeta: {str(e)}")
        else:
            messages.error(request, "Por favor completa todos los campos requeridos.")
    
    context = {
        'from_payment': 'from_payment' in request.GET,
    }
    
    return render(request, 'pagos/registrar_tarjeta.html', context)


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
        modalidad = request.POST.get("modalidad")  # mensual, semestral, anual
        
        # Verificar si el usuario es cliente
        try:
            cliente = request.user.cliente
        except:
            messages.error(request, "Debes ser un cliente registrado para adquirir un plan.")
            return redirect('clientes:login')
        
        # Verificar si tiene dirección registrada
        tiene_direccion = cliente.direcciones.exists()
        
        # Verificar si tiene tarjeta de crédito registrada
        tiene_tarjeta = cliente.tarjetas.exists()
        
        # Si no tiene dirección, redirigir a registrar dirección
        if not tiene_direccion:
            messages.warning(request, "Necesitas registrar una dirección de facturación antes de continuar con tu plan.")
            # Guardar la selección en sesión para después
            request.session["plan_pendiente"] = plan
            request.session["modalidad_pendiente"] = modalidad
            return redirect("pagos:registrar_direccion")
        
        # Si no tiene tarjeta, redirigir a registrar tarjeta
        if not tiene_tarjeta:
            messages.warning(request, "Necesitas registrar una tarjeta de crédito antes de continuar con tu plan.")
            # Guardar la selección en sesión para después
            request.session["plan_pendiente"] = plan
            request.session["modalidad_pendiente"] = modalidad
            return redirect("pagos:registrar_tarjeta")
        
        # Si tiene ambos, continuar a seleccionar dirección específica
        request.session["plan"] = plan
        request.session["modalidad"] = modalidad
        messages.success(request, f"Plan {plan} en modalidad {modalidad} seleccionado. Ahora selecciona tu dirección de facturación.")
        return redirect("pagos:seleccionar_direccion")
    
    return render(request, "pagos/seleccionar_plan.html", {"planes": PLANES_DISPONIBLES})

@login_required
def seleccionar_direccion(request):
    try:
        cliente = request.user.cliente
    except:
        messages.error(request, "Debes ser un cliente registrado.")
        return redirect('clientes:login')
    
    # Verificar que hay un plan seleccionado
    plan = request.session.get("plan")
    modalidad = request.session.get("modalidad")
    if not plan or not modalidad:
        messages.error(request, "Debes seleccionar un plan primero.")
        return redirect("pagos:seleccionar_plan")
    
    if request.method == "POST":
        direccion_id = request.POST.get("direccion_id")
        accion = request.POST.get("accion")
        
        if accion == "nueva_direccion":
            return redirect("pagos:registrar_direccion?from_payment=true")
        elif direccion_id:
            # Verificar que la dirección pertenece al cliente
            try:
                direccion = get_object_or_404(Direccion, direccionId=direccion_id, cliente=cliente)
                request.session["direccion_id"] = direccion.direccionId
                messages.success(request, f"Dirección seleccionada: {direccion.ubicacion}")
                return redirect("pagos:seleccionar_tarjeta")
            except:
                messages.error(request, "Dirección no válida.")
        else:
            messages.error(request, "Debes seleccionar una dirección.")
    
    # Obtener todas las direcciones del cliente
    direcciones = cliente.direcciones.all()
    context = {
        "direcciones": direcciones,
        "plan": plan,
        "modalidad": modalidad,
        "precio": PLANES_DISPONIBLES[plan][f"precio_{modalidad}"]
    }
    
    return render(request, "pagos/seleccionar_direccion.html", context)

@login_required
def ingresar_tarjeta(request):
    if request.method == "POST":
        tarjeta_id = request.POST.get("tarjeta_id")
        accion = request.POST.get("accion")
        
        if accion == "nueva_tarjeta":
            return redirect("pagos:registrar_tarjeta?from_payment=true")
        elif tarjeta_id:
            # Verificar que la tarjeta pertenece al cliente
            try:
                tarjeta = get_object_or_404(TarjetaCredito, id=tarjeta_id, cliente=cliente)
                request.session["tarjeta_id"] = tarjeta.id
                messages.success(request, f"Tarjeta seleccionada: **** **** **** {tarjeta.numero[-4:]}")
                return redirect("pagos:resumen_pago")
            except:
                messages.error(request, "Tarjeta no válida.")
        else:
            messages.error(request, "Debes seleccionar una tarjeta.")
    
    # Obtener todas las tarjetas del cliente
    tarjetas = cliente.tarjetas.all()
    direccion = get_object_or_404(Direccion, direccionId=direccion_id, cliente=cliente)
    
    context = {
        "tarjetas": tarjetas,
        "plan": plan,
        "modalidad": modalidad,
        "precio": PLANES_DISPONIBLES[plan][f"precio_{modalidad}"],
        "direccion": direccion
    }
    
    return render(request, "pagos/seleccionar_tarjeta.html", context)

@login_required
def resumen_pago(request):
    try:
        cliente = request.user.cliente
    except:
        messages.error(request, "Debes ser un cliente registrado.")
        return redirect('clientes:login')
    
    # Verificar que tenemos todos los datos necesarios
    plan = request.session.get("plan")
    modalidad = request.session.get("modalidad")
    direccion_id = request.session.get("direccion_id")
    tarjeta_id = request.session.get("tarjeta_id")
    
    if not all([plan, modalidad, direccion_id, tarjeta_id]):
        messages.error(request, "Faltan datos para procesar el pago. Por favor, inicia el proceso nuevamente.")
        return redirect("pagos:seleccionar_plan")
    
    # Obtener los objetos
    try:
        direccion = get_object_or_404(Direccion, direccionId=direccion_id, cliente=cliente)
        tarjeta = get_object_or_404(TarjetaCredito, id=tarjeta_id, cliente=cliente)
    except:
        messages.error(request, "Datos de dirección o tarjeta no válidos.")
        return redirect("pagos:seleccionar_plan")
    
    if request.method == "POST":
        # Verificar el monto
        monto = PLANES_DISPONIBLES[plan][f"precio_{modalidad}"]

        # Crear pago
        pago = Pago.objects.create(
            cliente=cliente,
            direccion=direccion,
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
        elif modalidad == "semestral":
            cliente.fecha_fin_suscripcion = timezone.now() + timedelta(days=180)
        elif modalidad == "anual":
            cliente.fecha_fin_suscripcion = timezone.now() + timedelta(days=365)

        cliente.save()

        messages.success(request, f"¡Pago procesado exitosamente! Tu plan {plan} está activo.")
        return redirect("pagos:confirmacion_pago")

    # Mostrar resumen
    monto = PLANES_DISPONIBLES[plan][f"precio_{modalidad}"]

    resumen = {
        "plan": plan,
        "modalidad": modalidad,
        "monto": monto,
        "direccion": direccion,
        "tarjeta": tarjeta
    }

    return render(request, "pagos/resumen_pago.html", resumen)

@login_required
def confirmacion_pago(request):
    # limpiar la sesión
    keys_to_remove = [
        "plan", "modalidad", "direccion_id", "tarjeta_id",
        "plan_pendiente", "modalidad_pendiente"
    ]
    for key in keys_to_remove:
        request.session.pop(key, None)

    return render(request, "pagos/confirmacion_pago.html")

@login_required
@distribuidor_required
def seleccionar_paquete(request):
    if request.method == "POST":
        cantidad = request.POST.get("cantidad")
        request.session["cantidad_paquetes"] = int(cantidad)
        request.session["es_compra_paquetes"] = True
        return redirect("pagos:direccion_facturacion")  # Reutilizas esta vista
    return render(request, "pagos/seleccionar_paquete.html")

@login_required
@distribuidor_required
def resumen_pago_paquetes(request):
    if request.method == "POST":
        distribuidor = request.user.cliente  # es un Distribuidor
        tarjeta = TarjetaCredito.objects.create(
            numero=request.session["numero_tarjeta"],
            nombre_titular=request.session["titular_tarjeta"],
            fecha_expiracion=request.session["expiracion_tarjeta"],
            cvv=request.session["cvv_tarjeta"],
            cliente=distribuidor
        )

        direccion_id = request.session.get("direccion_id")
        cantidad_paquetes = int(request.session.get("cantidad_paquetes"))
        precio_unitario = 25  # HAY QUE DEFINIR EL PRECIOO
        monto = cantidad_paquetes * precio_unitario

        # Crear el pago asociado a distribuidor
        pago = Pago.objects.create(
            cliente=distribuidor,
            direccion_id=direccion_id,
            tarjeta_usada=tarjeta,
            monto=monto
        )

        # Crear el registro extendido
        PagoDistribuidor.objects.create(
            cliente=distribuidor,
            direccion_id=direccion_id,
            tarjeta_usada=tarjeta,
            monto=monto,
            cantidad_paginas=cantidad_paquetes,
            descripcion=f"Compra de {cantidad_paquetes} páginas para reventa"
        )

        distribuidor_perfil = distribuidor.perfil_distribuidor  # accede al modelo Distribuidor
        distribuidor_perfil.cantidad_dominios += cantidad_paquetes
        distribuidor_perfil.save()



        return redirect("pagos:confirmacion_pago_paquetes")

    # Mostrar resumen
    cantidad = int(request.session.get("cantidad_paquetes", 0))
    precio_unitario = 25
    direccion = Direccion.objects.get(direccionId=request.session["direccion_id"])
    total = cantidad * precio_unitario

    return render(request, "pagos/resumen_pago_paquetes.html", {
        "cantidad": cantidad,
        "precio_unitario": precio_unitario,
        "total": total,
        "direccion": direccion,
        "tarjeta": f"**** **** **** {request.session.get('numero_tarjeta')[-4:]}"
    })


@login_required
@distribuidor_required
def confirmacion_pago_paquetes(request):
    # Limpieza de sesión
    for key in ["cantidad_paquetes", "direccion_id", "numero_tarjeta", "titular_tarjeta", "expiracion_tarjeta", "cvv_tarjeta", "es_compra_paquetes"]:
        request.session.pop(key, None)

    return render(request, "pagos/confirmacion_pago_paquetes.html")