from django import forms
from .models import Cliente
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['telefono']

class RegistroClienteForm(UserCreationForm):
    # Campos del modelo User
    first_name = forms.CharField(max_length=30, required=False, label='Nombre')
    last_name = forms.CharField(max_length=30, required=False, label='Apellido')
    # Campos adicionales del modelo Cliente
    telefono = forms.CharField(max_length=10, required=False, label='Teléfono')

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'telefono']
        labels = {
            'username': 'Nombre de usuario',
            'first_name': 'Nombre',
            'last_name': 'Apellido',
            'email': 'Correo electrónico',
        }

    # Logica de base de datos, agregarlo en infraestructura
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            cliente = Cliente.objects.create(
                user=user,
                telefono=self.cleaned_data['telefono'],
                es_distribuidor=False 
            )
        return user        