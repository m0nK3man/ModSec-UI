// Function to format the timestamp to UTC+7
function formatTimestampToUTC7() {
    // Select all elements with the class "timestamp-cell"
    const timestampCells = document.querySelectorAll('.timestamp-cell');

    timestampCells.forEach(cell => {
        const originalTimestamp = cell.textContent.trim(); // Get the timestamp
        const date = new Date(originalTimestamp); // Parse the timestamp

        // Adjust to UTC+7
        const options = { timeZone: 'Asia/Ho_Chi_Minh', hour12: false };
        const formatter = new Intl.DateTimeFormat('en-UK', {
            ...options,
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        });

        const formattedDate = formatter.format(date);
        cell.textContent = formattedDate; // Update the cell with the formatted timestamp
    });
}

// Call the function to format timestamps
formatTimestampToUTC7();

