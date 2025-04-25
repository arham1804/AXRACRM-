// Dashboard charts and dynamic data loading

document.addEventListener('DOMContentLoaded', function() {
    // Initialize charts
    initLeadStatusChart();
    initAssignmentStatusChart();
    initDemoStatusChart();
    initMonthlyTrendsChart();
    
    // Add event listeners
    setupRefreshButton();
});

// Lead Status Chart
function initLeadStatusChart() {
    const ctx = document.getElementById('leadStatusChart');
    if (!ctx) return;
    
    let leadData = { new: 0, assigned: 0, converted: 0, lost: 0 };
    try {
        const dataAttr = ctx.getAttribute('data-stats');
        if (dataAttr) {
            leadData = JSON.parse(dataAttr) || leadData;
        }
    } catch (e) {
        console.error('Error parsing lead status data:', e);
    }
    
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
                    'rgba(111, 116, 221, 0.8)', // royal-blue-light
                    'rgba(255, 183, 77, 0.8)', // royal-gold
                    'rgba(67, 160, 71, 0.8)', // royal-green
                    'rgba(229, 57, 53, 0.8)'  // royal-red
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
}

// Assignment Status Chart
function initAssignmentStatusChart() {
    const ctx = document.getElementById('assignmentStatusChart');
    if (!ctx) return;
    
    let assignmentData = { pending: 0, demo_scheduled: 0, converted: 0, cancelled: 0 };
    try {
        const dataAttr = ctx.getAttribute('data-stats');
        if (dataAttr) {
            assignmentData = JSON.parse(dataAttr) || assignmentData;
        }
    } catch (e) {
        console.error('Error parsing assignment status data:', e);
    }
    
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
                    'rgba(158, 158, 158, 0.8)', // royal-gray
                    'rgba(100, 111, 212, 0.8)', // royal-purple-lighter
                    'rgba(67, 160, 71, 0.8)', // royal-green
                    'rgba(229, 57, 53, 0.8)'  // royal-red
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
}

// Demo Status Chart
function initDemoStatusChart() {
    const ctx = document.getElementById('demoStatusChart');
    if (!ctx) return;
    
    let demoData = { scheduled: 0, completed: 0, cancelled: 0 };
    try {
        const dataAttr = ctx.getAttribute('data-stats');
        if (dataAttr) {
            demoData = JSON.parse(dataAttr) || demoData;
        }
    } catch (e) {
        console.error('Error parsing demo status data:', e);
    }
    
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
                    'rgba(103, 58, 183, 0.8)', // royal-purple
                    'rgba(67, 160, 71, 0.8)', // royal-green
                    'rgba(229, 57, 53, 0.8)'  // royal-red
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
}

// Monthly Trends Chart
function initMonthlyTrendsChart() {
    const ctx = document.getElementById('monthlyTrendsChart');
    if (!ctx) return;
    
    let months = [];
    let leads = [];
    let conversions = [];
    
    try {
        const monthsAttr = ctx.getAttribute('data-months');
        const leadsAttr = ctx.getAttribute('data-leads');
        const conversionsAttr = ctx.getAttribute('data-conversions');
        
        if (monthsAttr) {
            months = JSON.parse(monthsAttr) || [];
        }
        
        if (leadsAttr) {
            leads = JSON.parse(leadsAttr) || [];
        }
        
        if (conversionsAttr) {
            conversions = JSON.parse(conversionsAttr) || [];
        }
    } catch (e) {
        console.error('Error parsing monthly trends data:', e);
    }
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: months,
            datasets: [
                {
                    label: 'New Leads',
                    data: leads,
                    borderColor: 'rgba(103, 58, 183, 0.8)', // royal-purple
                    backgroundColor: 'rgba(103, 58, 183, 0.1)',
                    borderWidth: 2,
                    fill: true,
                    tension: 0.2
                },
                {
                    label: 'Conversions',
                    data: conversions,
                    borderColor: 'rgba(255, 193, 7, 0.8)', // royal-gold
                    backgroundColor: 'rgba(255, 193, 7, 0.1)',
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

// Show toast notification
function showToast(message, type = 'success') {
    const toastContainer = document.getElementById('toastContainer');
    if (!toastContainer) return;
    
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'success' ? 'success' : 'danger'} border-0`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove toast after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}
