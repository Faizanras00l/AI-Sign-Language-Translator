// SOS App Interactions

document.addEventListener('DOMContentLoaded', () => {
    const sosButton = document.getElementById('sosTrigger');
    let pressTimer;

    // Simulate "Hold to call"
    const startPress = () => {
        sosButton.style.transform = 'scale(0.85)';
        pressTimer = setTimeout(() => {
            alert('Emergency call initiated!');
            sosButton.style.transform = 'scale(1)';
        }, 2000);
    };

    const endPress = () => {
        clearTimeout(pressTimer);
        sosButton.style.transform = 'scale(1)';
    };

    sosButton.addEventListener('mousedown', startPress);
    sosButton.addEventListener('mouseup', endPress);
    sosButton.addEventListener('mouseleave', endPress);

    // Touch events for mobile
    sosButton.addEventListener('touchstart', (e) => {
        e.preventDefault();
        startPress();
    });

    sosButton.addEventListener('touchend', endPress);

    // Scroll highlighting
    const sections = document.querySelectorAll('.section');
    const navItems = document.querySelectorAll('.nav-item');

    const observerOptions = {
        threshold: 0.6
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const id = entry.target.getAttribute('id');
                navItems.forEach(item => item.classList.remove('active'));

                // Map section ID to nav index
                if (id === 'sos-section') navItems[0].classList.add('active');
                if (id === 'place-section') navItems[1].classList.add('active');
                if (id === 'medical-section') navItems[2].classList.add('active');
                if (id === 'contacts-section') navItems[3].classList.add('active');
            }
        });
    }, observerOptions);

    sections.forEach(section => observer.observe(section));

    // Nav click scrolling
    navItems.forEach((item, index) => {
        item.addEventListener('click', () => {
            sections[index].scrollIntoView({ behavior: 'smooth' });
        });
    });
});
