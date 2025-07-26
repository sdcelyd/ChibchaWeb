from django.core.exceptions import ValidationError

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
