// Handling the appearing of the spinner while the page is loading.
const mainContent = document.querySelector('.main-content')
const pageReloadSpinner = document.getElementById('page-reload-loading-info')
window.addEventListener('beforeunload', function() {
    mainContent.style.display = 'none';
    pageReloadSpinner.style.display = 'flex';
})

// Handling the time range select
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.dropdown-item').forEach(function(item) {
        item.addEventListener('click', function(event) {
            event.preventDefault();
            var value = this.getAttribute('data-value');
            document.getElementById('time-range-input').value = value;
            document.getElementById('time-range-form').submit();
        });
    });
})

