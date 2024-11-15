// Function to safely sanitize and display log content
function wrapUrlsInDetails() {
    const expandCells = document.querySelectorAll('.logs-table td.expand-cell');

    expandCells.forEach(cell => {
        const fullText = cell.innerText.trim();
        const separatorIndex = fullText.indexOf('---');
        
        if (separatorIndex !== -1) {
            var MSGText = fullText.substring(0, separatorIndex).trim();
            var DetailsText = fullText.substring(separatorIndex + 3).trim();
            
	    if (!MSGText) {
                MSGText = 'N/A';
            }

            if (!DetailsText) {
                DetailsText = 'N/A';
            }

	    // Sanitize both MSG and Details text using DOMPurify
            const sanitizedMSG = DOMPurify.sanitize(MSGText, {
                ALLOWED_TAGS: [], // Only allow text content for MSG
                ALLOWED_ATTR: []
            });
            
            const sanitizedDetails = DOMPurify.sanitize(DetailsText, {
                ALLOWED_TAGS: ['br', 'p', 'span', 'div'], // Allow basic formatting for details
                ALLOWED_ATTR: ['class']
            });

            // Create the HTML structure with sanitized content
            const sanitizedHTML = `
                <details>
                    <summary>▽ ${sanitizedMSG}</summary>
                    <div class="full-msg">---<br>Details:<br>${sanitizedDetails}</div>
                </details>
            `;

            // Sanitize the entire HTML structure as an additional security measure
            cell.innerHTML = DOMPurify.sanitize(sanitizedHTML, {
                ALLOWED_TAGS: ['details', 'summary', 'div', 'br'],
                ALLOWED_ATTR: ['class']
            });
        } else {
	    if (fullText.length > 20) {
		const truncated = "▽ " + fullText.substring(0, 40);
		// Create details structure
                cell.innerHTML = `
                    <details>
                        <summary>${truncated}</summary>
                        <div class="full-url">${fullText}</div>
                    </details>
                `;
	        // Add toggle event listener
                const details = cell.querySelector('details');
                const summary = cell.querySelector('summary');
                const originalText = summary.innerHTML;

                details.addEventListener('toggle', (e) => {
                    if (details.open) {
                        summary.innerHTML = "△";
                    } else {
                        summary.innerHTML = originalText;
                    }
                }); 
	    }
        }
    });
}

// Add event listener for both initial load and any dynamic updates
document.addEventListener('DOMContentLoaded', wrapUrlsInDetails);
