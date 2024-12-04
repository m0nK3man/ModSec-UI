function expandAllRows() {
    // Add click event listeners to all summary elements
    document.querySelectorAll('summary').forEach(summary => {
        summary.addEventListener('dblclick', function(e) {
            // Prevent the default toggle behavior
            e.preventDefault();
	    console.log(e)
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
}

// Lấy phần tử div cần theo dõi
var divElement = document.querySelector('.logs-table');

// Bắt sự kiện tùy chỉnh
divElement.addEventListener('lengthChange', (event) => {
//    console.log(`Div resized: Width=${event.detail.width}, Height=${event.detail.height}`);
    expandAllRows();
});

// Theo dõi phần tử div
observer.observe(divElement);
