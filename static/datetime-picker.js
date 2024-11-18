document.addEventListener('DOMContentLoaded', function () {
    const timeRange = document.getElementById('time_range');
    const startTimeInput = document.getElementById('start_time');
    const endTimeInput = document.getElementById('end_time');

    timeRange.addEventListener('change', function () {
        const now = new Date();
        const selectedRange = timeRange.value;

        if (selectedRange !== 'custom') {
            let startTime;

            switch (selectedRange) {
                case '15m':
                    startTime = new Date(now.getTime() - 15 * 60 * 1000); // 15 minutes ago
                    break;
                case '1h':
                    startTime = new Date(now.getTime() - 60 * 60 * 1000); // 1 hour ago
                    break;
                case '6h':
                    startTime = new Date(now.getTime() - 6 * 60 * 60 * 1000); // 6 hours ago
                    break;
                case '1d':
                    startTime = new Date(now.getTime() - 24 * 60 * 60 * 1000); // 24 hours ago
                    break;
                default:
                    return;
            }

            // Format datetime-local inputs
            const formatDateTimeLocal = (date) => {
                const year = date.getFullYear();
                const month = String(date.getMonth() + 1).padStart(2, '0');
                const day = String(date.getDate()).padStart(2, '0');
                const hours = String(date.getHours()).padStart(2, '0');
                const minutes = String(date.getMinutes()).padStart(2, '0');

                return `${year}-${month}-${day}T${hours}:${minutes}`;
            };
            startTimeInput.value = formatDateTimeLocal(startTime);
            endTimeInput.value = formatDateTimeLocal(now);
        }
    });

    // Remove `time_range` from form submission
    const form = document.querySelector('.filter-form');

    // Initialize time range if it's not custom
    if (timeRange.value !== 'custom') {
        timeRange.dispatchEvent(new Event('change'));
    }
});
