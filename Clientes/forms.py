from django import forms
from .models import Cliente
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.utils.translation import gettext_lazy as _

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['telefono']
        labels = {
            'telefono': _('Teléfono'),
        }
        help_texts = {
            'telefono': _('Ingresa tu número de teléfono'),
        }

class RegistroClienteForm(UserCreationForm):
    # Campos del modelo User
    first_name = forms.CharField(
        max_length=30, 
        required=False, 
        label=_('Nombre'),
        help_text=_('Opcional. Máximo 30 caracteres.')
    )
    last_name = forms.CharField(
        max_length=30, 
        required=False, 
        label=_('Apellido'),
        help_text=_('Opcional. Máximo 30 caracteres.')
    )
    
    # Campos adicionales del modelo Cliente
    telefono = forms.CharField(
        max_length=10, 
        required=False, 
        label=_('Teléfono'),
        help_text=_('Opcional. Formato: 3001234567')
    )
    
    # Sobrescribir el campo email para hacerlo obligatorio y con label traducido
    email = forms.EmailField(
        required=True,
        label=_('Correo electrónico'),
        help_text=_('Requerido. Ingresa una dirección de correo válida.')
    )

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2', 'telefono']
        labels = {
            'username': _('Nombre de usuario'),
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
            'email': _('Correo electrónico'),
        }
        help_texts = {
            'username': _('Requerido. 150 caracteres máximo. Solo letras, dígitos y @/./+/-/_.'),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Personalizar labels y help_texts de los campos de contraseña
        self.fields['password1'].label = _('Contraseña')
        self.fields['password1'].help_text = _(
            'Tu contraseña debe contener al menos 8 caracteres, '
            'no puede ser muy común y no puede ser completamente numérica.'
        )
        
        self.fields['password2'].label = _('Confirmar contraseña')
        self.fields['password2'].help_text = _(
            'Ingresa la misma contraseña anterior para verificación.'
        )
        
        # Personalizar placeholders si quieres
        self.fields['username'].widget.attrs.update({
            'placeholder': _('Ingresa tu nombre de usuario')
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': _('ejemplo@correo.com')
        })
        self.fields['first_name'].widget.attrs.update({
            'placeholder': _('Tu nombre')
        })
        self.fields['last_name'].widget.attrs.update({
            'placeholder': _('Tu apellido')
        })
        self.fields['telefono'].widget.attrs.update({
            'placeholder': _('3001234567')
        })

    def clean_email(self):
        """Validar que el email no esté ya registrado"""
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(_('Ya existe un usuario con este correo electrónico.'))
        return email

    def clean_telefono(self):
        """Validar formato del teléfono (opcional)"""
        telefono = self.cleaned_data.get('telefono')
        if telefono and not telefono.isdigit():
            raise forms.ValidationError(_('El teléfono debe contener solo números.'))
        if telefono and len(telefono) != 10:
            raise forms.ValidationError(_('El teléfono debe tener exactamente 10 dígitos.'))
        return telefono

    # Logica de base de datos, agregarlo en infraestructura
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.is_active = False  # No activo hasta confirmar correo
        if commit:
            user.save()
            cliente = Cliente.objects.create(
                user=user,
                telefono=self.cleaned_data['telefono'],
                es_distribuidor=False 
            )
        return user