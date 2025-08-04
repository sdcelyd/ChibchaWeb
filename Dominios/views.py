import requests
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .forms import VerificarURLForm
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