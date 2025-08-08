from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from Empleados.models import Empleado
from Clientes.models import Cliente
from Administradores.models import Administrador


class CrearUsuarioForm(UserCreationForm):
    TIPO_CHOICES = [
        ('cliente', _('Cliente')),
        ('empleado', _('Empleado')),
        ('administrador', _('Administrador')),
    ]
    
    ROL_EMPLEADO_CHOICES = [
        ('agente', _('Agente')),
        ('supervisor', _('Supervisor')),
    ]
    
    email = forms.EmailField(
        required=True,
        label=_('Email'),
        help_text=_('Ingrese una dirección de correo electrónico válida')
    )
    first_name = forms.CharField(
        max_length=30, 
        required=True, 
        label=_('Nombre'),
        help_text=_('Nombre del usuario')
    )
    last_name = forms.CharField(
        max_length=30, 
        required=True, 
        label=_('Apellido'),
        help_text=_('Apellido del usuario')
    )
    tipo_usuario = forms.ChoiceField(
        choices=TIPO_CHOICES, 
        required=True, 
        label=_('Tipo de Usuario'),
        help_text=_('Seleccione el tipo de perfil para el usuario')
    )
    telefono = forms.CharField(
        max_length=15, 
        required=False, 
        label=_('Teléfono'),
        help_text=_('Número de teléfono (opcional)')
    )
    rol_empleado = forms.ChoiceField(
        choices=ROL_EMPLEADO_CHOICES, 
        required=False,
        label=_('Rol de Empleado'),
        help_text=_('Solo requerido si el tipo de usuario es Empleado')
    )
    
    # Campos adicionales para personalización
    enviar_email_bienvenida = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Enviar email de bienvenida'),
        help_text=_('Enviar credenciales de acceso por correo electrónico')
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
        labels = {
            'username': _('Nombre de Usuario'),
            'password1': _('Contraseña'),
            'password2': _('Confirmar Contraseña'),
        }
        help_texts = {
            'username': _('Requerido. 150 caracteres o menos. Letras, dígitos y @/./+/-/_ únicamente.'),
            'password1': _('Su contraseña debe contener al menos 8 caracteres.'),
            'password2': _('Ingrese la misma contraseña que antes, para verificación.'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agregar clases CSS para Bootstrap
        for field_name, field in self.fields.items():
            if field_name in ['enviar_email_bienvenida']:
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Placeholders útiles con traducción
        self.fields['username'].widget.attrs.update({
            'placeholder': _('Nombre de usuario único')
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': _('correo@ejemplo.com')
        })
        self.fields['first_name'].widget.attrs.update({
            'placeholder': _('Nombres del usuario')
        })
        self.fields['last_name'].widget.attrs.update({
            'placeholder': _('Apellidos del usuario')
        })
        self.fields['telefono'].widget.attrs.update({
            'placeholder': _('Ej: +57 300 123 4567')
        })
        
        # Atributos adicionales para mejor UX
        self.fields['password1'].widget.attrs.update({
            'autocomplete': 'new-password'
        })
        self.fields['password2'].widget.attrs.update({
            'autocomplete': 'new-password'
        })
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Ya existe un usuario con este email."))
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError(_("Ya existe un usuario con este nombre de usuario."))
        return username
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono:
            # Validación básica de teléfono
            import re
            if not re.match(r'^[\+\d\s\-\(\)]{7,15}$', telefono):
                raise ValidationError(_("Formato de teléfono inválido."))
        return telefono
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        rol_empleado = cleaned_data.get('rol_empleado')
        
        # Si es empleado, el rol es obligatorio
        if tipo_usuario == 'empleado' and not rol_empleado:
            self.add_error('rol_empleado', _('El rol es obligatorio para empleados.'))
        
        return cleaned_data


class EditarUsuarioForm(forms.ModelForm):
    # Campos adicionales para gestionar perfiles específicos
    activo = forms.BooleanField(
        required=False, 
        initial=True, 
        label=_('Perfil Activo'),
        help_text=_('Determina si el perfil específico está activo')
    )
    telefono = forms.CharField(
        max_length=15, 
        required=False, 
        label=_('Teléfono'),
        help_text=_('Número de teléfono del usuario')
    )
    
    # Campos específicos para empleados
    rol_empleado = forms.ChoiceField(
        choices=[
            ('agente', _('Agente')), 
            ('supervisor', _('Supervisor'))
        ],
        required=False,
        label=_('Rol de Empleado'),
        help_text=_('Rol asignado al empleado')
    )
    nivel_empleado = forms.ChoiceField(
        choices=[
            (1, _('Nivel 1')), 
            (2, _('Nivel 2')), 
            (3, _('Nivel 3'))
        ],
        required=False,
        label=_('Nivel de Acceso'),
        help_text=_('Nivel de permisos del empleado')
    )
    
    # Campo para cambiar tipo de usuario
    tipo_usuario = forms.ChoiceField(
        choices=[
            ('cliente', _('Cliente')),
            ('empleado', _('Empleado')),
            ('administrador', _('Administrador')),
        ],
        required=False,
        label=_('Tipo de Usuario'),
        help_text=_('Cambiar el tipo de perfil del usuario')
    )
    
    # Campos adicionales para administradores
    puede_gestionar_usuarios = forms.BooleanField(
        required=False,
        label=_('Puede Gestionar Usuarios'),
        help_text=_('Permite al administrador crear, editar y eliminar usuarios')
    )
    puede_ver_estadisticas = forms.BooleanField(
        required=False,
        label=_('Puede Ver Estadísticas'),
        help_text=_('Permite al administrador acceder a reportes y estadísticas')
    )
    puede_gestionar_pagos = forms.BooleanField(
        required=False,
        label=_('Puede Gestionar Pagos'),
        help_text=_('Permite al administrador gestionar información de pagos')
    )
    
    # Campos adicionales para clientes
    plan_cliente = forms.ChoiceField(
        choices=[
            ('basico', _('Básico')),
            ('profesional', _('Profesional')),
            ('empresarial', _('Empresarial')),
        ],
        required=False,
        label=_('Plan del Cliente'),
        help_text=_('Plan de hosting asignado al cliente')
    )
    tiene_suscripcion = forms.BooleanField(
        required=False,
        label=_('Tiene Suscripción Activa'),
        help_text=_('Indica si el cliente tiene una suscripción activa')
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'is_active')
        labels = {
            'username': _('Nombre de Usuario'),
            'email': _('Email'),
            'first_name': _('Nombre'),
            'last_name': _('Apellido'),
            'is_active': _('Usuario Activo'),
        }
        help_texts = {
            'username': _('Nombre único para identificar al usuario'),
            'email': _('Dirección de correo electrónico'),
            'first_name': _('Nombre(s) del usuario'),
            'last_name': _('Apellido(s) del usuario'),
            'is_active': _('Determina si el usuario puede iniciar sesión'),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Agregar clases CSS
        for field_name, field in self.fields.items():
            if field_name in ['activo', 'is_active', 'puede_gestionar_usuarios', 
                            'puede_ver_estadisticas', 'puede_gestionar_pagos', 
                            'tiene_suscripcion']:
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Placeholders
        self.fields['telefono'].widget.attrs.update({
            'placeholder': _('Ej: +57 300 123 4567')
        })
        
        # Si el usuario existe, cargar información adicional
        if self.instance and self.instance.pk:
            user = self.instance
            
            # Determinar tipo actual y cargar datos
            if hasattr(user, 'cliente'):
                self.fields['tipo_usuario'].initial = 'cliente'
                cliente = user.cliente
                self.fields['telefono'].initial = getattr(cliente, 'telefono', '')
                self.fields['activo'].initial = getattr(cliente, 'activo', True)
                self.fields['plan_cliente'].initial = getattr(cliente, 'plan', 'basico')
                self.fields['tiene_suscripcion'].initial = getattr(cliente, 'tiene_suscripcion', False)
                
            elif hasattr(user, 'empleado'):
                self.fields['tipo_usuario'].initial = 'empleado'
                empleado = user.empleado
                self.fields['telefono'].initial = getattr(empleado, 'telefono', '')
                self.fields['activo'].initial = empleado.activo
                self.fields['rol_empleado'].initial = empleado.rol
                self.fields['nivel_empleado'].initial = empleado.nivel
                
            elif hasattr(user, 'administrador'):
                self.fields['tipo_usuario'].initial = 'administrador'
                admin = user.administrador
                self.fields['activo'].initial = admin.activo
                self.fields['puede_gestionar_usuarios'].initial = getattr(admin, 'puede_gestionar_usuarios', True)
                self.fields['puede_ver_estadisticas'].initial = getattr(admin, 'puede_ver_estadisticas', True)
                self.fields['puede_gestionar_pagos'].initial = getattr(admin, 'puede_gestionar_pagos', True)
                
            else:
                self.fields['tipo_usuario'].initial = 'cliente'  # Por defecto
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(id=self.instance.id).exists():
            raise ValidationError(_("Ya existe un usuario con este email."))
        return email
    
    def clean_telefono(self):
        telefono = self.cleaned_data.get('telefono', '').strip()
        if telefono:
            import re
            if not re.match(r'^[\+\d\s\-\(\)]{7,15}$', telefono):
                raise ValidationError(_("Formato de teléfono inválido."))
        return telefono
    
    def clean(self):
        cleaned_data = super().clean()
        tipo_usuario = cleaned_data.get('tipo_usuario')
        rol_empleado = cleaned_data.get('rol_empleado')
        
        # Si se cambia a empleado, el rol es obligatorio
        if tipo_usuario == 'empleado' and not rol_empleado:
            self.add_error('rol_empleado', _('El rol es obligatorio para empleados.'))
        
        return cleaned_data


class FiltroUsuariosForm(forms.Form):
    TIPO_CHOICES = [
        ('all', _('Todos')),
        ('cliente', _('Clientes')),
        ('empleado', _('Empleados')),
        ('administrador', _('Administradores')),
    ]
    
    ESTADO_CHOICES = [
        ('all', _('Todos')),
        ('true', _('Activos')),
        ('false', _('Inactivos')),
    ]
    
    ORDENAR_CHOICES = [
        ('username', _('Nombre de Usuario')),
        ('-date_joined', _('Fecha de Registro (Recientes)')),
        ('date_joined', _('Fecha de Registro (Antiguos)')),
        ('first_name', _('Nombre')),
        ('email', _('Email')),
    ]
    
    tipo = forms.ChoiceField(
        choices=TIPO_CHOICES, 
        required=False, 
        initial='all',
        label=_('Tipo de Usuario'),
        help_text=_('Filtrar por tipo de perfil')
    )
    busqueda = forms.CharField(
        max_length=100, 
        required=False, 
        label=_('Buscar'),
        help_text=_('Buscar por nombre, usuario o email')
    )
    activo = forms.ChoiceField(
        choices=ESTADO_CHOICES,
        required=False,
        initial='all',
        label=_('Estado'),
        help_text=_('Filtrar por estado del usuario')
    )
    ordenar = forms.ChoiceField(
        choices=ORDENAR_CHOICES,
        required=False,
        initial='username',
        label=_('Ordenar por'),
        help_text=_('Criterio de ordenamiento')
    )
    
    # Filtros adicionales
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Registrado desde'),
        help_text=_('Mostrar usuarios registrados desde esta fecha')
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Registrado hasta'),
        help_text=_('Mostrar usuarios registrados hasta esta fecha')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Placeholders
        self.fields['busqueda'].widget.attrs.update({
            'placeholder': _('Buscar usuarios...')
        })
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            raise ValidationError(_('La fecha "desde" debe ser anterior a la fecha "hasta".'))
        
        return cleaned_data


class FiltroEstadisticasForm(forms.Form):
    PERIODO_CHOICES = [
        ('7', _('Últimos 7 días')),
        ('30', _('Últimos 30 días')),
        ('90', _('Últimos 3 meses')),
        ('365', _('Último año')),
        ('custom', _('Personalizado')),
    ]
    
    TIPO_ESTADISTICA_CHOICES = [
        ('general', _('Estadísticas Generales')),
        ('usuarios', _('Usuarios')),
        ('pagos', _('Pagos')),
        ('hosting', _('Solo Hosting')),
        ('distribuidores', _('Solo Distribuidores')),
    ]
    
    periodo = forms.ChoiceField(
        choices=PERIODO_CHOICES, 
        required=False, 
        initial='30',
        label=_('Período de Tiempo'),
        help_text=_('Seleccione el rango temporal para las estadísticas')
    )
    fecha_inicio = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Fecha de Inicio'),
        help_text=_('Solo para período personalizado')
    )
    fecha_fin = forms.DateField(
        required=False, 
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Fecha de Fin'),
        help_text=_('Solo para período personalizado')
    )
    tipo_estadistica = forms.ChoiceField(
        choices=TIPO_ESTADISTICA_CHOICES,
        required=False,
        initial='general',
        label=_('Tipo de Estadística'),
        help_text=_('Seleccione el tipo de reporte a generar')
    )
    incluir_inactivos = forms.BooleanField(
        required=False,
        label=_('Incluir Usuarios Inactivos'),
        help_text=_('Incluir usuarios desactivados en las estadísticas')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'incluir_inactivos':
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        periodo = cleaned_data.get('periodo')
        fecha_inicio = cleaned_data.get('fecha_inicio')
        fecha_fin = cleaned_data.get('fecha_fin')
        
        if periodo == 'custom':
            if not fecha_inicio or not fecha_fin:
                raise ValidationError(_("Para período personalizado, debe especificar ambas fechas."))
            if fecha_inicio > fecha_fin:
                raise ValidationError(_("La fecha de inicio debe ser anterior a la fecha de fin."))
        
        return cleaned_data


class ConfiguracionAdminForm(forms.ModelForm):
    """Formulario para configurar permisos específicos de administrador"""
    
    class Meta:
        model = Administrador
        fields = [
            'puede_gestionar_usuarios', 
            'puede_ver_estadisticas', 
            'puede_gestionar_pagos'
        ]
        labels = {
            'puede_gestionar_usuarios': _('Gestionar Usuarios'),
            'puede_ver_estadisticas': _('Ver Estadísticas'),
            'puede_gestionar_pagos': _('Gestionar Pagos'),
        }
        help_texts = {
            'puede_gestionar_usuarios': _('Permite crear, editar y eliminar usuarios del sistema'),
            'puede_ver_estadisticas': _('Permite acceso a reportes y estadísticas del sistema'),
            'puede_gestionar_pagos': _('Permite gestionar información relacionada con pagos'),
        }
        widgets = {
            'puede_gestionar_usuarios': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_ver_estadisticas': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'puede_gestionar_pagos': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class BusquedaAvanzadaForm(forms.Form):
    """Formulario para búsqueda avanzada de usuarios"""
    
    # Campos de búsqueda
    nombre_completo = forms.CharField(
        max_length=100,
        required=False,
        label=_('Nombre Completo'),
        help_text=_('Buscar por nombre y apellido')
    )
    email_contiene = forms.CharField(
        max_length=100,
        required=False,
        label=_('Email contiene'),
        help_text=_('Buscar emails que contengan este texto')
    )
    username_contiene = forms.CharField(
        max_length=100,
        required=False,
        label=_('Usuario contiene'),
        help_text=_('Buscar nombres de usuario que contengan este texto')
    )
    
    # Filtros de fecha
    registrado_desde = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label=_('Registrado desde'),
        help_text=_('Usuarios registrados después de esta fecha y hora')
    )
    registrado_hasta = forms.DateTimeField(
        required=False,
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        label=_('Registrado hasta'),
        help_text=_('Usuarios registrados antes de esta fecha y hora')
    )
    
    # Filtros específicos
    tiene_telefono = forms.ChoiceField(
        choices=[
            ('', _('Todos')),
            ('si', _('Con teléfono')),
            ('no', _('Sin teléfono')),
        ],
        required=False,
        label=_('Teléfono'),
        help_text=_('Filtrar por presencia de número telefónico')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Placeholders
        self.fields['nombre_completo'].widget.attrs.update({
            'placeholder': _('Ej: Juan Pérez')
        })
        self.fields['email_contiene'].widget.attrs.update({
            'placeholder': _('Ej: gmail.com')
        })
        self.fields['username_contiene'].widget.attrs.update({
            'placeholder': _('Ej: admin')
        })


class ExportarDatosForm(forms.Form):
    """Formulario para exportar datos del sistema"""
    
    FORMATO_CHOICES = [
        ('csv', _('CSV')),
        ('excel', _('Excel (.xlsx)')),
        ('pdf', _('PDF')),
    ]
    
    DATOS_CHOICES = [
        ('usuarios', _('Lista de Usuarios')),
        ('pagos', _('Historial de Pagos')),
        ('estadisticas', _('Estadísticas Generales')),
        ('clientes', _('Solo Clientes')),
        ('empleados', _('Solo Empleados')),
        ('administradores', _('Solo Administradores')),
    ]
    
    tipo_datos = forms.ChoiceField(
        choices=DATOS_CHOICES,
        required=True,
        label=_('Tipo de Datos'),
        help_text=_('Seleccione qué información exportar')
    )
    formato = forms.ChoiceField(
        choices=FORMATO_CHOICES,
        required=True,
        initial='excel',
        label=_('Formato de Exportación'),
        help_text=_('Formato del archivo a generar')
    )
    incluir_inactivos = forms.BooleanField(
        required=False,
        label=_('Incluir Usuarios Inactivos'),
        help_text=_('Incluir usuarios desactivados en la exportación')
    )
    fecha_desde = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Desde Fecha'),
        help_text=_('Solo datos desde esta fecha (opcional)')
    )
    fecha_hasta = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date'}),
        label=_('Hasta Fecha'),
        help_text=_('Solo datos hasta esta fecha (opcional)')
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == 'incluir_inactivos':
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})
    
    def clean(self):
        cleaned_data = super().clean()
        fecha_desde = cleaned_data.get('fecha_desde')
        fecha_hasta = cleaned_data.get('fecha_hasta')
        
        if fecha_desde and fecha_hasta and fecha_desde > fecha_hasta:
            raise ValidationError(_('La fecha "desde" debe ser anterior a la fecha "hasta".'))
        
        return cleaned_data