document.addEventListener('DOMContentLoaded', function() {
    // Add click event listeners to all summary elements
    document.querySelectorAll('summary').forEach(summary => {
        summary.addEventListener('click', function(e) {
            // Prevent the default toggle behavior
            e.preventDefault();

            // Find the parent row
            const row = this.closest('tr');

            // Find if the clicked details element is open or closed
            const parentDetails = this.parentElement;
            const isOpening = !parentDetails.hasAttribute('open');

            // Toggle all details elements in the same row
            row.querySelectorAll('details').forEach(details => {
                if (isOpening) {
                    details.setAttribute('open', '');
                } else {
                    details.removeAttribute('open');
                }
            });

            // Update the summary text/symbol if you're using ▽ as toggle
            row.querySelectorAll('summary').forEach(sum => {
                const text = sum.textContent;
                if (isOpening) {
                    sum.textContent = text.replace('▽', '△');
                } else {
                    sum.textContent = text.replace('△', '▽');
                }
            });
        });
    });
});
