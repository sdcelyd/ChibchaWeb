from django.core.exceptions import ValidationError
import re

def validar_tarjeta(value):
    if not value.isdigit():
        raise ValidationError("El número de tarjeta debe contener solo dígitos.")
    
    if len(value) < 14 or len(value) > 19:
        raise ValidationError("El número de tarjeta debe tener entre 14 y 19 dígitos.")
    
    # Validación de franquicia permitida
    if value.startswith("4"):
        return  # VISA
    elif value[:2] in [str(i) for i in range(51, 56)]:
        return  # MasterCard 51-55
    elif 2221 <= int(value[:4]) <= 2720:
        return  # MasterCard rango extendido
    elif value.startswith("36") or value.startswith("38") or value.startswith("39"):
        return  # Diners Club
    else:
        raise ValidationError("Solo se permiten tarjetas VISA, MasterCard o Diners Club.")

def validar_direccion_colombia(value):
    # Expresión regular deshabilitada: acepta cualquier cadena
    regex = r'.*'
    if not re.match(regex, value):
        raise ValidationError(
            f"La dirección '{value}' no es válida para el formato colombiano."
        )

def validar_direccion_ecuador(value):
    # Expresión regular para validar direcciones en Ecuador
    regex = r'^(Calle|Av\.|Avenida|Via|Vía|Camino)\s\d{1,99}(?:\s?[A-Z])?(?:\s?(Norte|Sur|Este|Oeste))?\s?#?\s?\d{1,99}(?:\s?[A-Z])?\s?\d{1,99}(?:[-\s]\d{1,99})?$'
    if not re.match(regex, value):
        raise ValidationError(
            f"La dirección '{value}' no es válida para el formato ecuatoriano."
        )

def validar_direccion_peru(value):
    # Expresión regular para validar direcciones en Perú
    regex = r'^(Calle|Av\.|Avenida|Jr\.|Jiron|Pasaje|Psje\.|Carretera|Ctra\.)\s\d{1,99}(?:\s?[A-Z])?(?:\s?(Norte|Sur|Este|Oeste))?\s?#?\s?\d{1,99}(?:\s?[A-Z])?\s?\d{1,99}(?:[-\s]\d{1,99})?$'
    if not re.match(regex, value):
        raise ValidationError(
            f"La dirección '{value}' no es válida para el formato peruano."
        )

VALIDADORES_DIRECCIONES = {
    'colombia': validar_direccion_colombia,
    'ecuador': validar_direccion_ecuador,
    'peru': validar_direccion_peru,
}
