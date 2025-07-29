from django import forms
from .models import Cliente
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['telefono', 'metodoPago']

class RegistroClienteForm(UserCreationForm):
    # Campos adicionales del modelo Cliente
    telefono = forms.CharField(max_length=15, required=False, label='Teléfono')
    metodoPago = forms.BooleanField(required=False, label='¿Tiene método de pago activo?')

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'telefono', 'metodoPago']
        labels = {
            'email': 'Correo electrónico',
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            cliente = Cliente.objects.create(
                user=user,
                telefono=self.cleaned_data['telefono'],
                metodoPago=self.cleaned_data['metodoPago']
            )
        return user        