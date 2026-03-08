document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.querySelector('.start-btn');
    const arrowBtn = document.querySelector('.arrow-btn');
    const authOverlay = document.getElementById('auth-overlay');
    const closeAuthBtn = document.getElementById('close-auth');
    const goToSignup = document.getElementById('go-to-signup');
    const goToLogin = document.getElementById('go-to-login');
    const loginView = document.getElementById('login-view');
    const signupView = document.getElementById('signup-view');

    // Show Auth Overlay
    const showAuth = () => {
        authOverlay.classList.add('active');
        document.body.style.overflow = 'hidden'; // Prevent scrolling
    };

    // Hide Auth Overlay
    const hideAuth = () => {
        authOverlay.classList.remove('active');
        document.body.style.overflow = ''; // Restore scrolling
    };

    // Switch between Login and Signup
    const toggleAuthView = (showSignup) => {
        if (showSignup) {
            loginView.classList.remove('active');
            signupView.classList.add('active');
        } else {
            signupView.classList.remove('active');
            loginView.classList.add('active');
        }
    };

    // Event Listeners
    if (startBtn) startBtn.addEventListener('click', showAuth);
    if (arrowBtn) arrowBtn.addEventListener('click', showAuth);
    if (closeAuthBtn) closeAuthBtn.addEventListener('click', hideAuth);

    if (goToSignup) {
        goToSignup.addEventListener('click', (e) => {
            e.preventDefault();
            toggleAuthView(true);
        });
    }

    if (goToLogin) {
        goToLogin.addEventListener('click', (e) => {
            e.preventDefault();
            toggleAuthView(false);
        });
    }

    // Close on overlay click
    authOverlay.addEventListener('click', (e) => {
        if (e.target === authOverlay) {
            hideAuth();
        }
    });

    // Form Submissions (Demo)
    const forms = document.querySelectorAll('.auth-form');
    forms.forEach(form => {
        form.addEventListener('submit', (e) => {
            e.preventDefault();
            const btn = form.querySelector('.submit-btn');
            const originalText = btn.textContent;

            btn.disabled = true;
            btn.textContent = 'Processing...';

            setTimeout(() => {
                btn.textContent = 'Success!';
                btn.style.background = '#10B981';

                setTimeout(() => {
                    hideAuth();
                    btn.disabled = false;
                    btn.textContent = originalText;
                    btn.style.background = '';
                    window.location.href = 'home.html';
                }, 1000);
            }, 1500);
        });
    });
});
