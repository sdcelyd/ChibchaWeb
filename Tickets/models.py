from django.db import models
from django.utils import timezone
from Clientes.models import Cliente
from Empleados.models import Empleado

# Tabla Estado
class Estado(models.Model):
    idEstado = models.IntegerField(primary_key=True)
    nombreEstado = models.CharField(max_length=50)

    class Meta:
        db_table = 'Estado'

    def __str__(self):
        return self.nombreEstado

# Tabla Ticket
class Ticket(models.Model):
    idTicket = models.AutoField(primary_key=True)
    nombreTicket = models.CharField(max_length=50)
    descripcionTicket = models.CharField(max_length=250)
    fechar_creacion = models.DateField(default=timezone.now)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, db_column='clienteId')

    class Meta:
        db_table = 'Ticket'

    def __str__(self):
        cliente_nombre = f"{self.cliente.user.first_name} {self.cliente.user.last_name}".strip()
        if not cliente_nombre:
            cliente_nombre = self.cliente.user.username
        return f"{self.nombreTicket} - Cliente: {cliente_nombre}"

# Tabla HistoriaTicket
class HistoriaTicket(models.Model):
    idCambioTicket = models.AutoField(primary_key=True)
    modDescripcion = models.CharField(max_length=250)
    fecha_modificacion = models.DateField(default=timezone.now)
    empleado = models.ForeignKey(Empleado, null=True, blank=True, on_delete=models.SET_NULL, db_column='idEmpleado')
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, db_column='idTicket', related_name='historial')
    estado = models.ForeignKey(Estado, null=True, on_delete=models.SET_NULL, db_column='idEstado')

    class Meta:
        db_table = 'HistoriaTicket'

    def __str__(self):
        return f"Cambio en ticket {self.ticket.idTicket} a estado {self.estado.nombreEstado}"
