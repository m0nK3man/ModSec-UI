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
            const formatDateTimeLocal = (date) => date.toISOString().slice(0, 16);

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
