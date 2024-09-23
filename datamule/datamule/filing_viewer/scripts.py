script1 = """
document.addEventListener('DOMContentLoaded', function () {
    const sections = document.querySelectorAll('section');
    const navLinks = document.querySelectorAll('.sidebar a');
    const sidebar = document.querySelector('.sidebar');

    function makeActive(link) {
        navLinks.forEach(n => n.classList.remove('active'));
        link.classList.add('active');
    }

    function findActiveSection() {
        let currentSection = '';
        sections.forEach(section => {
            const sectionTop = section.offsetTop;
            const sectionHeight = section.clientHeight;
            if (pageYOffset >= sectionTop - window.innerHeight / 2) {
                currentSection = section.getAttribute('id');
            }
        });
        return currentSection;
    }

    function updateSidebar() {
        const currentSection = findActiveSection();
        navLinks.forEach(link => {
            if (link.getAttribute('href').substring(1) === currentSection) {
                makeActive(link);
                // Center the active link in the sidebar
                const linkRect = link.getBoundingClientRect();
                const sidebarRect = sidebar.getBoundingClientRect();
                const targetScrollTop = link.offsetTop - sidebar.offsetTop - (sidebarRect.height / 2) + (linkRect.height / 2);
                sidebar.scrollTop = targetScrollTop;
            }
        });
    }

    window.addEventListener('scroll', updateSidebar);
    updateSidebar(); // Call once to set initial state
});"""