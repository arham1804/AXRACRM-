/**
 * Lead Progress Animation and Management
 * This script handles the animated lead status progress indicator
 */

document.addEventListener('DOMContentLoaded', function() {
    // Initialize all lead progress indicators on page
    initLeadProgressIndicators();
});

/**
 * Initialize all lead progress indicators on the page
 */
function initLeadProgressIndicators() {
    const progressContainers = document.querySelectorAll('.lead-progress-container');
    
    progressContainers.forEach(container => {
        const currentStatus = container.dataset.status;
        const progressLine = container.querySelector('.progress-line');
        const steps = container.querySelectorAll('.lead-progress-step');
        
        updateProgressIndicator(steps, progressLine, currentStatus);
        
        // Add animation class after a short delay for animation effect
        setTimeout(() => {
            container.classList.add('animate');
        }, 200);
    });
}

/**
 * Update a progress indicator based on the current status
 * @param {NodeList} steps - The step elements
 * @param {Element} progressLine - The progress line element
 * @param {String} currentStatus - The current status
 */
function updateProgressIndicator(steps, progressLine, currentStatus) {
    // Define the order of statuses in the flow
    const statusOrder = ['New', 'Assigned', 'Demo Scheduled', 'Converted'];
    
    // Find index of current status
    const currentIndex = statusOrder.indexOf(currentStatus);
    
    if (currentIndex === -1) return; // Status not in our order - do nothing
    
    // Calculate progress percentage
    const progressPercentage = (currentIndex / (statusOrder.length - 1)) * 100;
    
    // Update progress line width
    if (progressLine) {
        progressLine.style.width = `${progressPercentage}%`;
    }
    
    // Update steps
    steps.forEach((step, index) => {
        // Get this step's status from data attribute
        const stepStatus = step.dataset.status;
        const stepIndex = statusOrder.indexOf(stepStatus);
        
        if (stepIndex < currentIndex) {
            // Completed step
            step.classList.add('completed');
            step.classList.remove('active');
        } else if (stepIndex === currentIndex) {
            // Current active step
            step.classList.add('active');
            step.classList.remove('completed');
        } else {
            // Future step
            step.classList.remove('active', 'completed');
        }
    });
}

/**
 * Create a new lead progress indicator dynamically
 * @param {Element} container - Container to append the progress indicator
 * @param {String} currentStatus - Current status of the lead
 */
function createLeadProgressIndicator(container, currentStatus) {
    // Define the flow of statuses
    const statusFlow = [
        { status: 'New', label: 'New Lead', icon: 'user-plus' },
        { status: 'Assigned', label: 'Teacher Assigned', icon: 'user-check' },
        { status: 'Demo Scheduled', label: 'Demo Scheduled', icon: 'calendar' },
        { status: 'Converted', label: 'Converted', icon: 'check-circle' }
    ];
    
    // Create container
    const progressContainer = document.createElement('div');
    progressContainer.className = 'lead-progress-container';
    progressContainer.dataset.status = currentStatus;
    
    // Create progress line
    const progressLine = document.createElement('div');
    progressLine.className = 'progress-line';
    progressContainer.appendChild(progressLine);
    
    // Create steps
    statusFlow.forEach((step, index) => {
        const stepEl = document.createElement('div');
        stepEl.className = 'lead-progress-step';
        stepEl.dataset.status = step.status;
        
        const circleEl = document.createElement('div');
        circleEl.className = 'step-circle';
        
        // Add icon or number
        if (feather) {
            // If feather is available, use icons
            const iconEl = document.createElement('i');
            iconEl.dataset.feather = step.icon;
            circleEl.appendChild(iconEl);
        } else {
            // Otherwise use numbers
            circleEl.innerText = index + 1;
        }
        
        const titleEl = document.createElement('div');
        titleEl.className = 'step-title';
        titleEl.innerText = step.label;
        
        stepEl.appendChild(circleEl);
        stepEl.appendChild(titleEl);
        progressContainer.appendChild(stepEl);
    });
    
    // Append to container
    container.appendChild(progressContainer);
    
    // Initialize icons if feather is available
    if (typeof feather !== 'undefined') {
        feather.replace({
            width: 16,
            height: 16
        });
    }
    
    // Initialize the progress indicator
    const steps = progressContainer.querySelectorAll('.lead-progress-step');
    updateProgressIndicator(steps, progressLine, currentStatus);
    
    // Add animation class after a short delay
    setTimeout(() => {
        progressContainer.classList.add('animate');
    }, 200);
}