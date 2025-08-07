/**
 * Sistema de Pagos ChibchaWeb - JavaScript Unificado
 * Manejo de selecciones, validaciones y UX del sistema de pagos
 */

class PaymentSystem {
    constructor() {
        this.selectedAddress = null;
        this.selectedCard = null;
        this.init();
    }

    init() {
        // Inicializar después de que el DOM esté listo
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this.setup());
        } else {
            this.setup();
        }
    }

    setup() {
        this.setupAddressSelection();
        this.setupCardSelection();
        this.setupFormValidation();
        this.setupAutoSelection();
        this.setupAnimations();
        this.checkFormCompletion();
    }

    /**
     * Configurar selección de direcciones
     */
    setupAddressSelection() {
        const addressCards = document.querySelectorAll('.direccion-card, .payment-item-card[data-direccion-id]');
        
        addressCards.forEach(card => {
            card.addEventListener('click', (e) => {
                e.preventDefault();
                this.selectAddress(card);
            });

            // Mejorar accesibilidad
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.selectAddress(card);
                }
            });

            // Hacer focusable para accesibilidad
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');
            card.setAttribute('aria-label', 'Seleccionar dirección');
        });
    }

    /**
     * Configurar selección de tarjetas
     */
    setupCardSelection() {
        const cardCards = document.querySelectorAll('.tarjeta-card, .payment-item-card[data-tarjeta-id]');
        
        cardCards.forEach(card => {
            card.addEventListener('click', (e) => {
                e.preventDefault();
                this.selectCard(card);
            });

            // Mejorar accesibilidad
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    this.selectCard(card);
                }
            });

            // Hacer focusable para accesibilidad
            card.setAttribute('tabindex', '0');
            card.setAttribute('role', 'button');
            card.setAttribute('aria-label', 'Seleccionar tarjeta');
        });
    }

    /**
     * Seleccionar dirección
     */
    selectAddress(card) {
        // Remover selecciones previas
        document.querySelectorAll('.direccion-card, .payment-item-card[data-direccion-id]')
            .forEach(c => {
                c.classList.remove('selected');
                c.setAttribute('aria-selected', 'false');
            });
        
        // Seleccionar nueva dirección
        card.classList.add('selected');
        card.setAttribute('aria-selected', 'true');
        
        const radio = card.querySelector('input[type="radio"]');
        if (radio) {
            radio.checked = true;
            this.selectedAddress = radio.value;
        }
        
        this.addSelectionEffect(card);
        this.checkFormCompletion();
    }

    /**
     * Seleccionar tarjeta
     */
    selectCard(card) {
        // Remover selecciones previas
        document.querySelectorAll('.tarjeta-card, .payment-item-card[data-tarjeta-id]')
            .forEach(c => {
                c.classList.remove('selected');
                c.setAttribute('aria-selected', 'false');
            });
        
        // Seleccionar nueva tarjeta
        card.classList.add('selected');
        card.setAttribute('aria-selected', 'true');
        
        const radio = card.querySelector('input[type="radio"]');
        if (radio) {
            radio.checked = true;
            this.selectedCard = radio.value;
        }
        
        this.addSelectionEffect(card);
        this.checkFormCompletion();
    }

    /**
     * Agregar efecto visual de selección
     */
    addSelectionEffect(card) {
        // Solo agregar una clase CSS para efectos visuales sin alterar tamaño
        card.classList.add('payment-card-selected-effect');
        
        // Remover el efecto después de la animación
        setTimeout(() => {
            card.classList.remove('payment-card-selected-effect');
        }, 300);
    }

    /**
     * Verificar si el formulario está completo
     */
    checkFormCompletion() {
        const addressSelected = document.querySelector('input[name="direccion_id"]:checked');
        const cardSelected = document.querySelector('input[name="tarjeta_id"]:checked');
        const continueBtn = document.querySelector('button[value="continuar"], .payment-btn-primary[value="continuar"]');
        
        if (continueBtn) {
            const isComplete = addressSelected && cardSelected;
            continueBtn.disabled = !isComplete;
            continueBtn.classList.toggle('payment-loading', !isComplete);
            
            // Actualizar texto del botón
            if (isComplete) {
                continueBtn.innerHTML = '<i class="fas fa-arrow-right me-2"></i>Continuar al Resumen';
                continueBtn.setAttribute('aria-label', 'Continuar al resumen de pago');
            } else {
                continueBtn.innerHTML = '<i class="fas fa-exclamation-triangle me-2"></i>Selecciona Dirección y Tarjeta';
                continueBtn.setAttribute('aria-label', 'Debes seleccionar una dirección y una tarjeta');
            }
        }

        // Actualizar indicador de progreso
        this.updateProgressIndicator(addressSelected, cardSelected);
    }

    /**
     * Actualizar indicador de progreso
     */
    updateProgressIndicator(addressSelected, cardSelected) {
        const currentStep = document.querySelector('.payment-step.active, .step.active');
        if (currentStep && (addressSelected && cardSelected)) {
            // Agregar animación de progreso
            currentStep.style.animation = 'completedPulse 0.6s ease-out';
            setTimeout(() => {
                if (currentStep.style) {
                    currentStep.style.animation = '';
                }
            }, 600);
        }
    }

    /**
     * Auto-seleccionar si solo hay una opción
     */
    setupAutoSelection() {
        const addresses = document.querySelectorAll('.direccion-card, .payment-item-card[data-direccion-id]');
        const cards = document.querySelectorAll('.tarjeta-card, .payment-item-card[data-tarjeta-id]');
        
        // Auto-seleccionar dirección si solo hay una
        if (addresses.length === 1) {
            setTimeout(() => {
                this.selectAddress(addresses[0]);
                this.showInfoMessage('Dirección seleccionada automáticamente');
            }, 500);
        }
        
        // Auto-seleccionar tarjeta si solo hay una
        if (cards.length === 1) {
            setTimeout(() => {
                this.selectCard(cards[0]);
                this.showInfoMessage('Tarjeta seleccionada automáticamente');
            }, 700);
        }
    }

    /**
     * Configurar validación del formulario
     */
    setupFormValidation() {
        const form = document.querySelector('form');
        if (!form) return;

        form.addEventListener('submit', (e) => {
            const action = e.submitter?.value;
            
            if (action === 'continuar') {
                const addressSelected = document.querySelector('input[name="direccion_id"]:checked');
                const cardSelected = document.querySelector('input[name="tarjeta_id"]:checked');
                
                if (!addressSelected || !cardSelected) {
                    e.preventDefault();
                    this.showErrorMessage('Por favor selecciona una dirección y una tarjeta antes de continuar.');
                    this.highlightMissingSelections(addressSelected, cardSelected);
                    return false;
                }
                
                // Mostrar loading state
                this.showLoadingState(e.submitter);
            }
        });
    }

    /**
     * Resaltar selecciones faltantes
     */
    highlightMissingSelections(addressSelected, cardSelected) {
        if (!addressSelected) {
            const addressSection = document.querySelector('.direccion-card, .payment-item-card[data-direccion-id]')?.closest('.selection-section, .payment-section');
            if (addressSection) {
                addressSection.style.animation = 'shake 0.5s ease-in-out';
                setTimeout(() => {
                    if (addressSection.style) {
                        addressSection.style.animation = '';
                    }
                }, 500);
            }
        }
        
        if (!cardSelected) {
            const cardSection = document.querySelector('.tarjeta-card, .payment-item-card[data-tarjeta-id]')?.closest('.selection-section, .payment-section');
            if (cardSection) {
                cardSection.style.animation = 'shake 0.5s ease-in-out';
                setTimeout(() => {
                    if (cardSection.style) {
                        cardSection.style.animation = '';
                    }
                }, 500);
            }
        }
    }

    /**
     * Mostrar estado de carga
     */
    showLoadingState(button) {
        if (button) {
            button.classList.add('payment-loading');
            button.disabled = true;
            button.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Procesando...';
        }
    }

    /**
     * Configurar animaciones mejoradas
     */
    setupAnimations() {
        // Observador para animaciones de entrada
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }
            });
        }, { threshold: 0.1 });

        // Observar elementos para animaciones
        document.querySelectorAll('.payment-item-card, .payment-container, .payment-section').forEach(el => {
            el.style.opacity = '0';
            el.style.transform = 'translateY(30px)';
            el.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            observer.observe(el);
        });
    }

    /**
     * Mostrar mensajes de estado
     */
    showSuccessMessage(message) {
        this.showMessage(message, 'success');
    }

    showErrorMessage(message) {
        this.showMessage(message, 'error');
    }

    showInfoMessage(message) {
        this.showMessage(message, 'info');
    }

    showMessage(message, type = 'info') {
        // Crear o actualizar mensaje
        let messageEl = document.querySelector('.payment-message');
        if (!messageEl) {
            messageEl = document.createElement('div');
            messageEl.className = 'payment-message';
            messageEl.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                padding: 1rem 1.5rem;
                border-radius: 8px;
                color: white;
                font-weight: 600;
                z-index: 9999;
                transform: translateX(100%);
                transition: transform 0.3s ease;
                max-width: 300px;
                box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            `;
            document.body.appendChild(messageEl);
        }

        // Establecer color según tipo
        const colors = {
            success: '#28a745',
            error: '#dc3545',
            info: '#17a2b8',
            warning: '#ffc107'
        };

        messageEl.style.background = colors[type] || colors.info;
        messageEl.textContent = message;
        
        // Mostrar mensaje
        setTimeout(() => {
            messageEl.style.transform = 'translateX(0)';
        }, 100);

        // Ocultar después de 3 segundos
        setTimeout(() => {
            messageEl.style.transform = 'translateX(100%)';
            setTimeout(() => {
                if (messageEl.parentNode) {
                    messageEl.parentNode.removeChild(messageEl);
                }
            }, 300);
        }, 3000);
    }
}

// Agregar estilos CSS para animaciones
const style = document.createElement('style');
style.textContent = `
    .payment-card-selected-effect {
        background-color: rgba(234, 178, 27, 0.08) !important;
        box-shadow: 0 0 0 2px rgba(234, 178, 27, 0.3) !important;
        transition: background-color 0.3s ease, box-shadow 0.3s ease !important;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
`;
document.head.appendChild(style);

// Inicializar el sistema de pagos
const paymentSystem = new PaymentSystem();
