// Agente Dashboard JavaScript
let ticketIdActual = null;

// Helper function para obtener CSRF token
function obtenerCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]') ? 
           document.querySelector('[name=csrfmiddlewaretoken]').value : 
           document.body.dataset.csrfToken;
}

// Helper function para realizar requests AJAX
function realizarRequestTicket(url, data, modalId) {
    const csrfToken = obtenerCsrfToken();
    
    return fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrfToken
        },
        body: new URLSearchParams(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('✅ ' + data.message);
            location.reload();
        } else {
            alert('❌ Error: ' + data.error);
        }
        bootstrap.Modal.getInstance(document.getElementById(modalId)).hide();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('❌ Error al procesar el ticket');
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', function() {
    // Botones de resolver
    document.querySelectorAll('.btn-resolver').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const ticketId = this.dataset.ticketId;
            const ticketNombre = this.dataset.ticketNombre;
            resolverTicket(ticketId, ticketNombre);
        });
    });

    // Botones de escalar
    document.querySelectorAll('.btn-escalar').forEach(function(btn) {
        btn.addEventListener('click', function() {
            const ticketId = this.dataset.ticketId;
            const ticketNombre = this.dataset.ticketNombre;
            const nivelActual = parseInt(this.dataset.nivelActual);
            escalarTicket(ticketId, ticketNombre, nivelActual);
        });
    });
});

function resolverTicket(ticketId, ticketNombre) {
    ticketIdActual = ticketId;
    document.getElementById('ticketNombreResolver').textContent = ticketNombre;
    document.getElementById('comentarioResolver').value = '';
    new bootstrap.Modal(document.getElementById('resolverModal')).show();
}

function escalarTicket(ticketId, ticketNombre, nivelActual) {
    ticketIdActual = ticketId;
    document.getElementById('ticketNombreEscalar').textContent = ticketNombre;
    document.getElementById('nivelActual').textContent = nivelActual;
    document.getElementById('nivelSiguiente').textContent = nivelActual + 1;
    document.getElementById('comentarioEscalar').value = '';
    new bootstrap.Modal(document.getElementById('escalarModal')).show();
}

function confirmarResolver() {
    const comentario = document.getElementById('comentarioResolver').value;
    
    realizarRequestTicket('/empleados/resolver-ticket/', {
        ticket_id: ticketIdActual,
        comentario: comentario
    }, 'resolverModal');
}

function confirmarEscalar() {
    const comentario = document.getElementById('comentarioEscalar').value;
    
    if (!comentario.trim()) {
        alert('⚠️ El motivo del escalamiento es requerido');
        return;
    }
    
    realizarRequestTicket('/empleados/escalar-ticket/', {
        ticket_id: ticketIdActual,
        comentario: comentario
    }, 'escalarModal');
}

// Función para hacer scroll a una sección específica
function scrollToSection(sectionId) {
    const element = document.getElementById(sectionId);
    if (element) {
        element.scrollIntoView({ 
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Función para mostrar/ocultar todos los tickets
function toggleAllTickets(tipo) {
    if (tipo === 'pendientes') {
        const ticketsPendientes = document.querySelectorAll('.ticket-pendiente');
        const toggleBtn = document.getElementById('togglePendientes');
        const toggleText = document.getElementById('textTogglePendientes');
        const isExpanded = toggleBtn.classList.contains('expanded');
        
        if (isExpanded) {
            // Ocultar tickets extras (mostrar solo 4)
            ticketsPendientes.forEach((ticket, index) => {
                if (index >= 4) {
                    ticket.style.display = 'none';
                }
            });
            toggleBtn.classList.remove('expanded');
            toggleBtn.innerHTML = '<i class="fas fa-expand me-1"></i>';
            toggleText.textContent = `Ver todos (${ticketsPendientes.length})`;
            toggleBtn.className = 'btn btn-outline-warning btn-sm';
        } else {
            // Mostrar todos los tickets
            ticketsPendientes.forEach(ticket => {
                ticket.style.display = 'block';
            });
            toggleBtn.classList.add('expanded');
            toggleBtn.innerHTML = '<i class="fas fa-compress me-1"></i>';
            toggleText.textContent = 'Ver menos';
            toggleBtn.className = 'btn btn-warning btn-sm';
        }
    } else if (tipo === 'resueltos') {
        const ticketsResueltos = document.querySelectorAll('.ticket-resuelto');
        const ticketsDetalles = document.querySelectorAll('.ticket-resuelto-detail');
        const toggleBtn = document.getElementById('toggleResueltos');
        const toggleText = document.getElementById('textToggleResueltos');
        const isExpanded = toggleBtn.classList.contains('expanded');
        
        if (isExpanded) {
            // Ocultar tickets extras (mostrar solo 4)
            ticketsResueltos.forEach((ticket, index) => {
                if (index >= 4) {
                    ticket.style.display = 'none';
                }
            });
            ticketsDetalles.forEach((detalle, index) => {
                if (index >= 4) {
                    detalle.style.display = 'none';
                }
            });
            toggleBtn.classList.remove('expanded');
            toggleBtn.innerHTML = '<i class="fas fa-expand me-1"></i>';
            toggleText.textContent = `Ver todos (${ticketsResueltos.length})`;
            toggleBtn.className = 'btn btn-outline-success btn-sm';
        } else {
            // Mostrar todos los tickets
            ticketsResueltos.forEach(ticket => {
                ticket.style.display = 'table-row';
            });
            ticketsDetalles.forEach(detalle => {
                detalle.style.display = 'table-row';
            });
            toggleBtn.classList.add('expanded');
            toggleBtn.innerHTML = '<i class="fas fa-compress me-1"></i>';
            toggleText.textContent = 'Ver menos';
            toggleBtn.className = 'btn btn-success btn-sm';
        }
    }
}
