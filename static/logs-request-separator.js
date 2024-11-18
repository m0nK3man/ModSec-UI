document.addEventListener("DOMContentLoaded", () => {
  const table = document.querySelector(".logs-table");
  const rows = table.querySelectorAll("tbody tr");

  let previousTime = null;
  let group = [];

  rows.forEach((row, index) => {
    const currentTime = row.cells[0].textContent.trim(); // Assumes timestamp is in the first cell
    const currentDate = new Date(currentTime);

    if (previousTime) {
      const previousDate = new Date(previousTime);
      const timeDifference = Math.abs(currentDate - previousDate) / 1000; // Time difference in seconds
      if (timeDifference > 0) { // New group if the difference exceeds 60 seconds
        group[group.length - 1].style.borderBottom = "2px solid #999"; // Apply style to last row of the group
        group = [];
      }
    }

    group.push(row);
    previousTime = currentTime;

    // Apply to the last group after looping
    if (index === rows.length - 1) {
      group[group.length - 1].style.borderBottom = "2px solid #999";
    }
  });
});
