/**
 * Export Utility for Axra Tutor CRM
 * Provides functionality to export data in different formats (CSV, PDF, etc.)
 */

// Create the ExportUtility class
class ExportUtility {
    constructor() {
        console.log('Export utility initialized');
    }
    
    /**
     * Export table data to CSV
     * @param {HTMLTableElement|string} table - The table element or table ID
     * @param {string} filename - The filename for the downloaded file
     */
    exportTableToCSV(table, filename = 'exported-data.csv') {
        try {
            // Get table element if string ID was provided
            if (typeof table === 'string') {
                table = document.getElementById(table);
                if (!table) {
                    console.error(`Table with ID "${table}" not found`);
                    return;
                }
            }
            
            // Validate table element
            if (!(table instanceof HTMLTableElement)) {
                console.error('Invalid table element provided');
                return;
            }
            
            // Get all rows
            const rows = table.querySelectorAll('tr');
            
            // Create CSV content
            let csvContent = '';
            
            // Process each row
            rows.forEach(row => {
                const rowData = [];
                
                // Get all cells in the row (either th or td)
                const cells = row.querySelectorAll('th, td');
                
                // Process each cell
                cells.forEach(cell => {
                    // Get cell text content
                    let data = cell.textContent.trim();
                    
                    // Handle commas in the data (wrap in quotes)
                    if (data.includes(',')) {
                        data = `"${data}"`;
                    }
                    
                    // Add to row data
                    rowData.push(data);
                });
                
                // Add row to CSV content
                csvContent += rowData.join(',') + '\\n';
            });
            
            // Create Blob and URL
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            const url = URL.createObjectURL(blob);
            
            // Create download link
            const link = document.createElement('a');
            link.setAttribute('href', url);
            link.setAttribute('download', filename);
            link.style.display = 'none';
            
            // Add to document, click, and clean up
            document.body.appendChild(link);
            link.click();
            
            // Clean up
            document.body.removeChild(link);
            URL.revokeObjectURL(url);
            
            // Show success toast if available
            if (typeof showToast === 'function') {
                showToast(`Exported successfully to ${filename}`, 'success');
            }
            
            return true;
        } catch (error) {
            console.error('Error exporting table to CSV:', error);
            
            // Show error toast if available
            if (typeof showToast === 'function') {
                showToast('Failed to export data', 'error');
            }
            
            return false;
        }
    }
    
    /**
     * Export table data to PDF
     * @param {HTMLTableElement|string} table - The table element or table ID
     * @param {string} filename - The filename for the downloaded file
     */
    exportTableToPDF(table, filename = 'exported-data.pdf') {
        try {
            // Show modal or toast to indicate this is a preview feature
            if (typeof showToast === 'function') {
                showToast('PDF export is coming soon. CSV export is available now.', 'info', 'Preview Feature');
            }
            
            return false;
        } catch (error) {
            console.error('Error in PDF export:', error);
            
            // Show error toast if available
            if (typeof showToast === 'function') {
                showToast('PDF export is not available yet', 'warning');
            }
            
            return false;
        }
    }
    
    /**
     * Setup export buttons for a specific table
     * @param {string} tableId - The ID of the table to export
     * @param {string} exportContainerId - The ID of the container for export buttons
     * @param {string} title - The title to use for the exported file
     */
    setupExportButtons(tableId, exportContainerId, title = 'data') {
        try {
            const container = document.getElementById(exportContainerId);
            if (!container) {
                console.warn(`Export container with ID "${exportContainerId}" not found`);
                return;
            }
            
            const table = document.getElementById(tableId);
            if (!table) {
                console.warn(`Table with ID "${tableId}" not found`);
                return;
            }
            
            // Add event listeners to export buttons
            const csvButton = container.querySelector('.export-csv');
            if (csvButton) {
                csvButton.addEventListener('click', () => {
                    this.exportTableToCSV(table, `${title}-${this.getFormattedDate()}.csv`);
                });
            }
            
            const pdfButton = container.querySelector('.export-pdf');
            if (pdfButton) {
                pdfButton.addEventListener('click', () => {
                    this.exportTableToPDF(table, `${title}-${this.getFormattedDate()}.pdf`);
                });
            }
            
            // Make the export container visible
            container.style.display = 'block';
            
            return true;
        } catch (error) {
            console.error('Error setting up export buttons:', error);
            return false;
        }
    }
    
    /**
     * Get formatted date for filenames (YYYY-MM-DD)
     * @returns {string} Formatted date
     */
    getFormattedDate() {
        const now = new Date();
        const year = now.getFullYear();
        const month = String(now.getMonth() + 1).padStart(2, '0');
        const day = String(now.getDate()).padStart(2, '0');
        
        return `${year}-${month}-${day}`;
    }
}

// Create global instance
const exportUtility = new ExportUtility();

// Setup export buttons for all tables with export functionality
function setupExportButtons() {
    try {
        // Export buttons for student leads table
        exportUtility.setupExportButtons(
            'studentLeadsTable', 
            'studentLeadsExport', 
            'student-leads'
        );
        
        // Export buttons for teachers table
        exportUtility.setupExportButtons(
            'teachersTable', 
            'teachersExport', 
            'teachers'
        );
        
        // Export buttons for assignments table
        exportUtility.setupExportButtons(
            'assignmentsTable', 
            'assignmentsExport', 
            'assignments'
        );
        
        // Export buttons for demos table
        exportUtility.setupExportButtons(
            'demosTable', 
            'demosExport', 
            'demos'
        );
        
        // Export buttons for communication templates table
        exportUtility.setupExportButtons(
            'communicationTemplatesTable', 
            'communicationTemplatesExport', 
            'communication-templates'
        );
        
        console.log('Dashboard export buttons initialized');
        return true;
    } catch (error) {
        console.error('Error setting up export buttons:', error);
        return false;
    }
}

// Make exportUtility available globally
window.ExportUtility = ExportUtility;
window.exportUtility = exportUtility;
window.setupExportButtons = setupExportButtons;