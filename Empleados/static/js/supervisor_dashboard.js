// Supervisor Dashboard JavaScript
// Variables globales para los datos de tickets
let ticketsData = {
    'sin-asignar': [],
    'asignados': []
};

let currentTicketType = '';
let filteredData = [];

// Función para inicializar los datos desde Django
function initializeTicketsData(ticketsSinAsignar, ticketsAsignados) {
    ticketsData['sin-asignar'] = ticketsSinAsignar;
    ticketsData['asignados'] = ticketsAsignados;
}

// Función para inicializar datos con contexto Django
function initializeDashboardData(ticketsSinAsignar, ticketsAsignados, csrfToken) {
    // Inicializar datos de tickets
    initializeTicketsData(ticketsSinAsignar, ticketsAsignados);
    
    // Hacer disponible el CSRF token globalmente
    window.csrfToken = csrfToken;
    
    // Attach event listeners una sola vez
    attachAsignarEventListeners();
    attachEmpleadoEventListeners();
}

// Inicialización automática cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Leer datos desde atributos data- del body
    const body = document.body;
    
    try {
        // Obtener datos de tickets desde atributos data
        const ticketsSinAsignarData = body.getAttribute('data-tickets-sin-asignar');
        const ticketsAsignadosData = body.getAttribute('data-tickets-asignados');
        const csrfToken = body.getAttribute('data-csrf-token');
        
        // Parsear JSON si existen los datos
        const ticketsSinAsignar = ticketsSinAsignarData ? JSON.parse(ticketsSinAsignarData) : [];
        const ticketsAsignados = ticketsAsignadosData ? JSON.parse(ticketsAsignadosData) : [];
        
        // Inicializar dashboard con los datos
        initializeDashboardData(ticketsSinAsignar, ticketsAsignados, csrfToken);
        
    } catch (error) {
        console.error('Error al parsear datos del dashboard:', error);
        // Inicializar con datos vacíos en caso de error
        initializeDashboardData([], [], '');
    }
    
    // Agregar event listeners para limpiar modales cuando se cierren
    setupModalCleanup();
});

// Función para configurar la limpieza de modales
function setupModalCleanup() {
    // Limpiar modal de ticket cuando se cierre
    const ticketModal = document.getElementById('ticketDetalleModal');
    if (ticketModal) {
        ticketModal.addEventListener('hidden.bs.modal', function () {
            // Limpiar el contenido del modal
            const modalBody = this.querySelector('.modal-body');
            if (modalBody) {
                modalBody.innerHTML = '';
            }
            const modalTitle = this.querySelector('.modal-title');
            if (modalTitle) {
                modalTitle.textContent = 'Detalles del Ticket';
            }
        });
    }
    
    // Limpiar modal de empleado cuando se cierre
    const empleadoModal = document.getElementById('empleadoDetalleModal');
    if (empleadoModal) {
        empleadoModal.addEventListener('hidden.bs.modal', function () {
            // Limpiar el contenido del modal
            const modalBody = this.querySelector('.modal-body');
            if (modalBody) {
                modalBody.innerHTML = '';
            }
            const modalTitle = this.querySelector('.modal-title');
            if (modalTitle) {
                modalTitle.textContent = 'Detalles del Empleado';
            }
        });
    }
}

// Funciones para modales de detalles
function verDetallesTicket(ticketId) {
    // Obtener el modal existente
    const modalElement = document.getElementById('ticketDetalleModal');
    if (!modalElement) {
        console.error('Modal ticketDetalleModal no encontrado');
        return;
    }

    // Obtener la instancia existente del modal o crear una nueva si no existe
    let modal = bootstrap.Modal.getInstance(modalElement);
    if (!modal) {
        modal = new bootstrap.Modal(modalElement);
    }

    // Mostrar loading en el contenido del modal antes de mostrarlo
    const modalBody = modalElement.querySelector('.modal-body');
    if (modalBody) {
        modalBody.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-3">Cargando detalles del ticket...</p>
            </div>
        `;
    }

    // Mostrar modal
    modal.show();

    // Obtener el CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                     document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                     window.csrfToken;

    // Hacer petición AJAX para obtener los datos reales del ticket
    fetch(`/empleados/ticket/${ticketId}/detalles/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cargarDatosTicketEnModal(data.ticket, data.historial);
        } else {
            mostrarErrorEnModal('Error al cargar los detalles del ticket: ' + data.error);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarErrorEnModal('Error de conexión al cargar los detalles del ticket');
    });
}

function cargarDatosTicketEnModal(ticketData, historialData) {
    // Restaurar el contenido original del modal
    const modalBody = document.querySelector('#ticketDetalleModal .modal-body');
    if (!modalBody) return;

    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-6">
                <h6><i class="fas fa-info-circle text-primary me-2"></i>Información General</h6>
                <div class="card border-0 bg-light">
                    <div class="card-body p-3">
                        <p><strong>Título:</strong> <span id="ticket-detail-nombre"></span></p>
                        <p><strong>Cliente:</strong> <span id="ticket-detail-cliente"></span></p>
                        <p><strong>Fecha de Creación:</strong> <span id="ticket-detail-fecha"></span></p>
                        <p><strong>Estado:</strong> <span id="ticket-detail-estado" class="badge"></span></p>
                        <p><strong>Prioridad:</strong> <span id="ticket-detail-prioridad" class="badge bg-info">Normal</span></p>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <h6><i class="fas fa-user-tie text-success me-2"></i>Asignación</h6>
                <div class="card border-0 bg-light">
                    <div class="card-body p-3">
                        <p><strong>Agente Asignado:</strong> <span id="ticket-detail-agente"></span></p>
                        <p><strong>Fecha de Asignación:</strong> <span id="ticket-detail-fecha-asignacion"></span></p>
                        <p><strong>Último Contacto:</strong> <span id="ticket-detail-ultimo-contacto"></span></p>
                    </div>
                </div>
            </div>
        </div>
        
        <hr>
        
        <div class="row">
            <div class="col-12">
                <h6><i class="fas fa-file-alt text-info me-2"></i>Descripción del Problema</h6>
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <p id="ticket-detail-descripcion" class="mb-0"></p>
                    </div>
                </div>
            </div>
        </div>

        <hr>

        <div class="row">
            <div class="col-12">
                <h6><i class="fas fa-history text-warning me-2"></i>Historial de Actividades</h6>
                <div class="timeline" id="ticket-detail-timeline">
                    <!-- El historial se cargará dinámicamente -->
                </div>
            </div>
        </div>
    `;

    // Función helper para asignar valor de forma segura
    function setElementText(id, value, isHTML = false) {
        const element = document.getElementById(id);
        if (element) {
            if (isHTML) {
                element.innerHTML = value;
            } else {
                element.textContent = value;
            }
        } else {
            console.warn(`Elemento con ID '${id}' no encontrado`);
        }
    }

    // Título del modal
    const modalTitle = document.querySelector('#ticketDetalleModal .modal-title');
    if (modalTitle) {
        modalTitle.textContent = `Detalles del Ticket ${ticketData.numero}`;
    }

    // Llenar información básica con datos reales
    setElementText('ticket-detail-nombre', ticketData.nombre);
    setElementText('ticket-detail-cliente', ticketData.cliente);
    setElementText('ticket-detail-fecha', ticketData.fecha_creacion);
    setElementText('ticket-detail-agente', ticketData.empleado_asignado);
    setElementText('ticket-detail-fecha-asignacion', ticketData.fecha_asignacion || 'No asignado');
    setElementText('ticket-detail-ultimo-contacto', ticketData.fecha_asignacion || 'Sin contacto');
    setElementText('ticket-detail-descripcion', ticketData.descripcion);

    // Configurar badge del estado con datos reales
    const estadoBadge = document.getElementById('ticket-detail-estado');
    if (estadoBadge) {
        estadoBadge.textContent = ticketData.estado_actual;
        // Asignar color según el estado
        let estadoClass = 'bg-info';
        switch(ticketData.estado_actual.toLowerCase()) {
            case 'resuelto':
                estadoClass = 'bg-success';
                break;
            case 'en proceso':
            case 'asignado':
                estadoClass = 'bg-warning';
                break;
            case 'cerrado':
            case 'cancelado':
                estadoClass = 'bg-danger';
                break;
            case 'pendiente':
                estadoClass = 'bg-warning';
                break;
        }
        estadoBadge.className = `badge ${estadoClass}`;
    }

    // Actualizar el span del número de ticket en el título
    const ticketIdSpan = document.getElementById('ticket-detail-id');
    if (ticketIdSpan) {
        ticketIdSpan.textContent = ticketData.id;
    }

    // Generar timeline con historial real
    const timeline = document.getElementById('ticket-detail-timeline');
    if (timeline) {
        timeline.innerHTML = '';
        
        if (historialData && historialData.length > 0) {
            historialData.forEach(item => {
                const timelineItem = document.createElement('div');
                timelineItem.className = `timeline-item ${item.tipo}`;
                timelineItem.innerHTML = `
                    <div class="timeline-date">${item.fecha}</div>
                    <strong>${item.estado}</strong> - ${item.usuario}
                    <div class="timeline-content">${item.comentario}</div>
                `;
                timeline.appendChild(timelineItem);
            });
        } else {
            timeline.innerHTML = '<p class="text-muted">No hay historial disponible para este ticket.</p>';
        }
    }
}

// Función genérica para mostrar errores en modales
function mostrarErrorEnModal(mensaje, modalId = 'ticketDetalleModal') {
    const modalBody = document.querySelector(`#${modalId} .modal-body`);
    if (modalBody) {
        modalBody.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-exclamation-triangle text-danger fa-3x mb-3"></i>
                <h5 class="text-danger">Error</h5>
                <p>${mensaje}</p>
                <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
            </div>
        `;
    }
}

function verDetallesEmpleado(empleadoId, nombre, email, departamento, telefono, fechaIngreso, estado) {
    // Obtener el modal existente
    const modalElement = document.getElementById('empleadoDetalleModal');
    if (!modalElement) {
        console.error('Modal empleadoDetalleModal no encontrado');
        return;
    }

    // Obtener la instancia existente del modal o crear una nueva si no existe
    let modal = bootstrap.Modal.getInstance(modalElement);
    if (!modal) {
        modal = new bootstrap.Modal(modalElement);
    }

    // Mostrar loading en el contenido del modal antes de mostrarlo
    const modalBody = modalElement.querySelector('.modal-body');
    if (modalBody) {
        modalBody.innerHTML = `
            <div class="text-center py-5">
                <div class="spinner-border text-success" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-3">Cargando información del empleado...</p>
            </div>
        `;
    }

    // Mostrar modal
    modal.show();

    // Obtener el CSRF token
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                     document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                     window.csrfToken;

    // Hacer petición AJAX para obtener los datos reales del empleado
    fetch(`/empleados/empleado/${empleadoId}/detalles/`, {
        method: 'GET',
        headers: {
            'X-CSRFToken': csrfToken,
            'Content-Type': 'application/json',
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            cargarDatosEmpleadoEnModal(data.empleado);
        } else {
            mostrarErrorEnModal('Error al cargar los detalles del empleado: ' + data.error, 'empleadoDetalleModal');
        }
    })
    .catch(error => {
        console.error('Error:', error);
        mostrarErrorEnModal('Error de conexión al cargar los detalles del empleado', 'empleadoDetalleModal');
    });
}

function cargarDatosEmpleadoEnModal(empleadoData) {
    // Restaurar el contenido original del modal
    const modalBody = document.querySelector('#empleadoDetalleModal .modal-body');
    if (!modalBody) return;

    modalBody.innerHTML = `
        <div class="row">
            <div class="col-md-4 text-center">
                <div class="card border-0">
                    <div class="card-body">
                        <div class="avatar-circle bg-primary text-white mb-3 mx-auto" style="width: 80px; height: 80px; border-radius: 50%; display: flex; align-items: center; justify-content: center;">
                            <i class="fas fa-user fa-2x" id="empleado-avatar"></i>
                        </div>
                        <h5 id="empleado-nombre-completo"></h5>
                        <p class="text-muted" id="empleado-username"></p>
                        <span id="empleado-estado-badge" class="badge"></span>
                    </div>
                </div>
            </div>
            <div class="col-md-8">
                <h6><i class="fas fa-info-circle text-primary me-2"></i>Información Personal</h6>
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <div class="row">
                            <div class="col-sm-6">
                                <p><strong>Email:</strong> <span id="empleado-email"></span></p>
                                <p><strong>Teléfono:</strong> <span id="empleado-telefono"></span></p>
                            </div>
                            <div class="col-sm-6">
                                <p><strong>Fecha de Ingreso:</strong> <span id="empleado-fecha-ingreso"></span></p>
                                <p><strong>Nivel:</strong> <span id="empleado-nivel" class="badge bg-info"></span></p>
                            </div>
                        </div>
                    </div>
                </div>

                <h6 class="mt-3"><i class="fas fa-chart-bar text-success me-2"></i>Estadísticas de Trabajo</h6>
                <div class="card border-0 bg-light">
                    <div class="card-body">
                        <div class="row text-center">
                            <div class="col-4">
                                <h4 class="text-primary" id="empleado-tickets-asignados">0</h4>
                                <small class="text-muted">Tickets Asignados</small>
                            </div>
                            <div class="col-4">
                                <h4 class="text-success" id="empleado-tickets-resueltos">0</h4>
                                <small class="text-muted">Tickets Resueltos</small>
                            </div>
                            <div class="col-4">
                                <h4 class="text-warning" id="empleado-tickets-pendientes">0</h4>
                                <small class="text-muted">Tickets Pendientes</small>
                            </div>
                        </div>
                    </div>
                </div>

                <h6 class="mt-3"><i class="fas fa-tasks text-info me-2"></i>Últimos Tickets</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Ticket</th>
                                <th>Cliente</th>
                                <th>Estado</th>
                                <th>Fecha</th>
                            </tr>
                        </thead>
                        <tbody id="empleado-tickets-recientes">
                            <!-- Se cargarán dinámicamente -->
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    `;

    // Función helper para asignar valor de forma segura
    function setElementText(id, value) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        } else {
            console.warn(`Elemento con ID '${id}' no encontrado`);
        }
    }

    // Título del modal
    const modalTitle = document.querySelector('#empleadoDetalleModal .modal-title');
    if (modalTitle) {
        modalTitle.textContent = `Empleado: ${empleadoData.nombre_completo}`;
    }
    
    // Avatar con iniciales
    const avatar = document.getElementById('empleado-avatar');
    if (avatar) {
        const iniciales = empleadoData.nombre_completo.split(' ').map(n => n[0]).join('').toUpperCase();
        avatar.textContent = iniciales;
        avatar.className = '';
        avatar.style.fontSize = '2rem';
    }

    // Información básica con datos reales
    setElementText('empleado-nombre-completo', empleadoData.nombre_completo);
    setElementText('empleado-username', `@${empleadoData.username}`);
    setElementText('empleado-email', empleadoData.email);
    setElementText('empleado-telefono', empleadoData.telefono);
    setElementText('empleado-fecha-ingreso', empleadoData.fecha_ingreso);
    setElementText('empleado-nivel', `Nivel ${empleadoData.nivel}`);

    // Estado badge con datos reales
    const estadoBadge = document.getElementById('empleado-estado-badge');
    if (estadoBadge) {
        estadoBadge.textContent = empleadoData.activo ? 'Activo' : 'Inactivo';
        estadoBadge.className = `badge bg-${empleadoData.activo ? 'success' : 'secondary'}`;
    }

    // Estadísticas con datos reales
    setElementText('empleado-tickets-asignados', empleadoData.estadisticas.tickets_asignados);
    setElementText('empleado-tickets-resueltos', empleadoData.estadisticas.tickets_resueltos);
    setElementText('empleado-tickets-pendientes', empleadoData.estadisticas.tickets_pendientes);

    // Cargar tickets recientes
    const ticketsRecientesBody = document.getElementById('empleado-tickets-recientes');
    if (ticketsRecientesBody && empleadoData.tickets_recientes) {
        if (empleadoData.tickets_recientes.length > 0) {
            ticketsRecientesBody.innerHTML = empleadoData.tickets_recientes.map(ticket => {
                // Determinar clase de badge para el estado
                let badgeClass = 'bg-secondary';
                if (ticket.estado === 'Resuelto') badgeClass = 'bg-success';
                else if (ticket.estado === 'En Proceso') badgeClass = 'bg-warning';
                else if (ticket.estado === 'En espera') badgeClass = 'bg-info';

                return `
                    <tr>
                        <td><strong>${ticket.numero}</strong></td>
                        <td>${ticket.cliente}</td>
                        <td><span class="badge ${badgeClass}">${ticket.estado}</span></td>
                        <td>${ticket.fecha}</td>
                    </tr>
                `;
            }).join('');
        } else {
            ticketsRecientesBody.innerHTML = `
                <tr>
                    <td colspan="4" class="text-center text-muted">
                        <i class="fas fa-info-circle me-2"></i>No hay tickets recientes
                    </td>
                </tr>
            `;
        }
    }
}

// Función para contactar empleado
function contactarEmpleado() {
    // Obtener el email del empleado desde el modal
    const emailElement = document.getElementById('empleado-email');
    const nombreElement = document.getElementById('empleado-nombre-completo');
    
    if (emailElement && nombreElement) {
        const email = emailElement.textContent;
        const nombre = nombreElement.textContent;
        
        // Crear un asunto predeterminado
        const asunto = `Comunicación de Supervisor - ${nombre}`;
        const cuerpo = `Hola ${nombre},\n\nEspero que estés bien. Te contacto desde el panel de supervisión para...\n\n\nSaludos cordiales.`;
        
        // Crear el enlace mailto
        const mailtoLink = `mailto:${email}?subject=${encodeURIComponent(asunto)}&body=${encodeURIComponent(cuerpo)}`;
        
        // Abrir el cliente de correo
        window.location.href = mailtoLink;
    } else {
        alert('No se pudo obtener la información de contacto del empleado.');
    }
}

// Función para mostrar secciones
function showSection(sectionName) {
    // Ocultar todas las secciones
    document.querySelectorAll('.content-section').forEach(section => {
        section.style.display = 'none';
    });
    
    // Mostrar la sección seleccionada
    const targetSection = document.getElementById(sectionName + '-section');
    if (targetSection) {
        targetSection.style.display = 'block';
    }
    
    // Actualizar enlaces activos en la navegación
    document.querySelectorAll('.nav-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Marcar el enlace activo
    const activeLink = document.querySelector(`[href="#${sectionName}"]`);
    if (activeLink) {
        activeLink.classList.add('active');
    }
}

// Función para abrir el modal de tickets
function openTicketModal(type) {
    currentTicketType = type;
    const modal = new bootstrap.Modal(document.getElementById('ticketsModal'));
    
    // Configurar el título del modal
    const titleText = type === 'sin-asignar' ? 'Tickets Sin Asignar' : 'Tickets Asignados';
    document.getElementById('modal-title-text').textContent = titleText;
    
    // Configurar header de tabla
    const headerExtra = document.getElementById('modal-header-extra');
    if (type === 'sin-asignar') {
        headerExtra.textContent = 'Estado';
    } else {
        headerExtra.textContent = 'Asignado a';
    }
    
    // Cargar datos
    filteredData = [...ticketsData[type]];
    renderTicketsTable();
    
    modal.show();
}

// Función para renderizar la tabla de tickets
function renderTicketsTable() {
    const tbody = document.getElementById('modalTicketsTableBody');
    tbody.innerHTML = '';
    
    if (filteredData.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center py-4">
                    <i class="fas fa-search fa-2x text-muted mb-2"></i><br>
                    <span class="text-muted">No se encontraron tickets con los filtros aplicados</span>
                </td>
            </tr>
        `;
    } else {
        filteredData.forEach(ticket => {
            const row = document.createElement('tr');
            
            if (currentTicketType === 'sin-asignar') {
                row.innerHTML = `
                    <td><strong>#${ticket.id}</strong></td>
                    <td>${ticket.nombre}</td>
                    <td>${ticket.cliente}</td>
                    <td>${ticket.fechaFormato}</td>
                    <td><span class="badge bg-warning">${ticket.estado}</span></td>
                    <td>
                        <div class="btn-group">
                            <button type="button" class="btn btn-sm btn-primary dropdown-toggle" 
                                    data-bs-toggle="dropdown" aria-expanded="false">
                                Asignar
                            </button>
                            <ul class="dropdown-menu">
                                ${ticket.agentes.map(agente => `
                                    <li>
                                        <a class="dropdown-item asignar-ticket" href="#" 
                                        data-ticket-id="${ticket.id}" 
                                        data-agente-id="${agente.id}"
                                        data-agente-name="${agente.nombre}">
                                            ${agente.nombre}
                                        </a>
                                    </li>
                                `).join('')}
                            </ul>
                        </div>
                    </td>
                `;
            } else {
                const estadoBadge = getEstadoBadge(ticket.estado);
                row.innerHTML = `
                    <td><strong>#${ticket.id}</strong></td>
                    <td>${ticket.nombre}</td>
                    <td>${ticket.cliente}</td>
                    <td>${ticket.fechaFormato}</td>
                    <td><span class="badge bg-primary">${ticket.agente}</span></td>
                    <td><span class="badge ${estadoBadge.class}">${ticket.estado}</span></td>
                `;
            }
            
            tbody.appendChild(row);
        });
    }
    
    // Actualizar contador
    document.getElementById('contadorResultados').textContent = 
        `Mostrando ${filteredData.length} tickets`;
        
    // Reattach event listeners para los botones de asignar
    attachAsignarEventListeners();
}

// Función para obtener la clase del badge según el estado
function getEstadoBadge(estado) {
    switch(estado) {
        case 'En Proceso': return {class: 'bg-warning'};
        case 'Resuelto': return {class: 'bg-success'};
        case 'Cerrado': return {class: 'bg-secondary'};
        default: return {class: 'bg-info'};
    }
}

// Función para aplicar filtros
function aplicarFiltros() {
    const fechaFiltro = document.getElementById('filtroFecha').value;
    const estadoFiltro = document.getElementById('filtroEstado').value;
    const clienteFiltro = document.getElementById('filtroCliente').value.toLowerCase();
    
    filteredData = ticketsData[currentTicketType].filter(ticket => {
        // Filtro por fecha
        if (fechaFiltro && ticket.fecha !== fechaFiltro) {
            return false;
        }
        
        // Filtro por estado
        if (estadoFiltro && ticket.estado !== estadoFiltro) {
            return false;
        }
        
        // Filtro por cliente
        if (clienteFiltro && !ticket.cliente.toLowerCase().includes(clienteFiltro)) {
            return false;
        }
        
        return true;
    });
    
    renderTicketsTable();
}

// Función para filtros rápidos
function filtroRapido(periodo) {
    const hoy = new Date();
    let fechaLimite;
    
    switch(periodo) {
        case 'hoy':
            fechaLimite = hoy.toISOString().split('T')[0];
            document.getElementById('filtroFecha').value = fechaLimite;
            break;
        case 'semana':
            fechaLimite = new Date(hoy.getTime() - 7 * 24 * 60 * 60 * 1000);
            break;
        case 'mes':
            fechaLimite = new Date(hoy.getTime() - 30 * 24 * 60 * 60 * 1000);
            break;
    }
    
    if (periodo === 'semana' || periodo === 'mes') {
        filteredData = ticketsData[currentTicketType].filter(ticket => {
            const ticketDate = new Date(ticket.fecha);
            return ticketDate >= fechaLimite;
        });
        renderTicketsTable();
    } else {
        aplicarFiltros();
    }
}

// Función para limpiar filtros
function limpiarFiltros() {
    document.getElementById('filtroFecha').value = '';
    document.getElementById('filtroEstado').value = '';
    document.getElementById('filtroCliente').value = '';
    filteredData = [...ticketsData[currentTicketType]];
    renderTicketsTable();
}

// Función para reattach event listeners
function attachAsignarEventListeners() {
    document.querySelectorAll('.asignar-ticket').forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            const ticketId = this.dataset.ticketId;
            const agenteId = this.dataset.agenteId;
            const agenteName = this.dataset.agenteName;
            
            asignarTicket(ticketId, agenteId, agenteName);
        });
    });
}

// Función para attachar event listeners de empleados
function attachEmpleadoEventListeners() {
    // Primero, remover event listeners existentes si los hay
    document.querySelectorAll('.ver-empleado').forEach(function(element) {
        // Crear una nueva copia del elemento para remover todos los event listeners
        const newElement = element.cloneNode(true);
        element.parentNode.replaceChild(newElement, element);
    });
    
    // Ahora agregar los event listeners frescos
    document.querySelectorAll('.ver-empleado').forEach(function(element) {
        element.addEventListener('click', function(e) {
            e.preventDefault();
            const empleadoId = this.dataset.empleadoId;
            const nombre = this.dataset.empleadoNombre;
            const email = this.dataset.empleadoEmail;
            const username = this.dataset.empleadoUsername;
            const activo = this.dataset.empleadoActivo;
            const fechaIngreso = this.dataset.empleadoFechaIngreso;
            
            // Llamar a la función de ver detalles con los datos del botón
            verDetallesEmpleado(empleadoId, nombre, email, username, '', fechaIngreso, activo);
        });
    });
}

// Función para asignar tickets
function asignarTicket(ticketId, agenteId, agenteNombre) {
    if (confirm(`¿Estás seguro de asignar este ticket a ${agenteNombre}?`)) {
        // Mostrar indicador de carga en el botón
        const buttons = document.querySelectorAll('.dropdown-toggle');
        buttons.forEach(button => {
            if (button.textContent.includes('Asignar')) {
                button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Asignando...';
                button.disabled = true;
            }
        });
        
        // Obtener el CSRF token
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
                         document.querySelector('meta[name="csrf-token"]')?.getAttribute('content') ||
                         window.csrfToken;
        
        fetch('/empleados/asignar-ticket/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': csrfToken
            },
            body: `ticket_id=${ticketId}&agente_id=${agenteId}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Mostrar mensaje de éxito
                const alertDiv = document.createElement('div');
                alertDiv.className = 'alert alert-success alert-dismissible fade show mt-3';
                alertDiv.innerHTML = `
                    <i class="fas fa-check-circle"></i> ${data.message}
                    <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
                `;
                
                // Insertar el alert en la parte superior del panel
                const cardBody = document.querySelector('.card-body');
                if (cardBody) {
                    cardBody.insertBefore(alertDiv, cardBody.firstChild);
                }
                
                // Recargar después de 2 segundos
                setTimeout(() => {
                    location.reload();
                }, 2000);
            } else {
                alert('Error: ' + data.error);
                location.reload();
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Error al asignar el ticket');
            location.reload();
        });
    }
}

// Inicialización cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', function() {
    // Event delegation para botones de asignar ticket existentes
    attachAsignarEventListeners();
    attachEmpleadoEventListeners();
});
