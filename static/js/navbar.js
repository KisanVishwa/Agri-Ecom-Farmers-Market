document.addEventListener('DOMContentLoaded', function() {
    const userMenuToggle = document.querySelector('.user-menu-toggle');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    if (userMenuToggle && dropdownMenu) {
        // Initialize aria-expanded
        userMenuToggle.setAttribute('aria-expanded', 'false');
        
        const toggleDropdown = (show) => {
            dropdownMenu.classList.toggle('show', show);
            userMenuToggle.setAttribute('aria-expanded', show ? 'true' : 'false');
        };

        userMenuToggle.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const isCurrentlyOpen = dropdownMenu.classList.contains('show');
            toggleDropdown(!isCurrentlyOpen);
        });

        // Close when clicking outside
        document.addEventListener('click', (e) => {
            if (!userMenuToggle.contains(e.target) && !dropdownMenu.contains(e.target)) {
                toggleDropdown(false);
            }
        });

        // Close on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && dropdownMenu.classList.contains('show')) {
                toggleDropdown(false);
            }
        });
    }
}); 