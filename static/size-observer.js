// Add event listener for initial load and any dynamic updates
// Tạo một ResizeObserver
const observer = new ResizeObserver(entries => {
    for (const entry of entries) {
        // Khi kích thước của phần tử thay đổi
        const element = entry.target;

        // Tạo một sự kiện tùy chỉnh
        const lengthChangeEvent = new CustomEvent('lengthChange', {
            detail: {
                width: entry.contentRect.width,
                height: entry.contentRect.height
            }
        });

        // Gọi sự kiện trên phần tử
        element.dispatchEvent(lengthChangeEvent);
    }
});
