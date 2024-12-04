// Function to safely sanitize and display log content
function wrapUrlsInDetails() {
    const expandCells = document.querySelectorAll('.logs-table td.expand-cell');

    expandCells.forEach(cell => {
        const fullText = cell.innerText.trim();	
        const separatorIndex = fullText.indexOf('---');
	const hasDetails = cell.querySelector('details') !== null;
        const hasSummary = cell.querySelector('summary') !== null;

        // work with summary and details field split by "---"
	if ((separatorIndex !== -1) && !(hasDetails && hasSummary)) {
            var MSGText = fullText.substring(0, separatorIndex).trim();
            var DetailsText = fullText.substring(separatorIndex + 3).trim();
	    if (!MSGText) {
                MSGText = 'N/A';
            }

            if (!DetailsText) {
                DetailsText = 'N/A';
            }

            // Create the HTML structure
            cell.innerHTML = `
                <details>
                    <summary></summary>
		    <div>
		        ---
                        <br>
                        Details:
                        <br>
		    </div>
                    <div class="full-msg"></div>
                </details>
            `;
	    // use innerText to avoid XSS
	    cell.querySelector('summary').innerText = `▽ ${MSGText}`
	    cell.getElementsByClassName('full-msg')[0].innerText = `${DetailsText}`
        }
	// work with the field already converted
	else if (hasDetails && hasSummary) {
	    
	}
	// work with a long field full text
	else {
	    if (fullText.length > 40) {
		const truncated = fullText.substring(0, 40);
		// Create the HTML structure
                cell.innerHTML = `
                    <details>
                        <summary></summary>
                        <div class="full-msg"></div>
                    </details>
                `;
		// use innerText to avoid XSS
		cell.querySelector('summary').innerText = `▽ ${truncated}`
		cell.getElementsByClassName('full-msg')[0].innerText = `${fullText}`
	        
		// Add toggle event listener
                const details = cell.querySelector('details');
                const summary = cell.querySelector('summary');
                const originalText = `▽ ${truncated}`;

                details.addEventListener('toggle', (e) => {
                    if (details.open) {
                        summary.innerText = "△";
                    } else {
                        summary.innerText = originalText;
                    }
                }); 
	    }
        }
    });
}

// Lấy phần tử div cần theo dõi
var divElement = document.querySelector('.logs-table');

// Bắt sự kiện tùy chỉnh
divElement.addEventListener('lengthChange', (event) => {
//    console.log(`Div resized: Width=${event.detail.width}, Height=${event.detail.height}`);
    wrapUrlsInDetails();
});

// Theo dõi phần tử div
observer.observe(divElement);
