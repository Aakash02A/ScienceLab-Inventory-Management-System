// Initialize tooltips, popovers, and UI enhancements
document.addEventListener('DOMContentLoaded', function() {
    // Enable Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Enable Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
    
    // Properly initialize all modals
    const modalElements = document.querySelectorAll('.modal');
    modalElements.forEach(modalElement => {
        const modal = new bootstrap.Modal(modalElement);
        
        // Add event listener to close the modal with escape key or clicking outside
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape' && modalElement.classList.contains('show')) {
                modal.hide();
            }
        });
        
        // Add a backup close button to each modal that might be stuck
        const modalBackdrop = document.querySelectorAll('.modal-backdrop');
        if (modalBackdrop.length > 0) {
            modalBackdrop.forEach(backdrop => {
                if (!backdrop.hasAttribute('data-emergency-button-added')) {
                    const emergencyCloseBtn = document.createElement('button');
                    emergencyCloseBtn.innerText = 'Emergency Close';
                    emergencyCloseBtn.className = 'emergency-close-button';
                    emergencyCloseBtn.style.position = 'fixed';
                    emergencyCloseBtn.style.top = '10px';
                    emergencyCloseBtn.style.right = '10px';
                    emergencyCloseBtn.style.zIndex = '2000';
                    emergencyCloseBtn.style.padding = '10px';
                    emergencyCloseBtn.style.backgroundColor = 'red';
                    emergencyCloseBtn.style.color = 'white';
                    emergencyCloseBtn.style.border = 'none';
                    emergencyCloseBtn.style.borderRadius = '5px';
                    
                    emergencyCloseBtn.addEventListener('click', function() {
                        // Force remove the modal and backdrop
                        const modals = document.querySelectorAll('.modal.show');
                        modals.forEach(m => {
                            m.classList.remove('show');
                            m.style.display = 'none';
                            m.setAttribute('aria-hidden', 'true');
                            m.removeAttribute('aria-modal');
                            m.removeAttribute('role');
                        });
                        
                        const backdrops = document.querySelectorAll('.modal-backdrop');
                        backdrops.forEach(b => b.remove());
                        
                        // Re-enable scrolling
                        document.body.classList.remove('modal-open');
                        document.body.style.overflow = '';
                        document.body.style.paddingRight = '';
                    });
                    
                    backdrop.appendChild(emergencyCloseBtn);
                    backdrop.setAttribute('data-emergency-button-added', 'true');
                }
            });
        }
    });
    
    // Auto-dismiss alerts after 5 seconds
    setTimeout(function() {
        const alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);
    
    // Add animation classes to elements when they become visible
    const animateOnScroll = function() {
        const elements = document.querySelectorAll('.animate-on-scroll:not(.animated)');
        
        elements.forEach(element => {
            const elementPosition = element.getBoundingClientRect().top;
            const windowHeight = window.innerHeight;
            
            if (elementPosition < windowHeight - 50) {
                const animation = element.dataset.animation || 'fadeIn';
                element.classList.add('animated', 'animate__animated', `animate__${animation}`);
            }
        });
    };
    
    // Run once on load and then on scroll
    animateOnScroll();
    window.addEventListener('scroll', animateOnScroll);
    
    // Add staggered animations to list items
    const staggeredLists = document.querySelectorAll('.staggered-list');
    staggeredLists.forEach(list => {
        const items = list.children;
        for (let i = 0; i < items.length; i++) {
            items[i].style.animationDelay = `${0.1 * (i + 1)}s`;
            items[i].classList.add('animate__animated', 'animate__fadeInUp');
        }
    });
    
    // Add hover effects to cards
    const cards = document.querySelectorAll('.card:not(.no-hover)');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.boxShadow = '0 12px 24px rgba(0, 0, 0, 0.12)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = '';
            this.style.boxShadow = '';
        });
    });
    
    // Add functionality to form with multiple item rows (for orders page)
    const addItemButton = document.getElementById('add-item-row');
    if (addItemButton) {
        let rowCounter = 0;
        
        addItemButton.addEventListener('click', function() {
            rowCounter++;
            const template = document.getElementById('item-row-template');
            const container = document.getElementById('order-items-container');
            
            if (template && container) {
                const clone = template.content.cloneNode(true);
                
                // Update the IDs to make them unique
                const inputs = clone.querySelectorAll('input, select');
                inputs.forEach(input => {
                    const originalId = input.id;
                    if (originalId) {
                        input.id = originalId + '-' + rowCounter;
                    }
                });
                
                // Add animation to the new row
                const newRow = clone.querySelector('.item-row');
                if (newRow) {
                    newRow.classList.add('animate__animated', 'animate__fadeInDown');
                }
                
                container.appendChild(clone);
                
                // Add event listener to remove button
                const removeButtons = container.querySelectorAll('.remove-item-row');
                removeButtons.forEach(button => {
                    button.addEventListener('click', function() {
                        const row = this.closest('.item-row');
                        row.classList.add('animate__animated', 'animate__fadeOutRight');
                        
                        // Wait for animation to complete before removing
                        setTimeout(() => {
                            row.remove();
                        }, 500);
                    });
                });
                
                // Add event listener to select existing item
                const itemSelectors = container.querySelectorAll('.item-selector');
                itemSelectors.forEach(selector => {
                    selector.addEventListener('change', function() {
                        const row = this.closest('.item-row');
                        const itemId = this.value;
                        
                        if (itemId) {
                            // Show loading indicator
                            const loadingIndicator = document.createElement('div');
                            loadingIndicator.className = 'loading-spinner';
                            loadingIndicator.innerHTML = '<i class="bi bi-arrow-repeat spinning"></i> Loading...';
                            row.appendChild(loadingIndicator);
                            
                            fetch('/api/item/' + itemId)
                                .then(response => response.json())
                                .then(data => {
                                    row.querySelector('[name="item_name[]"]').value = data.name;
                                    row.querySelector('[name="unit[]"]').value = data.unit || '';
                                    row.querySelector('[name="price[]"]').value = data.price || '';
                                    
                                    // Add a highlight effect to the updated fields
                                    const fieldsToHighlight = row.querySelectorAll('input, select');
                                    fieldsToHighlight.forEach(field => {
                                        field.classList.add('highlight-update');
                                        setTimeout(() => {
                                            field.classList.remove('highlight-update');
                                        }, 1000);
                                    });
                                    
                                    // Remove loading indicator
                                    row.removeChild(loadingIndicator);
                                })
                                .catch(error => {
                                    console.error('Error fetching item data:', error);
                                    // Remove loading indicator
                                    row.removeChild(loadingIndicator);
                                    
                                    // Show error message
                                    const errorMsg = document.createElement('div');
                                    errorMsg.className = 'alert alert-danger';
                                    errorMsg.textContent = 'Failed to load item data';
                                    row.appendChild(errorMsg);
                                    
                                    setTimeout(() => {
                                        row.removeChild(errorMsg);
                                    }, 3000);
                                });
                        }
                    });
                });
            }
        });
        
        // Initialize existing remove buttons
        const removeButtons = document.querySelectorAll('.remove-item-row');
        removeButtons.forEach(button => {
            button.addEventListener('click', function() {
                const row = this.closest('.item-row');
                row.classList.add('animate__animated', 'animate__fadeOutRight');
                
                setTimeout(() => {
                    row.remove();
                }, 500);
            });
        });
        
        // Initialize existing item selectors
        const itemSelectors = document.querySelectorAll('.item-selector');
        itemSelectors.forEach(selector => {
            selector.addEventListener('change', function() {
                const row = this.closest('.item-row');
                const itemId = this.value;
                
                if (itemId) {
                    fetch('/api/item/' + itemId)
                        .then(response => response.json())
                        .then(data => {
                            row.querySelector('[name="item_name[]"]').value = data.name;
                            row.querySelector('[name="unit[]"]').value = data.unit || '';
                            row.querySelector('[name="price[]"]').value = data.price || '';
                        })
                        .catch(error => console.error('Error fetching item data:', error));
                }
            });
        });
    }
    
    // Add search functionality enhancement
    const searchInputs = document.querySelectorAll('input[type="search"], input[id*="search"]');
    searchInputs.forEach(input => {
        // Add clear button
        const clearButton = document.createElement('button');
        clearButton.type = 'button';
        clearButton.className = 'search-clear';
        clearButton.innerHTML = '&times;';
        clearButton.style.display = 'none';
        
        // Position the clear button
        input.parentNode.style.position = 'relative';
        input.parentNode.appendChild(clearButton);
        
        // Style the clear button
        clearButton.style.position = 'absolute';
        clearButton.style.right = '10px';
        clearButton.style.top = '50%';
        clearButton.style.transform = 'translateY(-50%)';
        clearButton.style.border = 'none';
        clearButton.style.background = 'none';
        clearButton.style.color = '#999';
        clearButton.style.fontSize = '1.2em';
        clearButton.style.cursor = 'pointer';
        
        // Show/hide clear button
        input.addEventListener('input', function() {
            clearButton.style.display = this.value.length ? 'block' : 'none';
        });
        
        // Clear input when clicked
        clearButton.addEventListener('click', function() {
            input.value = '';
            this.style.display = 'none';
            input.focus();
            
            // Trigger input event to update search results
            const event = new Event('input', { bubbles: true });
            input.dispatchEvent(event);
        });
        
        // Add animation to the search input
        input.addEventListener('focus', function() {
            this.classList.add('search-focused');
        });
        
        input.addEventListener('blur', function() {
            this.classList.remove('search-focused');
        });
    });
    
    // Initialize any charts if present
    initializeCharts();
    
    // Handle any modals that might be stuck
    handleStuckModals();
    
    // Fix action buttons in all tables (the ones that cause shading and blinking)
    fixActionButtons();
});

// Function to initialize charts with animations
function initializeCharts() {
    // Set default Chart.js animation options
    Chart.defaults.animation = {
        duration: 2000,
        easing: 'easeOutQuart'
    };
    
    // Inventory Status by Category chart
    const categoryChartElement = document.getElementById('category-chart');
    if (categoryChartElement) {
        const ctx = categoryChartElement.getContext('2d');
        const labels = JSON.parse(categoryChartElement.getAttribute('data-labels') || '[]');
        const data = JSON.parse(categoryChartElement.getAttribute('data-values') || '[]');
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        '#4A6FFF', // Primary
                        '#F44336', // Danger
                        '#4CAF50', // Success
                        '#FF9800', // Warning
                        '#9C27B0', // Purple
                        '#03A9F4', // Info
                        '#795548'  // Brown
                    ],
                    borderWidth: 1,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'right',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'circle'
                        }
                    },
                    tooltip: {
                        backgroundColor: 'rgba(0,0,0,0.8)',
                        padding: 12,
                        titleFont: {
                            size: 14
                        },
                        bodyFont: {
                            size: 13
                        },
                        displayColors: true
                    }
                },
                cutout: '65%',
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });
    }
    
    // Inventory Status by Status chart
    const statusChartElement = document.getElementById('status-chart');
    if (statusChartElement) {
        const ctx = statusChartElement.getContext('2d');
        const labels = JSON.parse(statusChartElement.getAttribute('data-labels') || '[]');
        const data = JSON.parse(statusChartElement.getAttribute('data-values') || '[]');
        
        new Chart(ctx, {
            type: 'pie',
            data: {
                labels: labels,
                datasets: [{
                    data: data,
                    backgroundColor: [
                        'rgba(76, 175, 80, 0.8)',  // Success (in_stock)
                        'rgba(255, 152, 0, 0.8)',  // Warning (low_stock)
                        'rgba(244, 67, 54, 0.8)',  // Danger (out_of_stock)
                        'rgba(3, 169, 244, 0.8)'   // Info (expiring_soon)
                    ],
                    hoverBackgroundColor: [
                        'rgba(76, 175, 80, 1)',
                        'rgba(255, 152, 0, 1)',
                        'rgba(244, 67, 54, 1)',
                        'rgba(3, 169, 244, 1)'
                    ],
                    borderWidth: 1,
                    borderColor: '#ffffff'
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true,
                            pointStyle: 'rectRounded'
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(context) {
                                const label = context.label || '';
                                const value = context.parsed || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = Math.round((value / total) * 100);
                                return `${label}: ${value} (${percentage}%)`;
                            }
                        }
                    }
                },
                animation: {
                    animateScale: true,
                    animateRotate: true
                }
            }
        });
    }
    
    // Transaction History chart
    const transactionChartElement = document.getElementById('transaction-chart');
    if (transactionChartElement) {
        const ctx = transactionChartElement.getContext('2d');
        const labels = JSON.parse(transactionChartElement.getAttribute('data-labels') || '[]');
        const checkIn = JSON.parse(transactionChartElement.getAttribute('data-check-in') || '[]');
        const checkOut = JSON.parse(transactionChartElement.getAttribute('data-check-out') || '[]');
        const restock = JSON.parse(transactionChartElement.getAttribute('data-restock') || '[]');
        const dispose = JSON.parse(transactionChartElement.getAttribute('data-dispose') || '[]');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Check In',
                        data: checkIn,
                        backgroundColor: 'rgba(76, 175, 80, 0.7)',
                        borderColor: 'rgba(76, 175, 80, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Check Out',
                        data: checkOut,
                        backgroundColor: 'rgba(244, 67, 54, 0.7)',
                        borderColor: 'rgba(244, 67, 54, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Restock',
                        data: restock,
                        backgroundColor: 'rgba(74, 111, 255, 0.7)',
                        borderColor: 'rgba(74, 111, 255, 1)',
                        borderWidth: 1
                    },
                    {
                        label: 'Dispose',
                        data: dispose,
                        backgroundColor: 'rgba(255, 152, 0, 0.7)',
                        borderColor: 'rgba(255, 152, 0, 1)',
                        borderWidth: 1
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        },
                        grid: {
                            display: true,
                            color: 'rgba(0, 0, 0, 0.05)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                },
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            boxWidth: 15,
                            padding: 15
                        }
                    },
                    tooltip: {
                        mode: 'index',
                        intersect: false
                    }
                },
                animation: {
                    delay: function(context) {
                        return context.dataIndex * 100;
                    }
                }
            }
        });
    }
}

// Function to update item status based on quantity and min_quantity with animation
function updateItemStatus() {
    const quantityInput = document.getElementById('quantity');
    const minQuantityInput = document.getElementById('min_quantity');
    const statusDisplay = document.getElementById('status-display');
    
    if (quantityInput && minQuantityInput && statusDisplay) {
        const quantity = parseFloat(quantityInput.value) || 0;
        const minQuantity = parseFloat(minQuantityInput.value) || 0;
        
        let status = 'in_stock';
        let statusText = 'In Stock';
        let statusClass = 'bg-success';
        
        if (quantity <= 0) {
            status = 'out_of_stock';
            statusText = 'Out of Stock';
            statusClass = 'bg-danger';
        } else if (minQuantity > 0 && quantity <= minQuantity) {
            status = 'low_stock';
            statusText = 'Low Stock';
            statusClass = 'bg-warning';
        }
        
        // Update hidden status input if it exists
        const statusInput = document.getElementById('status');
        if (statusInput) {
            statusInput.value = status;
        }
        
        // Animate status change
        statusDisplay.classList.add('animate__animated', 'animate__fadeOut');
        
        // After the fadeOut completes, update the status and fade back in
        setTimeout(() => {
            statusDisplay.className = 'badge ' + statusClass + ' animate__animated animate__fadeIn';
            statusDisplay.textContent = statusText;
        }, 300);
    }
}

// Function to format currency with animation
function formatCurrency(input) {
    if (!input) return '';
    
    const value = parseFloat(input.value);
    if (!isNaN(value)) {
        // Add formatting animation
        input.classList.add('highlight-update');
        input.value = value.toFixed(2);
        
        // Remove highlight after animation completes
        setTimeout(() => {
            input.classList.remove('highlight-update');
        }, 1000);
    }
}

// Barcode scanner simulation with visual effect
function simulateBarcodeScanning() {
    const barcodeInput = document.getElementById('barcode-input');
    const scanButton = document.getElementById('scan-button');
    
    if (barcodeInput && scanButton) {
        // Disable the scan button
        scanButton.disabled = true;
        scanButton.innerHTML = '<i class="bi bi-upc-scan animate__animated animate__pulse animate__infinite"></i> Scanning...';
        
        // Show scanning animation
        const scannerOverlay = document.createElement('div');
        scannerOverlay.className = 'scanner-overlay';
        scannerOverlay.innerHTML = '<div class="scanner-line"></div>';
        document.body.appendChild(scannerOverlay);
        
        const demoBarcode = '1234567890123'; // Example barcode
        
        // Clear the input first
        barcodeInput.value = '';
        
        // Simulate typing the barcode
        let index = 0;
        const interval = setInterval(() => {
            if (index < demoBarcode.length) {
                barcodeInput.value += demoBarcode.charAt(index);
                index++;
            } else {
                clearInterval(interval);
                
                // Remove scanner overlay
                document.body.removeChild(scannerOverlay);
                
                // Reset the scan button
                scanButton.disabled = false;
                scanButton.innerHTML = '<i class="bi bi-upc-scan"></i> Scan';
                
                // Add success animation to the input
                barcodeInput.classList.add('animate__animated', 'animate__pulse');
                
                // Submit the form after a short delay
                setTimeout(() => {
                    barcodeInput.form.submit();
                }, 500);
            }
        }, 100);
    }
}

// Add CSS for new animations
document.addEventListener('DOMContentLoaded', function() {
    // Add CSS for spinning icon
    const style = document.createElement('style');
    style.textContent = `
        .spinning {
            animation: spin 1s linear infinite;
        }
        
        @keyframes spin {
            from { transform: rotate(0deg); }
            to { transform: rotate(360deg); }
        }
        
        .loading-spinner {
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 0.5rem;
            color: var(--primary-color);
        }
        
        .loading-spinner i {
            margin-right: 0.5rem;
        }
        
        .highlight-update {
            animation: highlight 1s ease;
        }
        
        @keyframes highlight {
            0%, 100% { background-color: transparent; }
            50% { background-color: rgba(74, 111, 255, 0.2); }
        }
        
        .search-focused {
            transition: all 0.3s;
            box-shadow: 0 0 0 0.25rem rgba(74, 111, 255, 0.25);
            transform: translateY(-2px);
        }
        
        .scanner-overlay {
            position: fixed;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background-color: rgba(0, 0, 0, 0.5);
            z-index: 9999;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        
        .scanner-line {
            width: 300px;
            height: 2px;
            background-color: red;
            animation: scan 1.5s linear infinite;
        }
        
        @keyframes scan {
            0% { transform: translateY(-100px); }
            50% { transform: translateY(100px); }
            100% { transform: translateY(-100px); }
        }
    `;
    document.head.appendChild(style);
});

// Function to ensure all modal action buttons work correctly
function fixActionButtons() {
    // Find all action buttons that open modals
    const actionButtons = document.querySelectorAll('button[data-bs-toggle="modal"]');
    
    actionButtons.forEach(button => {
        // Remove any existing click listeners
        const newButton = button.cloneNode(true);
        button.parentNode.replaceChild(newButton, button);
        
        // Get the target modal ID
        const modalId = newButton.getAttribute('data-bs-target');
        if (!modalId) return;
        
        // Find the corresponding modal element
        const modalElement = document.querySelector(modalId);
        if (!modalElement) return;
        
        // Create a proper Bootstrap Modal instance
        const modal = new bootstrap.Modal(modalElement);
        
        // Add a proper click handler
        newButton.addEventListener('click', function(e) {
            e.preventDefault();
            e.stopPropagation();
            
            // Show the modal properly
            modal.show();
            
            // Add safety measure - create close button if not present
            const modalHeader = modalElement.querySelector('.modal-header');
            if (modalHeader && !modalHeader.querySelector('.emergency-close')) {
                const closeBtn = document.createElement('button');
                closeBtn.className = 'btn btn-sm btn-danger emergency-close ms-2';
                closeBtn.innerHTML = 'Stuck? Close';
                closeBtn.style.display = 'none';
                
                // Show after a delay if the modal is still open
                setTimeout(() => {
                    if (modalElement.classList.contains('show')) {
                        closeBtn.style.display = 'inline-block';
                    }
                }, 3000);
                
                closeBtn.addEventListener('click', function() {
                    modal.hide();
                    
                    // Force cleanup if the modal hide doesn't work
                    setTimeout(() => {
                        if (modalElement.classList.contains('show')) {
                            modalElement.classList.remove('show');
                            modalElement.style.display = 'none';
                            document.body.classList.remove('modal-open');
                            const backdrop = document.querySelector('.modal-backdrop');
                            if (backdrop) backdrop.remove();
                        }
                    }, 300);
                });
                
                modalHeader.appendChild(closeBtn);
            }
        });
        
        // Ensure close buttons work properly
        const closeButtons = modalElement.querySelectorAll('[data-bs-dismiss="modal"]');
        closeButtons.forEach(closeBtn => {
            // Remove existing listeners
            const newCloseBtn = closeBtn.cloneNode(true);
            closeBtn.parentNode.replaceChild(newCloseBtn, closeBtn);
            
            // Add proper close handler
            newCloseBtn.addEventListener('click', function(e) {
                e.preventDefault();
                modal.hide();
                
                // Double-check the modal is actually hidden
                setTimeout(() => {
                    if (modalElement.classList.contains('show')) {
                        modalElement.classList.remove('show');
                        modalElement.style.display = 'none';
                        document.body.classList.remove('modal-open');
                        const backdrop = document.querySelector('.modal-backdrop');
                        if (backdrop) backdrop.remove();
                    }
                }, 300);
            });
        });
    });
}

// Helper function to handle any stuck modals
function handleStuckModals() {
    // Create an emergency close button on the document body
    const existingButton = document.querySelector('#emergency-modal-close');
    if (!existingButton) {
        const emergencyButton = document.createElement('button');
        emergencyButton.id = 'emergency-modal-close';
        emergencyButton.innerText = 'Close Stuck Modals';
        emergencyButton.style.position = 'fixed';
        emergencyButton.style.bottom = '10px';
        emergencyButton.style.right = '10px';
        emergencyButton.style.zIndex = '9999';
        emergencyButton.style.padding = '10px';
        emergencyButton.style.backgroundColor = 'rgba(220, 53, 69, 0.8)';
        emergencyButton.style.color = 'white';
        emergencyButton.style.border = 'none';
        emergencyButton.style.borderRadius = '5px';
        emergencyButton.style.cursor = 'pointer';
        emergencyButton.style.display = 'none';
        
        emergencyButton.addEventListener('click', function() {
            // Force remove all modals and backdrops
            const modals = document.querySelectorAll('.modal');
            modals.forEach(modal => {
                modal.classList.remove('show');
                modal.style.display = 'none';
                modal.setAttribute('aria-hidden', 'true');
                modal.removeAttribute('aria-modal');
                modal.removeAttribute('role');
            });
            
            const backdrops = document.querySelectorAll('.modal-backdrop');
            backdrops.forEach(backdrop => {
                backdrop.remove();
            });
            
            // Re-enable scrolling
            document.body.classList.remove('modal-open');
            document.body.style.overflow = '';
            document.body.style.paddingRight = '';
            
            // Hide the emergency button
            emergencyButton.style.display = 'none';
        });
        
        document.body.appendChild(emergencyButton);
        
        // Listen for the Escape key to show the emergency button
        document.addEventListener('keydown', function(event) {
            if (event.key === 'Escape') {
                const backdrop = document.querySelector('.modal-backdrop');
                if (backdrop) {
                    emergencyButton.style.display = 'block';
                    setTimeout(() => {
                        emergencyButton.style.display = 'none';
                    }, 5000); // Hide after 5 seconds
                }
            }
        });
        
        // Also check periodically for stuck modals
        setInterval(() => {
            const backdrop = document.querySelector('.modal-backdrop');
            const openModal = document.querySelector('.modal.show');
            if (backdrop && !openModal) {
                emergencyButton.style.display = 'block';
                setTimeout(() => {
                    emergencyButton.style.display = 'none';
                }, 5000);
            }
        }, 2000);
    }
}