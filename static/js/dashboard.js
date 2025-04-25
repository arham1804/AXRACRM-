// Dashboard charts and dynamic data loading

// Define global initialization function that will be called after all utilities are loaded
function initializePage() {
    try {
        console.log('Initializing dashboard page...');
        
        // Initialize charts
        initLeadStatusChart();
        initAssignmentStatusChart();
        initDemoStatusChart();
        initMonthlyTrendsChart();
        
        // Add event listeners
        setupRefreshButton();
        
        // Setup export buttons
        setupExportButtons();
        
        console.log('Dashboard initialized successfully');
    } catch (error) {
        console.error('Error initializing dashboard:', error);
    }
}

// Also define jQuery ready handler for backward compatibility
$(document).ready(function() {
    // If not already initialized, try to initialize
    if (typeof initializePage === 'function' && !window.dashboardInitialized) {
        window.dashboardInitialized = true;
        initializePage();
    }
});

// Lead Status Chart
function initLeadStatusChart() {
    try {
        const ctx = document.getElementById('leadStatusChart');
        if (!ctx) {
            console.warn('Lead status chart element not found');
            return;
        }
        
        const statsAttr = ctx.getAttribute('data-stats');
        if (!statsAttr) {
            console.warn('No data-stats attribute found on lead status chart');
            return;
        }
        
        // Safely parse JSON data
        let leadData;
        try {
            leadData = JSON.parse(statsAttr);
        } catch (e) {
            console.error('Failed to parse lead status data:', e, statsAttr);
            leadData = { new: 0, assigned: 0, converted: 0, lost: 0 };
        }
        
        console.log('Lead status data:', leadData);
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['New', 'Assigned', 'Converted', 'Lost'],
                datasets: [{
                    data: [
                        leadData.new || 0,
                        leadData.assigned || 0,
                        leadData.converted || 0,
                        leadData.lost || 0
                    ],
                    backgroundColor: [
                        '#0dcaf0', // info
                        '#ffc107', // warning
                        '#198754', // success
                        '#dc3545'  // danger
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#f8f9fa' // light text color for dark theme
                        }
                    },
                    title: {
                        display: true,
                        text: 'Lead Status Distribution',
                        color: '#f8f9fa'
                    }
                }
            }
        });
        
        console.log('Lead status chart initialized');
    } catch (error) {
        console.error('Error initializing lead status chart:', error);
    }
}

// Assignment Status Chart
function initAssignmentStatusChart() {
    try {
        const ctx = document.getElementById('assignmentStatusChart');
        if (!ctx) {
            console.warn('Assignment status chart element not found');
            return;
        }
        
        const statsAttr = ctx.getAttribute('data-stats');
        if (!statsAttr) {
            console.warn('No data-stats attribute found on assignment status chart');
            return;
        }
        
        // Safely parse JSON data
        let assignmentData;
        try {
            assignmentData = JSON.parse(statsAttr);
        } catch (e) {
            console.error('Failed to parse assignment status data:', e, statsAttr);
            assignmentData = { pending: 0, demo_scheduled: 0, converted: 0, cancelled: 0 };
        }
        
        console.log('Assignment status data:', assignmentData);
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'Demo Scheduled', 'Converted', 'Cancelled'],
                datasets: [{
                    data: [
                        assignmentData.pending || 0,
                        assignmentData.demo_scheduled || 0,
                        assignmentData.converted || 0,
                        assignmentData.cancelled || 0
                    ],
                    backgroundColor: [
                        '#6c757d', // secondary
                        '#0d6efd', // primary
                        '#198754', // success
                        '#dc3545'  // danger
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#f8f9fa' // light text color for dark theme
                        }
                    },
                    title: {
                        display: true,
                        text: 'Assignment Status Distribution',
                        color: '#f8f9fa'
                    }
                }
            }
        });
        
        console.log('Assignment status chart initialized');
    } catch (error) {
        console.error('Error initializing assignment status chart:', error);
    }
}

// Demo Status Chart
function initDemoStatusChart() {
    try {
        const ctx = document.getElementById('demoStatusChart');
        if (!ctx) {
            console.warn('Demo status chart element not found');
            return;
        }
        
        const statsAttr = ctx.getAttribute('data-stats');
        if (!statsAttr) {
            console.warn('No data-stats attribute found on demo status chart');
            return;
        }
        
        // Safely parse JSON data
        let demoData;
        try {
            demoData = JSON.parse(statsAttr);
        } catch (e) {
            console.error('Failed to parse demo status data:', e, statsAttr);
            demoData = { scheduled: 0, completed: 0, cancelled: 0 };
        }
        
        console.log('Demo status data:', demoData);
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Scheduled', 'Completed', 'Cancelled'],
                datasets: [{
                    data: [
                        demoData.scheduled || 0,
                        demoData.completed || 0,
                        demoData.cancelled || 0
                    ],
                    backgroundColor: [
                        '#0d6efd', // primary
                        '#198754', // success
                        '#dc3545'  // danger
                    ],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            color: '#f8f9fa' // light text color for dark theme
                        }
                    },
                    title: {
                        display: true,
                        text: 'Demo Status Distribution',
                        color: '#f8f9fa'
                    }
                }
            }
        });
        
        console.log('Demo status chart initialized');
    } catch (error) {
        console.error('Error initializing demo status chart:', error);
    }
}

// Monthly Trends Chart
function initMonthlyTrendsChart() {
    try {
        const ctx = document.getElementById('monthlyTrendsChart');
        if (!ctx) {
            console.warn('Monthly trends chart element not found');
            return;
        }
        
        // Safely parse months data
        let months;
        try {
            const monthsAttr = ctx.getAttribute('data-months');
            if (!monthsAttr) {
                console.warn('No data-months attribute found on monthly trends chart');
                return;
            }
            months = JSON.parse(monthsAttr);
        } catch (e) {
            console.error('Failed to parse months data:', e);
            months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        }
        
        // Safely parse leads data
        let leads;
        try {
            const leadsAttr = ctx.getAttribute('data-leads');
            if (!leadsAttr) {
                console.warn('No data-leads attribute found on monthly trends chart');
                return;
            }
            leads = JSON.parse(leadsAttr);
        } catch (e) {
            console.error('Failed to parse leads data:', e);
            leads = [0, 0, 0, 0, 0, 0];
        }
        
        // Safely parse conversions data
        let conversions;
        try {
            const conversionsAttr = ctx.getAttribute('data-conversions');
            if (!conversionsAttr) {
                console.warn('No data-conversions attribute found on monthly trends chart');
                return;
            }
            conversions = JSON.parse(conversionsAttr);
        } catch (e) {
            console.error('Failed to parse conversions data:', e);
            conversions = [0, 0, 0, 0, 0, 0];
        }
        
        console.log('Monthly trends data:', { months, leads, conversions });
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: months,
                datasets: [
                    {
                        label: 'New Leads',
                        data: leads,
                        borderColor: '#0dcaf0', // info
                        backgroundColor: 'rgba(13, 202, 240, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.2
                    },
                    {
                        label: 'Conversions',
                        data: conversions,
                        borderColor: '#198754', // success
                        backgroundColor: 'rgba(25, 135, 84, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.2
                    }
                ]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'top',
                        labels: {
                            color: '#f8f9fa' // light text color for dark theme
                        }
                    },
                    title: {
                        display: true,
                        text: 'Monthly Lead and Conversion Trends',
                        color: '#f8f9fa'
                    }
                },
                scales: {
                    x: {
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            color: '#f8f9fa'
                        }
                    },
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(255, 255, 255, 0.1)'
                        },
                        ticks: {
                            precision: 0,
                            color: '#f8f9fa'
                        }
                    }
                }
            }
        });
        
        console.log('Monthly trends chart initialized');
    } catch (error) {
        console.error('Error initializing monthly trends chart:', error);
    }
}

// Setup refresh button
function setupRefreshButton() {
    const refreshBtn = document.getElementById('refreshDashboard');
    if (!refreshBtn) return;
    
    refreshBtn.addEventListener('click', function() {
        // Show loading indicator
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) {
            loadingIndicator.classList.remove('d-none');
        }
        
        // Fetch fresh data
        fetch('/api/dashboard/stats')
            .then(response => response.json())
            .then(data => {
                // Update stats
                updateDashboardStats(data);
                
                // Update charts
                updateCharts(data);
                
                // Hide loading indicator
                if (loadingIndicator) {
                    loadingIndicator.classList.add('d-none');
                }
                
                // Show success message
                showToast('Dashboard refreshed successfully!');
            })
            .catch(error => {
                console.error('Error refreshing dashboard:', error);
                
                // Hide loading indicator
                if (loadingIndicator) {
                    loadingIndicator.classList.add('d-none');
                }
                
                // Show error message
                showToast('Failed to refresh dashboard data', 'error');
            });
    });
}

// Update dashboard statistics
function updateDashboardStats(data) {
    // Update total counts
    const elements = {
        'totalLeads': data.total_leads || 0,
        'totalTeachers': data.total_teachers || 0,
        'totalAssignments': data.total_assignments || 0,
        'totalDemos': data.total_demos || 0,
        'leadConversionRate': data.lead_to_demo_rate || 0,
        'demoConversionRate': data.demo_to_conversion_rate || 0
    };
    
    for (const [id, value] of Object.entries(elements)) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
    
    // Update recent activity tables
    updateRecentLeads(data.recent_leads || []);
    updateRecentDemos(data.recent_demos || []);
    
    // Update top teachers table
    updateTopTeachers(data.top_teachers || []);
}

// Update recent leads table
function updateRecentLeads(leads) {
    const tableBody = document.querySelector('#recentLeadsTable tbody');
    if (!tableBody) return;
    
    // Clear current rows
    tableBody.innerHTML = '';
    
    if (leads.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="5" class="text-center">No recent leads found</td>';
        tableBody.appendChild(row);
        return;
    }
    
    // Add new rows
    leads.forEach(lead => {
        const row = document.createElement('tr');
        
        const statusClass = `status-${lead.status.toLowerCase()}`;
        
        row.innerHTML = `
            <td>${lead.name}</td>
            <td>${lead.area}</td>
            <td>${lead.class_level}</td>
            <td>${lead.created_at}</td>
            <td><span class="badge ${statusClass}">${lead.status}</span></td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Update recent demos table
function updateRecentDemos(demos) {
    const tableBody = document.querySelector('#recentDemosTable tbody');
    if (!tableBody) return;
    
    // Clear current rows
    tableBody.innerHTML = '';
    
    if (demos.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="4" class="text-center">No recent demos found</td>';
        tableBody.appendChild(row);
        return;
    }
    
    // Add new rows
    demos.forEach(demo => {
        const row = document.createElement('tr');
        
        const statusClass = `status-${demo.status.toLowerCase()}`;
        
        row.innerHTML = `
            <td>${demo.student_name}</td>
            <td>${demo.teacher_name}</td>
            <td>${demo.scheduled_date}</td>
            <td><span class="badge ${statusClass}">${demo.status}</span></td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Update top teachers table
function updateTopTeachers(teachers) {
    const tableBody = document.querySelector('#topTeachersTable tbody');
    if (!tableBody) return;
    
    // Clear current rows
    tableBody.innerHTML = '';
    
    if (teachers.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="4" class="text-center">No teacher data found</td>';
        tableBody.appendChild(row);
        return;
    }
    
    // Add new rows
    teachers.forEach(teacher => {
        const row = document.createElement('tr');
        
        row.innerHTML = `
            <td>${teacher.name}</td>
            <td>${teacher.total_assignments}</td>
            <td>${teacher.conversions}</td>
            <td>${teacher.conversion_rate}%</td>
        `;
        
        tableBody.appendChild(row);
    });
}

// Update charts with new data
function updateCharts(data) {
    // Update chart data
    window.location.reload(); // Simple refresh for now to update charts
}

// Show toast notification using the toastNotification utility
function showToast(message, type = 'success') {
    // Check if toastNotification is available
    if (typeof toastNotification !== 'undefined') {
        // Use our toast notification system
        if (type === 'success') {
            toastNotification.success(message);
        } else if (type === 'error') {
            toastNotification.error(message);
        } else if (type === 'warning') {
            toastNotification.warning(message);
        } else {
            toastNotification.info(message);
        }
    } else {
        // Fallback to native browser alert
        console.warn('Toast notification system not available');
        alert(message);
    }
}

// Setup export buttons for dashboard tables
function setupExportButtons() {
    try {
        // Check if export utility is available
        if (typeof addExportDropdown === 'function') {
            // Add export dropdown to recent leads
            addExportDropdown('recentLeadsExport', 'recentLeadsTable', 'recent_leads');
            
            // Add export dropdown to recent demos
            addExportDropdown('recentDemosExport', 'recentDemosTable', 'recent_demos');
            
            // Add export dropdown to top teachers
            addExportDropdown('topTeachersExport', 'topTeachersTable', 'top_teachers');
            
            console.log('Dashboard export buttons initialized');
        } else {
            console.warn('Export utility not available');
        }
    } catch (error) {
        console.error('Error setting up export buttons:', error);
    }
}
