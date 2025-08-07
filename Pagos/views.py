from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.conf import settings
from django.urls import reverse
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
                        return render(request, 'registrar_direccion.html', context)
                
                direccion = Direccion.objects.create(
                    ubicacion=ubicacion,
                    codigoPostal=codigo_postal,
                    pais=pais,
                    cliente=cliente
                )
                messages.success(request, "Dirección registrada exitosamente.")
                
                # Si viene del flujo de pago, redirigir de vuelta a selección unificada
                if 'from_payment' in request.GET:
                    return redirect('pagos:seleccionar_direccion_tarjeta')
                
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
                        return redirect("pagos:seleccionar_direccion_tarjeta")
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
    return render(request, 'registrar_direccion.html', context)


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
                    return render(request, 'registrar_tarjeta.html')
                
                # Validar CVV (3 o 4 dígitos)
                if not re.match(r'^\d{3,4}$', cvv):
                    messages.error(request, "El CVV debe tener 3 o 4 dígitos")
                    return render(request, 'registrar_tarjeta.html')
                
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
                
                # Si viene del flujo de pago, redirigir de vuelta a selección unificada
                if 'from_payment' in request.GET:
                    return redirect('pagos:seleccionar_direccion_tarjeta')
                
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
                        return redirect("pagos:seleccionar_direccion_tarjeta")
                    else:
                        # Aún falta la dirección
                        messages.info(request, "Ahora necesitas registrar una dirección de facturación para completar tu plan.")
                        return redirect("pagos:registrar_direccion")
                
                return redirect('clientes:detalle_cliente')
            except ValidationError as e:
                messages.error(request, str(e))
                return render(request, 'registrar_tarjeta.html')
            except Exception as e:
                messages.error(request, f"Error al registrar la tarjeta: {str(e)}")
        else:
            messages.error(request, "Por favor completa todos los campos requeridos.")
    
    context = {
        'from_payment': 'from_payment' in request.GET,
    }
    
    return render(request, 'registrar_tarjeta.html', context)


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
        
        # Si tiene ambos, continuar a seleccionar dirección y tarjeta específicas
        request.session["plan"] = plan
        request.session["modalidad"] = modalidad
        messages.success(request, f"Plan {plan} en modalidad {modalidad} seleccionado. Ahora selecciona tu dirección y tarjeta de pago.")
        return redirect("pagos:seleccionar_direccion_tarjeta")
    
    return render(request, "seleccionar_plan.html", {"planes": PLANES_DISPONIBLES})

@login_required
def seleccionar_direccion_tarjeta(request):
    try:
        cliente = request.user.cliente
    except:
        messages.error(request, "Debes ser un cliente registrado.")
        return redirect('clientes:login')
    
    # Verificar si es compra de paquetes o planes
    es_compra_paquetes = request.session.get("es_compra_paquetes", False)
    
    if es_compra_paquetes:
        # Para compra de paquetes
        cantidad_paquetes = request.session.get("cantidad_paquetes")
        if not cantidad_paquetes:
            messages.error(request, "Debes seleccionar un paquete primero.")
            return redirect("pagos:seleccionar_paquete")
    else:
        # Para compra de planes
        plan = request.session.get("plan")
        modalidad = request.session.get("modalidad")
        if not plan or not modalidad:
            messages.error(request, "Debes seleccionar un plan primero.")
            return redirect("pagos:seleccionar_plan")
    
    if request.method == "POST":
        direccion_id = request.POST.get("direccion_id")
        tarjeta_id = request.POST.get("tarjeta_id")
        accion = request.POST.get("accion")
        
        # Manejar acciones de crear nuevos elementos
        if accion == "nueva_direccion":
            url = reverse("pagos:registrar_direccion") + "?from_payment=true"
            return redirect(url)
        elif accion == "nueva_tarjeta":
            url = reverse("pagos:registrar_tarjeta") + "?from_payment=true"
            return redirect(url)
        
        # Validar que se seleccionaron ambos
        if not direccion_id or not tarjeta_id:
            messages.error(request, "Debes seleccionar una dirección y una tarjeta para continuar.")
        else:
            # Verificar que ambos pertenecen al cliente
            try:
                direccion = get_object_or_404(Direccion, direccionId=direccion_id, cliente=cliente)
                tarjeta = get_object_or_404(TarjetaCredito, id=tarjeta_id, cliente=cliente)
                
                # Guardar en sesión
                request.session["direccion_id"] = direccion.direccionId
                request.session["tarjeta_id"] = tarjeta.id
                
                messages.success(request, f"Seleccionado: {direccion.ubicacion} y tarjeta terminada en {tarjeta.numero[-4:]}")
                
                # Redirigir según el tipo de compra
                if es_compra_paquetes:
                    return redirect("pagos:resumen_pago_paquetes")
                else:
                    return redirect("pagos:resumen_pago")
            except:
                messages.error(request, "Dirección o tarjeta no válida.")
    
    # Obtener direcciones y tarjetas del cliente
    direcciones = cliente.direcciones.all()
    tarjetas = cliente.tarjetas.all()
    
    # Preparar contexto según el tipo de compra
    context = {
        "direcciones": direcciones,
        "tarjetas": tarjetas,
        "es_compra_paquetes": es_compra_paquetes,
    }
    
    if es_compra_paquetes:
        cantidad_paquetes = request.session.get("cantidad_paquetes")
        precio_unitario = settings.PRECIO_POR_PAGINA_DISTRIBUIDOR
        total_paquetes = int(cantidad_paquetes) * precio_unitario
        context.update({
            "cantidad_paquetes": cantidad_paquetes,
            "precio_unitario": precio_unitario,
            "total_paquetes": total_paquetes,
        })
    else:
        plan = request.session.get("plan")
        modalidad = request.session.get("modalidad")
        context.update({
            "plan": plan,
            "modalidad": modalidad,
            "precio": PLANES_DISPONIBLES[plan][f"precio_{modalidad}"]
        })
    
    return render(request, "seleccionar_direccion_tarjeta.html", context)

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

    return render(request, "resumen_pago.html", resumen)

@login_required
def confirmacion_pago(request):
    # limpiar la sesión
    keys_to_remove = [
        "plan", "modalidad", "direccion_id", "tarjeta_id",
        "plan_pendiente", "modalidad_pendiente"
    ]
    for key in keys_to_remove:
        request.session.pop(key, None)

    return render(request, "confirmacion_pago.html")

@login_required
@distribuidor_required
def seleccionar_paquete(request):
    if request.method == 'POST':
        cantidad = int(request.POST.get('cantidad', 1))
        precio_unitario = settings.PRECIO_POR_PAGINA_DISTRIBUIDOR
        request.session['es_compra_paquetes'] = True
        request.session['cantidad_paquetes'] = cantidad
        request.session['precio_unitario'] = precio_unitario
        request.session['total_paquetes'] = cantidad * precio_unitario
        
        return redirect('pagos:seleccionar_direccion_tarjeta')
    
    context = {
        'precio_por_pagina': settings.PRECIO_POR_PAGINA_DISTRIBUIDOR,
    }
    
    return render(request, 'seleccionar_paquete.html', context)

@login_required
@distribuidor_required
def resumen_pago_paquetes(request):
    cliente = request.cliente  # Proporcionado por el decorador
    
    # Verificar que tenemos todos los datos necesarios
    cantidad_paquetes = request.session.get("cantidad_paquetes")
    direccion_id = request.session.get("direccion_id")
    tarjeta_id = request.session.get("tarjeta_id")
    
    if not all([cantidad_paquetes, direccion_id, tarjeta_id]):
        messages.error(request, "Faltan datos para procesar el pago. Por favor, inicia el proceso nuevamente.")
        return redirect("pagos:seleccionar_paquete")
    
    # Obtener los objetos
    try:
        direccion = get_object_or_404(Direccion, direccionId=direccion_id, cliente=cliente)
        tarjeta = get_object_or_404(TarjetaCredito, id=tarjeta_id, cliente=cliente)
    except:
        messages.error(request, "Datos de dirección o tarjeta no válidos.")
        return redirect("pagos:seleccionar_paquete")

    if request.method == "POST":
        cantidad_paquetes = int(cantidad_paquetes)
        precio_unitario = settings.PRECIO_POR_PAGINA_DISTRIBUIDOR
        monto = cantidad_paquetes * precio_unitario

        # Crear el pago base
        pago = Pago.objects.create(
            cliente=cliente,
            direccion=direccion,
            tarjeta_usada=tarjeta,
            monto=monto
        )

        # Crear el registro extendido para distribuidores
        PagoDistribuidor.objects.create(
            cliente=cliente,
            direccion=direccion,
            tarjeta_usada=tarjeta,
            monto=monto,
            cantidad_paginas=cantidad_paquetes,
            descripcion=f"Compra de {cantidad_paquetes} páginas para reventa"
        )

        # Actualizar el perfil del distribuidor
        try:
            distribuidor_perfil = cliente.perfil_distribuidor
            distribuidor_perfil.cantidad_dominios += cantidad_paquetes
            distribuidor_perfil.save()
        except:
            messages.warning(request, "No se pudo actualizar el perfil de distribuidor.")

        messages.success(request, f"¡Pago procesado exitosamente! Se agregaron {cantidad_paquetes} páginas a tu cuenta.")
        return redirect("pagos:confirmacion_pago_paquetes")

    # Mostrar resumen
    cantidad = int(cantidad_paquetes)
    precio_unitario = settings.PRECIO_POR_PAGINA_DISTRIBUIDOR
    total = cantidad * precio_unitario

    resumen = {
        "cantidad": cantidad,
        "precio_unitario": precio_unitario,
        "total": total,
        "direccion": direccion,
        "tarjeta": tarjeta
    }

    return render(request, "resumen_pago_paquetes.html", resumen)


@login_required
@distribuidor_required
def confirmacion_pago_paquetes(request):
    # Limpieza de sesión - usar las variables del nuevo flujo
    keys_to_remove = [
        "cantidad_paquetes", "direccion_id", "tarjeta_id", "es_compra_paquetes"
    ]
    for key in keys_to_remove:
        request.session.pop(key, None)

    return render(request, "confirmacion_pago_paquetes.html")