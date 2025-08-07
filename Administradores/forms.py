from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from Empleados.models import Empleado
from Clientes.models import Cliente
from Administradores.models import Administrador


class CrearUsuarioForm(UserCreationForm):
    TIPO_CHOICES = [
        ('cliente', 'Cliente'),
        ('empleado', 'Empleado'),
        ('administrador', 'Administrador'),
    ]
    
    ROL_EMPLEADO_CHOICES = [
        ('agente', 'Agente'),
        ('supervisor', 'Supervisor'),
    ]
    
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True, label='Nombre')
    last_name = forms.CharField(max_length=30, required=True, label='Apellido')
    tipo_usuario = forms.ChoiceField(choices=TIPO_CHOICES, required=True, label='Tipo de Usuario')
    telefono = forms.CharField(max_length=15, required=False, label='Teléfono')
    rol_empleado = forms.ChoiceField(
        choices=ROL_EMPLEADO_CHOICES, 
        required=False,
        label='Rol de Empleado'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agregar clases CSS para Bootstrap
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Placeholders útiles
        self.fields['username'].widget.attrs.update({'placeholder': 'Nombre de usuario único'})
        self.fields['email'].widget.attrs.update({'placeholder': 'correo@ejemplo.com'})
        self.fields['telefono'].widget.attrs.update({'placeholder': 'Opcional - ej: 3001234567'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya existe un usuario con este email.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        rol_empleado = cleaned_data.get('rol_empleado')
        
        # Si es empleado, el rol es obligatorio
        if tipo_usuario == 'empleado' and not rol_empleado:
            self.add_error('rol_empleado', 'El rol es obligatorio para empleados.')
        
        return cleaned_data


class EditarUsuarioForm(forms.ModelForm):
    # Campos adicionales para gestionar perfiles específicos
    activo = forms.BooleanField(required=False, initial=True, label='Perfil Activo')
    telefono = forms.CharField(max_length=15, required=False, label='Teléfono')
    
    # Campos específicos para empleados
    rol_empleado = forms.ChoiceField(
        choices=[('agente', 'Agente'), ('supervisor', 'Supervisor')],
        required=False,
        label='Rol de Empleado'
    )
    nivel_empleado = forms.ChoiceField(
        choices=[(1, 'Nivel 1'), (2, 'Nivel 2'), (3, 'Nivel 3')],
        required=False,
        label='Nivel de Acceso'
    )
    
    # Campo para cambiar tipo de usuario
    tipo_usuario = forms.ChoiceField(
        choices=[
            ('cliente', 'Cliente'),
            ('empleado', 'Empleado'),
            ('administrador', 'Administrador'),
        ],
        required=False,
        label='Tipo de Usuario'
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agregar clases CSS
        for field in self.fields:
            if field in ['activo', 'is_active']:
                self.fields[field].widget.attrs.update({'class': 'form-check-input'})
            else:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Si el usuario existe, cargar información adicional
        if self.instance and self.instance.pk:
            user = self.instance
            
            # Determinar tipo actual y cargar datos
            if hasattr(user, 'cliente'):
                self.fields['tipo_usuario'].initial = 'cliente'
                self.fields['telefono'].initial = getattr(user.cliente, 'telefono', '')
                self.fields['activo'].initial = getattr(user.cliente, 'activo', True)
            elif hasattr(user, 'empleado'):
                self.fields['tipo_usuario'].initial = 'empleado'
                self.fields['telefono'].initial = getattr(user.empleado, 'telefono', '')
                self.fields['activo'].initial = user.empleado.activo
                self.fields['rol_empleado'].initial = user.empleado.rol
                self.fields['nivel_empleado'].initial = user.empleado.nivel
            elif hasattr(user, 'administrador'):
                self.fields['tipo_usuario'].initial = 'administrador'
                self.fields['activo'].initial = user.administrador.activo
            else:
                self.fields['tipo_usuario'].initial = 'cliente'  # Por defecto
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError("Ya existe un usuario con este email.")
        return email
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        rol_empleado = cleaned_data.get('rol_empleado')
        
        # Si se cambia a empleado, el rol es obligatorio
        if tipo_usuario == 'empleado' and not rol_empleado:
            self.add_error('rol_empleado', 'El rol es obligatorio para empleados.')
        
        return cleaned_data


class FiltroUsuariosForm(forms.Form):
    TIPO_CHOICES = [
        ('all', 'Todos'),
        ('cliente', 'Clientes'),
        ('empleado', 'Empleados'),
        ('administrador', 'Administradores'),
    ]
    
    tipo = forms.ChoiceField(choices=TIPO_CHOICES, required=False, initial='all')
    busqueda = forms.CharField(max_length=100, required=False, label='Buscar')
    activo = forms.ChoiceField(
        choices=[('all', 'Todos'), ('true', 'Activos'), ('false', 'Inactivos')],
        required=False,
        initial='all'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})


class FiltroEstadisticasForm(forms.Form):
    PERIODO_CHOICES = [
        ('7', 'Últimos 7 días'),
        ('30', 'Últimos 30 días'),
        ('90', 'Últimos 3 meses'),
        ('365', 'Último año'),
        ('custom', 'Personalizado'),
    ]
    
    periodo = forms.ChoiceField(choices=PERIODO_CHOICES, required=False, initial='30')
    fecha_inicio = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    fecha_fin = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        periodo = cleaned_data.get('periodo')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if periodo == 'custom':
            if not fecha_inicio or not fecha_fin:
                raise ValidationError("Para período personalizado, debe especificar ambas fechas.")
            if fecha_inicio > fecha_fin:
                raise ValidationError("La fecha de inicio debe ser anterior a la fecha de fin.")
        
        return cleaned_data