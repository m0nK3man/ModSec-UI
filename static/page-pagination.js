const itemsPerPage = 50; // Number of items to display per page
let currentPage = 1; // Current page number
const rows = document.querySelectorAll('.logs-table tbody tr'); // All rows in the table
const totalPages = Math.ceil(rows.length / itemsPerPage);

// Function to display the current page
function displayPage(page) {
    // Calculate start and end indices for the current page
    const start = (page - 1) * itemsPerPage;
    const end = start + itemsPerPage;

    // Hide all rows and only show the rows for the current page
    rows.forEach((row, index) => {
        if (index >= start && index < end) {
            row.style.display = ''; // Show row
        } else {
            row.style.display = 'none'; // Hide row
        }
    });

    // Update pagination info
    document.getElementById('page-info').innerText = `Page ${page} of ${totalPages}`;
    // Update button states
    document.getElementById('prev').disabled = page === 1;
    document.getElementById('next').disabled = page === totalPages;
}

// Function to handle next page
function nextPage() {
    if (currentPage < totalPages) {
        currentPage++;
        displayPage(currentPage);
    }
}

// Function to handle previous page
function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        displayPage(currentPage);
    }
}

// Event listeners for pagination buttons
document.getElementById('next').addEventListener('click', nextPage);
document.getElementById('prev').addEventListener('click', prevPage);

// Display the first page on load
displayPage(currentPage);
