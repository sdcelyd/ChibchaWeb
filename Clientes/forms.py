from django import forms
from .models import Cliente

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['nickname', 'email', 'nombre', 'contrasena', 'telefono']
        widgets = {
            'contrasena': forms.PasswordInput(),  # esto oculta el texto
        }