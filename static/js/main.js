document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle
    const sidebarCollapse = document.getElementById('sidebarCollapse');
    const sidebar = document.getElementById('sidebar');
    const content = document.getElementById('content');
    
    if (sidebarCollapse) {
        sidebarCollapse.addEventListener('click', function() {
            sidebar.classList.toggle('active');
            content.classList.toggle('active');
        });
    }
    
    // Dropdown toggle
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function(e) {
            e.preventDefault();
            
            const expanded = this.getAttribute('aria-expanded') === 'true' || false;
            this.setAttribute('aria-expanded', !expanded);
            
            const submenu = this.nextElementSibling;
            if (submenu) {
                submenu.classList.toggle('show');
            }
        });
    });
    
    // Close dropdowns when clicking outside
    document.addEventListener('click', function(e) {
        if (!e.target.closest('.dropdown-toggle')) {
            const openDropdowns = document.querySelectorAll('.collapse.show');
            openDropdowns.forEach(dropdown => {
                dropdown.classList.remove('show');
                const toggle = dropdown.previousElementSibling;
                if (toggle && toggle.classList.contains('dropdown-toggle')) {
                    toggle.setAttribute('aria-expanded', 'false');
                }
            });
        }
    });
    
    // Testimonials slider auto-scroll
    const testimonialsSlider = document.querySelector('.testimonials-slider');
    
    if (testimonialsSlider) {
        let scrollAmount = 0;
        const slideWidth = 380; // Width of testimonial + gap
        const maxScroll = testimonialsSlider.scrollWidth - testimonialsSlider.clientWidth;
        
        function autoScroll() {
            scrollAmount += slideWidth;
            
            if (scrollAmount > maxScroll) {
                scrollAmount = 0;
            }
            
            testimonialsSlider.scrollTo({
                left: scrollAmount,
                behavior: 'smooth'
            });
        }
        
        // Auto scroll every 5 seconds
        setInterval(autoScroll, 5000);
    }
    
    // Form validation
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    isValid = false;
                    field.classList.add('error');
                } else {
                    field.classList.remove('error');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                alert('Please fill in all required fields.');
            }
        });
    });
    
    // Password confirmation validation
    const passwordForms = document.querySelectorAll('form:has(#password, #confirm_password)');
    
    passwordForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const password = form.querySelector('#password');
            const confirmPassword = form.querySelector('#confirm_password');
            
            if (password && confirmPassword) {
                if (password.value !== confirmPassword.value) {
                    e.preventDefault();
                    alert('Passwords do not match!');
                }
            }
        });
    });
    
    // Mobile menu toggle
    const mobileMenuToggle = document.querySelector('.navbar-toggler');
    const navbarCollapse = document.querySelector('.navbar-collapse');
    
    if (mobileMenuToggle && navbarCollapse) {
        mobileMenuToggle.addEventListener('click', function() {
            navbarCollapse.classList.toggle('show');
        });
    }
    
    // Smooth scroll for anchor links
    const anchorLinks = document.querySelectorAll('a[href^="#"]:not([href="#"])');
    
    anchorLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                targetElement.scrollIntoView({
                    behavior: 'smooth'
                });
            }
        });
    });
    
    // Initialize any date pickers
    const datePickers = document.querySelectorAll('input[type="date"]');
    
    datePickers.forEach(picker => {
        // Set min date to today
        const today = new Date();
        const yyyy = today.getFullYear();
        const mm = String(today.getMonth() + 1).padStart(2, '0');
        const dd = String(today.getDate()).padStart(2, '0');
        const formattedToday = `${yyyy}-${mm}-${dd}`;
        
        if (!picker.min) {
            picker.min = formattedToday;
        }
    });
    
    // Initialize modals
    const modalTriggers = document.querySelectorAll('[data-toggle="modal"]');
    const modals = document.querySelectorAll('.modal');
    const closeButtons = document.querySelectorAll('.close-modal');
    
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', function() {
            const targetModal = document.querySelector(this.dataset.target);
            
            if (targetModal) {
                targetModal.style.display = 'block';
            }
        });
    });
    
    closeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const modal = this.closest('.modal');
            
            if (modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    window.addEventListener('click', function(e) {
        modals.forEach(modal => {
            if (e.target === modal) {
                modal.style.display = 'none';
            }
        });
    });
    
    // Initialize tooltips
    const tooltips = document.querySelectorAll('[data-toggle="tooltip"]');
    
    tooltips.forEach(tooltip => {
        tooltip.addEventListener('mouseenter', function() {
            const title = this.getAttribute('title');
            
            if (title) {
                const tooltipElement = document.createElement('div');
                tooltipElement.className = 'tooltip';
                tooltipElement.textContent = title;
                
                document.body.appendChild(tooltipElement);
                
                const rect = this.getBoundingClientRect();
                const tooltipRect = tooltipElement.getBoundingClientRect();
                
                tooltipElement.style.top = `${rect.top - tooltipRect.height - 10}px`;
                tooltipElement.style.left = `${rect.left + (rect.width / 2) - (tooltipRect.width / 2)}px`;
                
                this.addEventListener('mouseleave', function() {
                    tooltipElement.remove();
                }, { once: true });
            }
        });
    });
    
    // Admin appointment status update
    const statusUpdateButtons = document.querySelectorAll('.btn-confirm, .btn-complete, .btn-cancel');
    
    statusUpdateButtons.forEach(button => {
        button.addEventListener('click', function() {
            if (this.disabled) return;
            
            const row = this.closest('tr');
            const appointmentId = row.dataset.appointmentId;
            let status;
            
            if (this.classList.contains('btn-confirm')) {
                status = 'confirmed';
            } else if (this.classList.contains('btn-complete')) {
                status = 'completed';
            } else if (this.classList.contains('btn-cancel')) {
                status = 'cancelled';
                
                if (!confirm('Are you sure you want to cancel this appointment?')) {
                    return;
                }
            }
            
            // Send AJAX request to update status
            fetch('/api/update-appointment-status', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    appointment_id: appointmentId,
                    status: status
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Update UI
                    const statusCell = row.querySelector('td:nth-child(5)');
                    statusCell.innerHTML = `<span class="status-badge status-${status}">${status.charAt(0).toUpperCase() + status.slice(1)}</span>`;
                    
                    // Update row data attribute
                    row.dataset.status = status;
                    
                    // Update button states
                    const confirmBtn = row.querySelector('.btn-confirm');
                    const completeBtn = row.querySelector('.btn-complete');
                    const cancelBtn = row.querySelector('.btn-cancel');
                    
                    if (confirmBtn) confirmBtn.disabled = status !== 'pending';
                    if (completeBtn) completeBtn.disabled = status !== 'confirmed';
                    if (cancelBtn) cancelBtn.disabled = ['completed', 'cancelled'].includes(status);
                    
                    // Show success message
                    alert(`Appointment status updated to ${status}.`);
                } else {
                    alert('Failed to update appointment status: ' + data.message);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('An error occurred while updating the appointment status.');
            });
        });
    });
    
    // Filter appointments
    const filterBtn = document.getElementById('filterBtn');
    const searchInput = document.getElementById('appointmentSearch');
    const statusFilter = document.getElementById('statusFilter');
    
    if (filterBtn && searchInput && statusFilter) {
        filterBtn.addEventListener('click', function() {
            const searchTerm = searchInput.value.toLowerCase();
            const statusValue = statusFilter.value;
            
            const rows = document.querySelectorAll('.appointments-table tbody tr');
            
            rows.forEach(row => {
                let showRow = true;
                
                // Filter by status
                if (statusValue !== 'all' && row.dataset.status !== statusValue) {
                    showRow = false;
                }
                
                // Filter by search term
                if (searchTerm) {
                    const rowText = row.textContent.toLowerCase();
                    if (!rowText.includes(searchTerm)) {
                        showRow = false;
                    }
                }
                
                row.style.display = showRow ? '' : 'none';
            });
        });
    }
    
    // FAQ accordion
    const faqItems = document.querySelectorAll('.faq-item');
    
    faqItems.forEach(item => {
        const question = item.querySelector('.faq-question');
        const answer = item.querySelector('.faq-answer');
        const toggle = item.querySelector('.faq-toggle');
        
        if (question && answer && toggle) {
            question.addEventListener('click', () => {
                answer.classList.toggle('active');
                toggle.innerHTML = answer.classList.contains('active') ? 
                    '<i class="fas fa-minus"></i>' : '<i class="fas fa-plus"></i>';
            });
        }
    });
});