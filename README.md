# ChibchaWeb


---

# Requisitos
- Python 3.10 o superior
- Git
- (Opcional pero recomendado) Visual Studio Code

# Crear y activar el entorno virtual:
- python -m venv venv #cres el entono virtual(desde terminal)
- venv\Scripts\activate   #activa el entorno virtual (desde cmd)

# Instalar dependencias
- pip install django
- pip install django-crispy-forms

# Aplicar migraciones
- python manage.py makemigrations
- python manage.py migrate

# Crear superusuario (opcional para admin)
 -python manage.py createsuperuser

# Ejecutar el servidor
- python manage.py runserver

# Direcciones hasta ahora

-http://127.0.0.1:8000/admin → panel de administración (requiere superusuario)
-http://127.0.0.1:8000/clientes/register

# Notas adicionales
La base de datos usada es SQLite (se crea automáticamente).

El entorno virtual y archivos temporales están excluidos vía .gitignore.
