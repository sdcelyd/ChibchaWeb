from django.core.exceptions import ValidationError
import re

def validar_tarjeta(value):
    T=""; par=0; impar=0; X=""
    if not value.isdigit():
        raise ValidationError("El número de tarjeta debe contener solo dígitos.")
    if len(value) < 14 or len(value) > 19:
        raise ValidationError("El número de tarjeta debe tener entre 14 y 19 dígitos.")
    for c in range(0, len(value), 2):
        X = str(int(value[c]) * 2)
        if len(X) == 2:
            par += (int(X[0]) + int(X[1]))
        else:
            par += int(X)
    for c in range(1, len(value), 2):
        impar += int(value[c])
    if (par + impar) % 10 != 0:
        raise ValidationError("El número de tarjeta no es válido.")
    if int(value[0:2]) > 49 and int(value[0:2]) < 56:
        T = "**MasterCard**"
    if value[0:2] == "34" or value[0:2] == "37":
        T = "**America Express**"
    if value[0] == "4":
        T = "**VISA**"
    if value[0:2] in ["60", "62", "64", "65"]:
        T = "**Discover**"

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
