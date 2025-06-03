// Global chart instances
let leadStatusChartInstance = null;
let assignmentStatusChartInstance = null;
let demoStatusChartInstance = null;
let monthlyTrendsChartInstance = null;

// Auto-refresh interval in milliseconds (e.g., 5 minutes)
const AUTO_REFRESH_INTERVAL = 5 * 60 * 1000;
let autoRefreshTimer = null;

// Initialize SocketIO client
const socket = io();

// Listen for new notifications
socket.on('new_notification', function(notification) {
    console.log('Received new notification:', notification);

    // Parse and convert created_at to local time string if available
    let localTimeStr = '';
    if (notification.created_at) {
        let parsedDate = null;

        // Try parsing as ISO 8601 with 'Z' (UTC) suffix
        try {
            parsedDate = new Date(notification.created_at + 'Z');
            if (isNaN(parsedDate.getTime())) {
                parsedDate = null;
            }
        } catch (e) {
            parsedDate = null;
        }

        // If failed, try parsing as local time (replace space with 'T' for ISO format)
        if (!parsedDate) {
            try {
                parsedDate = new Date(notification.created_at.replace(' ', 'T'));
                if (isNaN(parsedDate.getTime())) {
                    parsedDate = null;
                }
            } catch (e) {
                parsedDate = null;
            }
        }

        // If still failed, fallback to original parsing with ' UTC'
        if (!parsedDate) {
            parsedDate = new Date(notification.created_at + ' UTC');
        }

        if (!isNaN(parsedDate.getTime())) {
            // Include timezone offset in display
            const options = {
                year: 'numeric',
                month: 'short',
                day: 'numeric',
                hour: '2-digit',
                minute: '2-digit',
                hour12: false,
                timeZoneName: 'short'
            };
            localTimeStr = parsedDate.toLocaleString(undefined, options);
        }
    }

    const displayMessage = localTimeStr
        ? `[${localTimeStr}] ${notification.title}: ${notification.message}`
        : `${notification.title}: ${notification.message}`;

    if (typeof toastNotification !== 'undefined') {
        toastNotification.info(displayMessage);
    } else {
        alert(displayMessage);
    }
});

// Define global initialization function that will be called after all utilities are loaded
function initializePage() {
    try {
        console.log('Initializing dashboard page...');
        
        // Make sure Chart.js is loaded
        if (typeof Chart === 'undefined') {
            console.error('Chart.js is not loaded! Unable to initialize charts.');
            return;
        }
        
        // Initialize charts
        initLeadStatusChart();
        initAssignmentStatusChart();
        initDemoStatusChart();
        initMonthlyTrendsChart();
        
        // Add event listeners
        setupRefreshButton();
        
        // Setup export buttons
        if (typeof addExportDropdown === 'function') {
            setupExportButtons();
        } else {
            console.warn('Export utility not loaded properly');
        }
        
        // Start auto-refresh timer
        startAutoRefresh();

        // Start clock update
        startClockUpdate();
        
        console.log('Dashboard initialized successfully');
    } catch (error) {
        console.error('Error initializing dashboard:', error);
    }
}

// Function to update the dashboard clock every second
function startClockUpdate() {
    const clockElement = document.getElementById('dashboardClock');
    if (!clockElement) {
        console.warn('Dashboard clock element not found');
        return;
    }

    function updateClock() {
        const now = new Date();
        const options = {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false
        };
        const formatted = now.toLocaleString('en-US', options);
        clockElement.textContent = formatted;
    }

    updateClock(); // initial call
    setInterval(updateClock, 1000);
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
        
        // Get data from the canvas element
        let leadData;
        try {
            let statsAttr = ctx.getAttribute('data-stats');
            if (!statsAttr) {
                leadData = { new: 0, assigned: 0, converted: 0, lost: 0 };
            } else {
                if (typeof statsAttr === 'string') {
                    if (statsAttr.trim().startsWith('{')) {
                        leadData = JSON.parse(statsAttr);
                    } else {
                        statsAttr = statsAttr.replace(/"/g, '"')
                                           .replace(/&#39;/g, "'")
                                           .replace(/</g, '<')
                                           .replace(/>/g, '>');
                        leadData = JSON.parse(statsAttr);
                    }
                } else if (typeof statsAttr === 'object') {
                    leadData = statsAttr;
                } else {
                    leadData = { new: 0, assigned: 0, converted: 0, lost: 0 };
                }
            }
        } catch (e) {
            leadData = { new: 0, assigned: 0, converted: 0, lost: 0 };
        }
        
        if (leadStatusChartInstance) {
            leadStatusChartInstance.data.datasets[0].data = [
                leadData.new || 0,
                leadData.assigned || 0,
                leadData.converted || 0,
                leadData.lost || 0
            ];
            leadStatusChartInstance.update();
        } else {
            leadStatusChartInstance = new Chart(ctx, {
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
                            '#0dcaf0',
                            '#ffc107',
                            '#198754',
                            '#dc3545'
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
                                color: '#f8f9fa'
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
        
        let assignmentData;
        try {
            let statsAttr = ctx.getAttribute('data-stats');
            if (!statsAttr) {
                assignmentData = { pending: 0, demo_scheduled: 0, converted: 0, cancelled: 0 };
            } else {
                if (typeof statsAttr === 'string') {
                    if (statsAttr.trim().startsWith('{')) {
                        assignmentData = JSON.parse(statsAttr);
                    } else {
                        statsAttr = statsAttr.replace(/"/g, '"')
                                           .replace(/&#39;/g, "'")
                                           .replace(/</g, '<')
                                           .replace(/>/g, '>');
                        assignmentData = JSON.parse(statsAttr);
                    }
                } else if (typeof statsAttr === 'object') {
                    assignmentData = statsAttr;
                } else {
                    assignmentData = { pending: 0, demo_scheduled: 0, converted: 0, cancelled: 0 };
                }
            }
        } catch (e) {
            assignmentData = { pending: 0, demo_scheduled: 0, converted: 0, cancelled: 0 };
        }
        
        if (assignmentStatusChartInstance) {
            assignmentStatusChartInstance.data.datasets[0].data = [
                assignmentData.pending || 0,
                assignmentData.demo_scheduled || 0,
                assignmentData.converted || 0,
                assignmentData.cancelled || 0
            ];
            assignmentStatusChartInstance.update();
        } else {
            assignmentStatusChartInstance = new Chart(ctx, {
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
                            '#6c757d',
                            '#0d6efd',
                            '#198754',
                            '#dc3545'
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
                                color: '#f8f9fa'
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
        
        let demoData;
        try {
            let statsAttr = ctx.getAttribute('data-stats');
            if (!statsAttr) {
                demoData = { scheduled: 0, completed: 0, cancelled: 0 };
            } else {
                if (typeof statsAttr === 'string') {
                    if (statsAttr.trim().startsWith('{')) {
                        demoData = JSON.parse(statsAttr);
                    } else {
                        statsAttr = statsAttr.replace(/"/g, '"')
                                           .replace(/&#39;/g, "'")
                                           .replace(/</g, '<')
                                           .replace(/>/g, '>');
                        demoData = JSON.parse(statsAttr);
                    }
                } else if (typeof statsAttr === 'object') {
                    demoData = statsAttr;
                } else {
                    demoData = { scheduled: 0, completed: 0, cancelled: 0 };
                }
            }
        } catch (e) {
            demoData = { scheduled: 0, completed: 0, cancelled: 0 };
        }
        
        if (demoStatusChartInstance) {
            demoStatusChartInstance.data.datasets[0].data = [
                demoData.scheduled || 0,
                demoData.completed || 0,
                demoData.cancelled || 0
            ];
            demoStatusChartInstance.update();
        } else {
            demoStatusChartInstance = new Chart(ctx, {
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
                            '#0d6efd',
                            '#198754',
                            '#dc3545'
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
                                color: '#f8f9fa'
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
        
        const defaultMonths = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
        const defaultLeads = [0, 0, 0, 0, 0, 0];
        const defaultConversions = [0, 0, 0, 0, 0, 0];
        
        let months = defaultMonths;
        try {
            let monthsAttr = ctx.getAttribute('data-months');
            if (monthsAttr) {
                monthsAttr = monthsAttr.replace(/"/g, '"')
                                   .replace(/&#39;/g, "'")
                                   .replace(/</g, '<')
                                   .replace(/>/g, '>');
                                   
                if (monthsAttr.trim().startsWith('[')) {
                    const parsedData = JSON.parse(monthsAttr);
                    if (Array.isArray(parsedData) && parsedData.length > 0) {
                        months = parsedData;
                    }
                }
            }
        } catch (e) {
            months = defaultMonths;
        }
        
        let leads = defaultLeads;
        try {
            let leadsAttr = ctx.getAttribute('data-leads');
            if (leadsAttr) {
                leadsAttr = leadsAttr.replace(/"/g, '"')
                                   .replace(/&#39;/g, "'")
                                   .replace(/</g, '<')
                                   .replace(/>/g, '>');
                                   
                if (leadsAttr.trim().startsWith('[')) {
                    const parsedData = JSON.parse(leadsAttr);
                    if (Array.isArray(parsedData)) {
                        leads = parsedData;
                    }
                }
            }
        } catch (e) {
            leads = defaultLeads;
        }
        
        let conversions = defaultConversions;
        try {
            let conversionsAttr = ctx.getAttribute('data-conversions');
            if (conversionsAttr) {
                conversionsAttr = conversionsAttr.replace(/"/g, '"')
                                           .replace(/&#39;/g, "'")
                                           .replace(/</g, '<')
                                           .replace(/>/g, '>');
                                   
                if (conversionsAttr.trim().startsWith('[')) {
                    const parsedData = JSON.parse(conversionsAttr);
                    if (Array.isArray(parsedData)) {
                        conversions = parsedData;
                    }
                }
            }
        } catch (e) {
            conversions = defaultConversions;
        }
        
        if (monthlyTrendsChartInstance) {
            monthlyTrendsChartInstance.data.labels = months;
            monthlyTrendsChartInstance.data.datasets[0].data = leads;
            monthlyTrendsChartInstance.data.datasets[1].data = conversions;
            monthlyTrendsChartInstance.update();
        } else {
            monthlyTrendsChartInstance = new Chart(ctx, {
                type: 'line',
                data: {
                    labels: months,
                    datasets: [
                        {
                            label: 'New Leads',
                            data: leads,
                            borderColor: '#0dcaf0',
                            backgroundColor: 'rgba(13, 202, 240, 0.1)',
                            borderWidth: 2,
                            fill: true,
                            tension: 0.2
                        },
                        {
                            label: 'Conversions',
                            data: conversions,
                            borderColor: '#198754',
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
                                color: '#f8f9fa'
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
    } catch (error) {
        console.error('Error initializing monthly trends chart:', error);
    }
}

// Setup refresh button
function setupRefreshButton() {
    const refreshBtn = document.getElementById('refreshDashboard');
    if (!refreshBtn) return;
    
    refreshBtn.addEventListener('click', function() {
        const loadingIndicator = document.getElementById('loadingIndicator');
        if (loadingIndicator) {
            loadingIndicator.classList.remove('d-none');
        }
        
        fetch('/api/dashboard/stats')
            .then(response => response.json())
            .then(data => {
                updateDashboardStats(data);
                updateCharts(data);
                
                if (loadingIndicator) {
                    loadingIndicator.classList.add('d-none');
                }
                
                showToast('Dashboard refreshed successfully!');
            })
            .catch(error => {
                console.error('Error refreshing dashboard:', error);
                
                if (loadingIndicator) {
                    loadingIndicator.classList.add('d-none');
                }
                
                showToast('Failed to refresh dashboard data', 'error');
            });
    });
}

// Update dashboard statistics
function updateDashboardStats(data) {
    const elements = {
        'totalLeads': data.total_leads || 0,
        'totalTeachers': data.total_teachers || 0,
        'totalAssignments': data.total_assignments || 0,
        'totalDemos': data.total_demos || 0,
        'leadConversionRate': data.lead_to_demo_rate || 0,
        'demoConversionRate': data.demo_to_conversion_rate || 0,
        'callToLeadRate': data.call_to_lead_rate || 0,
        'leadToDemoRate': data.lead_to_demo_rate || 0,
        'demoToConversionRate': data.demo_to_conversion_rate || 0,
        'conversionToPaymentRate': data.conversion_to_payment_rate || 0,
        'salesOverview': data.sales_overview || 0,
        'totalSale': data.total_sale || 0,
        'demoConversionAvgTime': data.demo_conversion_avg_time || 0,
        'avgFeesPerConversion': data.avg_fees_per_conversion || 0
    };
    
    for (const [id, value] of Object.entries(elements)) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    }
    
    const leadProgress = document.getElementById('leadConversionProgress');
    if (leadProgress) {
        const leadRate = data.lead_to_demo_rate || 0;
        leadProgress.style.width = leadRate + '%';
        leadProgress.setAttribute('aria-valuenow', leadRate);
    }
    
    const demoProgress = document.getElementById('demoConversionProgress');
    if (demoProgress) {
        const demoRate = data.demo_to_conversion_rate || 0;
        demoProgress.style.width = demoRate + '%';
        demoProgress.setAttribute('aria-valuenow', demoRate);
    }
    
    updateRecentLeads(data.recent_leads || []);
    updateRecentDemos(data.recent_demos || []);
    updateTopTeachers(data.top_teachers || []);
    // Removed call to updateChats() as it is undefined and causes errors
}

// Update recent leads table
function updateRecentLeads(leads) {
    const tableBody = document.querySelector('#recentLeadsTable tbody');
    if (!tableBody) return;
    
    tableBody.innerHTML = '';
    
    if (leads.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="5" class="text-center">No recent leads found</td>';
        tableBody.appendChild(row);
        return;
    }
    
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
    
    tableBody.innerHTML = '';
    
    if (demos.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="4" class="text-center">No recent demos found</td>';
        tableBody.appendChild(row);
        return;
    }
    
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
    
    tableBody.innerHTML = '';
    
    if (teachers.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="4" class="text-center">No teacher data found</td>';
        tableBody.appendChild(row);
        return;
    }
    
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
    try {
        if (!data) {
            console.warn('No data provided to updateCharts');
            return;
        }
        
        if (leadStatusChartInstance && data.lead_status) {
            leadStatusChartInstance.data.datasets[0].data = [
                data.lead_status.new || 0,
                data.lead_status.assigned || 0,
                data.lead_status.converted || 0,
                data.lead_status.lost || 0
            ];
            leadStatusChartInstance.update();
        }
        
        if (assignmentStatusChartInstance && data.assignment_status) {
            assignmentStatusChartInstance.data.datasets[0].data = [
                data.assignment_status.pending || 0,
                data.assignment_status.demo_scheduled || 0,
                data.assignment_status.converted || 0,
                data.assignment_status.cancelled || 0
            ];
            assignmentStatusChartInstance.update();
        }
        
        if (demoStatusChartInstance && data.demo_status) {
            demoStatusChartInstance.data.datasets[0].data = [
                data.demo_status.scheduled || 0,
                data.demo_status.completed || 0,
                data.demo_status.cancelled || 0
            ];
            demoStatusChartInstance.update();
        }
        
        if (monthlyTrendsChartInstance && data.trend_months && data.trend_leads && data.trend_conversions) {
            monthlyTrendsChartInstance.data.labels = data.trend_months;
            monthlyTrendsChartInstance.data.datasets[0].data = data.trend_leads;
            monthlyTrendsChartInstance.data.datasets[1].data = data.trend_conversions;
            monthlyTrendsChartInstance.update();
        }
    } catch (error) {
        console.error('Error updating charts:', error);
    }
}

// Show toast notification using the toastNotification utility
function showToast(message, type = 'success') {
    if (typeof toastNotification !== 'undefined') {
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
        alert(message);
    }
}

// Setup export buttons for dashboard tables
function setupExportButtons() {
    if (typeof addExportDropdown !== 'function') {
        if (typeof window.exportUtilityLoaded === 'undefined') {
            const script = document.createElement('script');
            script.src = '/static/js/exportUtility.js';
            script.onload = function() {
                window.exportUtilityLoaded = true;
                setTimeout(setupExportButtons, 500);
            };
            document.head.appendChild(script);
        }
        return;
    }
    
    setTimeout(() => {
        const recentLeadsExport = document.getElementById('recentLeadsExport');
        if (recentLeadsExport) recentLeadsExport.innerHTML = '';
        
        const recentDemosExport = document.getElementById('recentDemosExport');
        if (recentDemosExport) recentDemosExport.innerHTML = '';
        
        const topTeachersExport = document.getElementById('topTeachersExport');
        if (topTeachersExport) topTeachersExport.innerHTML = '';
        
        if (recentLeadsExport && document.getElementById('recentLeadsTable')) {
            addExportDropdown('recentLeadsExport', 'recentLeadsTable', 'recent_leads');
        }
        
        if (recentDemosExport && document.getElementById('recentDemosTable')) {
            addExportDropdown('recentDemosExport', 'recentDemosTable', 'recent_demos');
        }
        
        if (topTeachersExport && document.getElementById('topTeachersTable')) {
            addExportDropdown('topTeachersExport', 'topTeachersTable', 'top_teachers');
        }
    }, 500);
}

// Start auto-refresh timer
function startAutoRefresh() {
    if (autoRefreshTimer) {
        clearInterval(autoRefreshTimer);
    }
    autoRefreshTimer = setInterval(() => {
        console.log('Auto-refreshing dashboard data...');
        fetch('/api/dashboard/stats')
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
        updateDashboardStats(data);
        updateCharts(data);
        showToast('Dashboard auto-refreshed');
    })
    .catch(error => {
        console.error('Error auto-refreshing dashboard:', error);
        showToast('Failed to auto-refresh dashboard data', 'error');
    });
    }, AUTO_REFRESH_INTERVAL);
}
