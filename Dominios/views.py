import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from ChibchaWeb.decorators import cliente_required
from .forms import VerificarURLForm, AgregarDominioForm
from .models import Dominios
import xml.etree.ElementTree as ET

def verificar_url(request):
    resultado = None
    valido = True

    if request.method == 'POST':
        form = VerificarURLForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    resultado = f"La URL {url} está siendo utilizada."
                    valido = False
                else:
                    resultado = f"La URL {url} respondió con código {response.status_code}."
                    valido = False
            except requests.RequestException:
                resultado = f"La URL {url} no está siendo ocupada y la puedes usar!."
                valido = True
    else:
        form = VerificarURLForm()

    return render(request, 'verificar_url.html', {'form': form, 'resultado': resultado,  'valido': valido,})

@login_required
def generar_xml(request):
    """
    Genera un XML con la última URL verificada (pasada por GET o sesión)
    y datos del cliente (usuario Django).
    """
    # 1) Recuperar la URL: la puedes pasar como parámetro GET o guardarla en sesión
    url = request.GET.get('url', '')
    user = request.user

    # 2) Construir el XML
    root = ET.Element('Solicitud')
    ET.SubElement(root, 'Cliente').text = user.get_full_name() or user.username
    ET.SubElement(root, 'Email').text = user.email
    ET.SubElement(root, 'URL').text = url

    xml_bytes = ET.tostring(root, encoding='utf-8', xml_declaration=True)

    # 3) Devolver respuesta con content_type XML
    response = HttpResponse(xml_bytes, content_type='application/xml')
    response['Content-Disposition'] = f'attachment; filename=Solicitud_{user.username}.xml'
    return response

@cliente_required
def agregar_dominio(request):
    """
    Vista para que los clientes agreguen dominios a su cuenta
    """
    cliente = request.cliente
    
    # Verificar si viene desde un distribuidor
    from_distribuidor = request.GET.get('from') == 'distribuidor'
    compra_distribuidor = from_distribuidor
    
    # Verificar que tenga suscripción activa
    if not cliente.suscripcion_activa:
        messages.warning(request, "Necesitas una suscripción activa para agregar dominios.")
        return redirect('clientes:home_clientes')
    
    # Verificar límite de dominios según el plan (solo si no viene de distribuidor)
    if not from_distribuidor and not cliente.puede_agregar_dominios:
        messages.error(request, f"Has alcanzado el límite de dominios para tu plan {cliente.plan} ({cliente.limite_dominios} dominios). Considera actualizar tu plan para agregar más dominios.")
        return redirect('clientes:mis_hosts')
    
    form = AgregarDominioForm()
    dominio_validado = False
    dominio_disponible = False
    dominio_valor = ""
    
    if request.method == 'POST':
        form = AgregarDominioForm(request.POST)
        accion = request.POST.get('accion')
        
        if form.is_valid():
            dominio = form.cleaned_data['dominio']
            dominio_valor = dominio
            
            # Verificar si el dominio ya existe en nuestra base de datos
            if Dominios.objects.filter(nombreDominio=dominio).exists():
                messages.error(request, f"El dominio '{dominio}' ya está registrado en nuestro sistema.")
                return render(request, 'agregar_dominio.html', {
                    'form': form, 
                    'cliente': cliente,
                    'dominio_validado': False,
                    'dominio_disponible': False,
                    'dominio_valor': dominio_valor,
                    'from_distribuidor': from_distribuidor
                })
            
            if accion == 'validar':
                # Solo validar disponibilidad
                try:
                    response = requests.get(f"http://{dominio}", timeout=3)
                    if response.status_code == 200:
                        dominio_validado = True
                        dominio_disponible = False
                        messages.warning(request, f"El dominio '{dominio}' está actualmente en uso. Si este dominio te pertenece y quieres transferirlo a ChibchaWeb, contacta a nuestro soporte.")
                    else:
                        dominio_validado = True
                        dominio_disponible = True
                        messages.success(request, f"¡Excelente! El dominio '{dominio}' está disponible y listo para configurar.")
                except requests.RequestException:
                    dominio_validado = True
                    dominio_disponible = True
                    messages.success(request, f"¡Perfecto! El dominio '{dominio}' está disponible y listo para usar en tu hosting.")
                    
            elif accion == 'agregar':
                # Verificar disponibilidad antes de agregar
                try:
                    response = requests.get(f"http://{dominio}", timeout=3)
                    if response.status_code == 200:
                        messages.error(request, f"No se puede agregar el dominio '{dominio}' porque está siendo utilizado activamente. Por favor, elige un dominio diferente o contacta a soporte si este dominio te pertenece.")
                        return render(request, 'agregar_dominio.html', {
                            'form': form, 
                            'cliente': cliente,
                            'dominio_validado': True,
                            'dominio_disponible': False,
                            'dominio_valor': dominio_valor,
                            'from_distribuidor': from_distribuidor
                        })
                except requests.RequestException:
                    # Dominio no responde, se puede agregar
                    pass
                
                # Crear el registro del dominio
                nuevo_dominio = Dominios.objects.create(
                    clienteId=cliente,
                    nombreDominio=dominio,
                    compraDistribuidor=compra_distribuidor
                )
                
                # Si viene desde distribuidor, actualizar contador de páginas vendidas
                if from_distribuidor and hasattr(cliente, 'perfil_distribuidor'):
                    distribuidor = cliente.perfil_distribuidor
                    if distribuidor.paginas_disponibles > 0:
                        distribuidor.paginas_vendidas += 1
                        distribuidor.save()
                        messages.info(request, f"Se ha usado 1 espacio de tu paquete de distribuidor. Tienes {distribuidor.paginas_disponibles - 1} espacios restantes.")
                    else:
                        # Esto no debería pasar si se valida correctamente en el frontend
                        messages.warning(request, "No tienes espacios disponibles en tu paquete de distribuidor.")
                
                # Generar XML para uso interno
                generar_xml_interno(cliente, dominio)
                
                messages.success(request, f"¡Perfecto! El dominio '{dominio}' ha sido agregado exitosamente a tu cuenta.")
                
                # Redirigir según el origen
                if from_distribuidor:
                    return redirect('distribuidores:mis_paquetes')
                else:
                    return redirect('clientes:mis_hosts')
    
    return render(request, 'agregar_dominio.html', {
        'form': form, 
        'cliente': cliente,
        'dominio_validado': dominio_validado,
        'dominio_disponible': dominio_disponible,
        'dominio_valor': dominio_valor,
        'from_distribuidor': from_distribuidor
    })

def generar_xml_interno(cliente, dominio):
    """
    Genera un XML interno para el equipo de ChibchaWeb
    """
    root = ET.Element('SolicitudDominio')
    ET.SubElement(root, 'Cliente').text = cliente.user.get_full_name() or cliente.user.username
    ET.SubElement(root, 'Email').text = cliente.user.email
    ET.SubElement(root, 'UserId').text = str(cliente.user.id)
    ET.SubElement(root, 'ClienteId').text = str(cliente.id)
    ET.SubElement(root, 'Dominio').text = dominio
    ET.SubElement(root, 'Plan').text = cliente.plan or "N/A"
    ET.SubElement(root, 'FechaSolicitud').text = str(timezone.now())
    
    # Guardar XML en directorio interno (opcional)
    xml_string = ET.tostring(root, encoding='utf-8', xml_declaration=True)
    
    # Aquí podrías guardar el XML en un directorio específico para el equipo
    # Por ahora, solo lo generamos en memoria

@cliente_required
def eliminar_dominio(request, dominio_id):
    """
    Vista para eliminar dominios del cliente
    """
    cliente = request.cliente
    
    # Verificar si viene desde un distribuidor
    from_distribuidor = request.GET.get('from') == 'distribuidor'
    
    try:
        dominio = Dominios.objects.get(id=dominio_id, clienteId=cliente)
    except Dominios.DoesNotExist:
        messages.error(request, "El dominio no existe o no te pertenece.")
        if from_distribuidor:
            return redirect('distribuidores:mis_paquetes')
        else:
            return redirect('clientes:mis_hosts')
    
    if request.method == 'POST':
        nombre_dominio = dominio.nombreDominio
        es_dominio_distribuidor = dominio.compraDistribuidor
        
        # Si era un dominio del distribuidor, decrementar el contador
        if es_dominio_distribuidor and hasattr(cliente, 'perfil_distribuidor'):
            distribuidor = cliente.perfil_distribuidor
            if distribuidor.paginas_vendidas > 0:
                distribuidor.paginas_vendidas -= 1
                distribuidor.save()
                messages.info(request, f"Se ha liberado 1 espacio en tu paquete de distribuidor. Tienes {distribuidor.paginas_disponibles} espacios disponibles.")
        
        dominio.delete()
        messages.success(request, f"El dominio '{nombre_dominio}' ha sido eliminado de tu cuenta exitosamente.")
        
        # Redirigir según el origen
        if from_distribuidor:
            return redirect('distribuidores:mis_paquetes')
        else:
            return redirect('clientes:mis_hosts')
    
    return render(request, 'eliminar_dominio.html', {
        'dominio': dominio,
        'cliente': cliente,
        'from_distribuidor': from_distribuidor
    })