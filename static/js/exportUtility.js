/**
 * Export Utility for Axra Tutor CRM
 * Provides functionality to export table data to various formats
 */

// Initialize when jQuery is ready
jQueryReady(function() {
    // Listen for export button clicks
    $('.export-csv-btn').on('click', function(e) {
        e.preventDefault();
        exportTableToCSV($(this).data('table-id'), $(this).data('filename') || 'export');
    });
    
    $('.export-pdf-btn').on('click', function(e) {
        e.preventDefault();
        
        // Check if we have notification system
        if (typeof toastNotification !== 'undefined') {
            toastNotification.info('PDF export is being implemented. Please use CSV export for now.');
        } else {
            alert('PDF export is being implemented. Please use CSV export for now.');
        }
    });
});

/**
 * Export table data to CSV file
 * @param {string} tableId - The ID of the table to export
 * @param {string} filename - The name of the file (without extension)
 */
function exportTableToCSV(tableId, filename = 'export') {
    try {
        const table = document.getElementById(tableId);
        if (!table) {
            console.error('Table not found:', tableId);
            
            if (typeof toastNotification !== 'undefined') {
                toastNotification.error('Table not found. Please try again.');
            }
            return;
        }
        
        // Get all rows from table
        const rows = table.querySelectorAll('tr');
        if (!rows || rows.length === 0) {
            console.error('No rows found in table');
            
            if (typeof toastNotification !== 'undefined') {
                toastNotification.warning('No data to export.');
            }
            return;
        }
        
        // Prepare CSV content
        let csvContent = 'data:text/csv;charset=utf-8,';
        
        // Process each row
        rows.forEach(function(row) {
            const rowData = [];
            // Get all cells in the row
            const cells = row.querySelectorAll('th, td');
            
            cells.forEach(function(cell) {
                // Clean the cell text: replace multiple spaces, newlines with a single space
                let cellText = cell.textContent.replace(/\s+/g, ' ').trim();
                
                // Escape quotes in the cell text and wrap with quotes
                cellText = '"' + cellText.replace(/"/g, '""') + '"';
                
                rowData.push(cellText);
            });
            
            // Add row to CSV
            csvContent += rowData.join(',') + '\r\n';
        });
        
        // Create download link
        const encodedUri = encodeURI(csvContent);
        const link = document.createElement('a');
        link.setAttribute('href', encodedUri);
        link.setAttribute('download', filename + '.csv');
        document.body.appendChild(link);
        
        // Trigger download
        link.click();
        document.body.removeChild(link);
        
        // Show success message
        if (typeof toastNotification !== 'undefined') {
            toastNotification.success('Data exported successfully to CSV.');
        }
    } catch (error) {
        console.error('Error exporting to CSV:', error);
        
        if (typeof toastNotification !== 'undefined') {
            toastNotification.error('Failed to export data. Please try again.');
        }
    }
}

/**
 * Add the export utility dropdown to a page
 * @param {string} containerId - The ID of the container to add the dropdown to
 * @param {string} tableId - The ID of the table to export
 * @param {string} filename - The base filename for exports
 */
function addExportDropdown(containerId, tableId, filename) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    const exportDropdown = `
        <div class="dropdown ms-2">
            <button class="btn btn-outline-primary dropdown-toggle" type="button" id="exportDropdownBtn" 
                    data-bs-toggle="dropdown" aria-expanded="false">
                <i data-feather="download" class="feather-sm me-1"></i> Export
            </button>
            <ul class="dropdown-menu dropdown-menu-end" aria-labelledby="exportDropdownBtn">
                <li>
                    <a class="dropdown-item export-csv-btn" href="#" data-table-id="${tableId}" data-filename="${filename}">
                        <i data-feather="file-text" class="feather-sm me-2"></i> Export as CSV
                    </a>
                </li>
                <li>
                    <a class="dropdown-item export-pdf-btn" href="#" data-table-id="${tableId}" data-filename="${filename}">
                        <i data-feather="file" class="feather-sm me-2"></i> Export as PDF
                    </a>
                </li>
            </ul>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', exportDropdown);
    
    // Re-initialize Feather icons
    if (typeof feather !== 'undefined') {
        feather.replace();
    }
}