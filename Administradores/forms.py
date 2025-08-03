from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


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
    tipo_usuario = forms.ChoiceField(choices=TIPO_CHOICES, required=True)
    telefono = forms.CharField(max_length=15, required=False)
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
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['first_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['last_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['tipo_usuario'].widget.attrs.update({'class': 'form-control'})
        self.fields['telefono'].widget.attrs.update({'class': 'form-control'})
        self.fields['rol_empleado'].widget.attrs.update({'class': 'form-control'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError("Ya exists un usuario con este email.")
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
    activo = forms.BooleanField(required=False, initial=True)
    telefono = forms.CharField(max_length=15, required=False)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agregar clases CSS
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        
        # Si el usuario tiene un perfil específico, obtener información adicional
        if self.instance:
            if hasattr(self.instance, 'cliente'):
                self.fields['telefono'].initial = getattr(self.instance.cliente, 'telefono', '')
                self.fields['activo'].initial = getattr(self.instance.cliente, 'activo', True)
            elif hasattr(self.instance, 'empleado'):
                self.fields['telefono'].initial = getattr(self.instance.empleado, 'telefono', '')
                self.fields['activo'].initial = self.instance.empleado.activo
            elif hasattr(self.instance, 'administrador'):
                self.fields['activo'].initial = self.instance.administrador.activo
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError("Ya existe un usuario con este email.")
        return email


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