/**
 * Lead Progress Visualization
 * Manages the animated progress indicators for lead status
 */

document.addEventListener('DOMContentLoaded', function() {
    // Find all progress containers
    const progressContainers = document.querySelectorAll('.lead-progress-container');
    
    if (progressContainers.length === 0) return;
    
    // Initialize each progress container
    progressContainers.forEach(container => {
        const steps = container.querySelectorAll('.lead-progress-step');
        if (steps.length === 0) return;
        
        // Find the last active step
        let lastActiveIndex = -1;
        steps.forEach((step, index) => {
            if (step.classList.contains('active')) {
                lastActiveIndex = index;
            }
        });
        
        // Adjust the progress line width based on active steps
        const progressLine = container.querySelector('.progress-line');
        if (progressLine && lastActiveIndex >= 0) {
            // Calculate progress percentage
            const totalSteps = steps.length;
            const progressPercentage = ((lastActiveIndex + 1) / totalSteps) * 100;
            
            // Animate the progress line
            setTimeout(() => {
                progressLine.style.width = `${progressPercentage}%`;
                
                // Add pulse animation to the last active step
                if (lastActiveIndex >= 0 && lastActiveIndex < steps.length) {
                    const lastActiveStep = steps[lastActiveIndex];
                    const circle = lastActiveStep.querySelector('.step-circle');
                    if (circle) {
                        circle.classList.add('pulse');
                    }
                }
            }, 500);
        }
    });
    
    // Initialize any progress bars
    const progressBars = document.querySelectorAll('.progress-bar');
    if (progressBars.length > 0) {
        progressBars.forEach(bar => {
            const percentage = bar.getAttribute('aria-valuenow');
            setTimeout(() => {
                bar.style.width = `${percentage}%`;
            }, 300);
        });
    }
    
    // Re-initialize feather icons if needed
    if (typeof feather !== 'undefined' && feather.replace) {
        feather.replace();
    }
});