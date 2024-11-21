document.addEventListener("DOMContentLoaded", () => {
  const table = document.querySelector(".logs-table");
  const rows = table.querySelectorAll("tbody tr");

  let previousTime = null;
  let group = [];
  
  // Function to parse the custom date format into a JavaScript Date object
  function parseCustomDate(dateStr) {
    const [datePart, timePart] = dateStr.split(", "); // Split into date and time
    const [day, month, year] = datePart.split("/").map(Number);
    const [hours, minutes, seconds] = timePart.split(":").map(Number);
    return new Date(year, month - 1, day, hours, minutes, seconds); // Create the Date object
  }

  rows.forEach((row, index) => {
    const timestampCell = row.getElementsByClassName('timestamp-cell')[0];
    if (!timestampCell) return; // Skip rows without the timestamp-cell
    
    const currentTime = timestampCell.textContent.trim();
    const currentDate = parseCustomDate(currentTime);

    if (previousTime) {
      const timeDifference = Math.abs(currentDate - previousTime) / 1000; // Time difference in seconds
      if (timeDifference > 0) { // New group if the difference exceeds 60 seconds
        console.log('cut')
	group[group.length - 1].style.borderBottom = "2px solid #999"; // Style last row of the group
        group = []; // Reset the group
      }
    }
    
    group.push(row); // Add current row to the group
    previousTime = currentDate; // Update the previous time

    // Apply the border to the last group after looping
    if (index === rows.length - 1 && group.length > 0) {
      group[group.length - 1].style.borderBottom = "2px solid #999";
    }
  });
});
