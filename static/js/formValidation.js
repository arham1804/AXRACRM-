// Form validation helper functions

document.addEventListener('DOMContentLoaded', function() {
    // Add custom form validation for any forms on the page
    setupFormValidation();
    
    // Setup multi-select enhancements
    setupMultiSelectFields();
    
    // Initialize date/time pickers
    setupDateTimePickers();
});

// Setup form validation
function setupFormValidation() {
    // Get all forms with the class needs-validation
    const forms = document.querySelectorAll('.needs-validation');
    
    // Loop over forms and prevent submission if invalid
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
}

// Setup multi-select fields
function setupMultiSelectFields() {
    // Add helper text for multiple select fields
    const multiSelects = document.querySelectorAll('select[multiple]');
    
    Array.from(multiSelects).forEach(select => {
        // Add helper text after the select
        const helpText = document.createElement('small');
        helpText.className = 'form-text text-muted mt-1';
        helpText.textContent = 'Hold Ctrl (Cmd on Mac) to select multiple options';
        
        select.parentNode.insertBefore(helpText, select.nextSibling);
    });
}

// Setup datetime pickers
function setupDateTimePickers() {
    // Add min attribute to datetime-local inputs to prevent scheduling in the past
    const dateTimeInputs = document.querySelectorAll('input[type="datetime-local"]');
    
    if (dateTimeInputs.length) {
        // Get current date and time in the format YYYY-MM-DDThh:mm
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        const hours = String(now.getHours()).padStart(2, '0');
        const minutes = String(now.getMinutes()).padStart(2, '0');
        
        const currentDateTime = `${year}-${month}-${day}T${hours}:${minutes}`;
        
        Array.from(dateTimeInputs).forEach(input => {
            input.setAttribute('min', currentDateTime);
        });
    }
}

// Validate phone number format
function validatePhoneNumber(phoneNumber) {
    // Allow +91 prefix and 10 digits
    const phoneRegex = /^(\+91)?[0-9]{10}$/;
    return phoneRegex.test(phoneNumber.replace(/\s/g, ''));
}

// Format currency input
function formatCurrency(input) {
    // Remove non-numeric characters
    let value = input.value.replace(/[^0-9.]/g, '');
    
    // Ensure only one decimal point
    const parts = value.split('.');
    if (parts.length > 2) {
        value = parts[0] + '.' + parts.slice(1).join('');
    }
    
    // Format with thousand separators
    const numParts = value.split('.');
    numParts[0] = numParts[0].replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    
    // Update input value
    input.value = '₹ ' + numParts.join('.');
}

// Custom validation for area input
function validatePreferredAreas(textArea) {
    const areas = textArea.value.split('\n').filter(area => area.trim() !== '');
    const minAreas = 5;
    
    if (areas.length < minAreas) {
        textArea.setCustomValidity(`Please enter at least ${minAreas} preferred areas (one per line)`);
    } else {
        textArea.setCustomValidity('');
    }
}

// Dynamically generate ID preview
function updateIdPreview(input, previewElement, prefix) {
    const name = input.value.trim();
    if (name) {
        // Generate a sample ID based on name and random characters
        const namePart = name.split(' ')[0].substring(0, 3).toUpperCase();
        const randomPart = Math.random().toString(36).substring(2, 6).toUpperCase();
        
        document.getElementById(previewElement).textContent = `${prefix}${namePart}${randomPart}`;
        document.getElementById(previewElement).parentElement.classList.remove('d-none');
    } else {
        document.getElementById(previewElement).parentElement.classList.add('d-none');
    }
}
