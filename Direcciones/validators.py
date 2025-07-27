import re
from django.core.exceptions import ValidationError

def validar_direccion_colombia(value):
    # Expresión regular para validar direcciones en Colombia
    regex = r'^(Calle|Cl\.|Carrera|Cra\.|Diagonal|Dg\.|Transversal|Tv\.)\s\d{1,99}(?:\s?[A-Z])?(?:\s?(Sur|Este|Oeste))?\s?#?\s?\d{1,99}(?:\s?[A-Z])?\s?\d{1,99}(?:[-\s]\d{1,99})?$'
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
