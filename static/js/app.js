/* SOS App interactions and common navigation */

document.addEventListener('DOMContentLoaded', () => {
    // --- USER DATA & PROFILE LOGIC ---
    // Elements
    const panelNameInput = document.getElementById('panel-name-input');
    const panelAvatarPreview = document.getElementById('panel-avatar-preview');
    const headerName = document.getElementById('user-display-name');
    const headerImg = document.getElementById('header-profile-img');
    const profilePanel = document.getElementById('profile-panel');
    const notifToggle = document.getElementById('notif-toggle');
    const langSelect = document.getElementById('lang-select');

    // Load User Data
    let user = JSON.parse(localStorage.getItem('wlasUser')) || {
        name: 'Barry',
        plan: 'Basic',
        avatarSeed: 'Barry',
        avatarUrl: null, // For custom uploads
        notifications: true,
        language: 'en'
    };

    function updateProfileUI() {
        // Safe updates if elements exist
        if (headerName) headerName.textContent = `Hey, ${user.name} 👋`;

        // Avatar Logic: Prefer Custom URL, else Dicebear
        const avatarSrc = user.avatarUrl || `https://api.dicebear.com/7.x/avataaars/svg?seed=${user.avatarSeed}`;

        if (headerImg) headerImg.src = avatarSrc;
        if (panelAvatarPreview) panelAvatarPreview.src = avatarSrc;
        if (panelNameInput) panelNameInput.value = user.name;

        // Settings
        if (notifToggle) notifToggle.checked = user.notifications;
        if (langSelect) langSelect.value = user.language;

        // Plan Selection UI
        document.querySelectorAll('.plan-option').forEach(opt => {
            opt.classList.remove('selected');
        });
        const activePlanEl = document.getElementById(`plan-${user.plan.toLowerCase()}`);
        if (activePlanEl) activePlanEl.classList.add('selected');
    }

    updateProfileUI();

    // Profile Panel Actions
    window.openProfilePanel = () => {
        if (profilePanel) {
            profilePanel.style.display = 'flex';
            // Force reflow
            profilePanel.offsetHeight;
            profilePanel.classList.add('active');
            updateProfileUI(); // Ensure fresh data
        }
    };

    window.closeProfilePanel = () => {
        if (profilePanel) {
            profilePanel.classList.remove('active');
            setTimeout(() => {
                profilePanel.style.display = 'none';
            }, 300); // Match transition duration
        }
    };

    window.saveProfilePanel = () => {
        const newName = panelNameInput.value.trim();
        if (newName) {
            user.name = newName;
            // Only update seed if no custom url, or just let custom url persist.
            if (!user.avatarUrl) user.avatarSeed = newName;

            user.notifications = notifToggle.checked;
            user.language = langSelect.value;

            localStorage.setItem('wlasUser', JSON.stringify(user));
            updateProfileUI();
            closeProfilePanel();

            // Success Feedback
            // Could use a toast, but standard alert for now
            alert('Profile saved successfully!');
        }
    };

    window.handleAvatarUpload = (input) => {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            reader.onload = (e) => {
                user.avatarUrl = e.target.result; // Save as Data URL
                if (panelAvatarPreview) panelAvatarPreview.src = user.avatarUrl;
            };
            reader.readAsDataURL(input.files[0]);
        }
    };

    // Plan Data
    const PLANS_DATA = {
        'Basic': {
            features: [
                { name: "Core Translations", active: true },
                { name: "5 Daily Scans", active: true },
                { name: "Offline Mode", active: false },
                { name: "Human Assistant", active: false }
            ]
        },
        'Premium': {
            features: [
                { name: "Unlimited Translations", active: true },
                { name: "Unlimited Scans", active: true },
                { name: "Offline Mode", active: true },
                { name: "Human Assistant", active: false }
            ]
        },
        'Ultra': {
            features: [
                { name: "Everything in Premium", active: true },
                { name: "Priority Support", active: true },
                { name: "Offline Mode", active: true },
                { name: "24/7 Live Human Assist", active: true }
            ]
        }
    };

    function renderPlanDetails(planName) {
        const container = document.getElementById('selected-plan-details');
        const plan = PLANS_DATA[planName] || PLANS_DATA['Basic'];

        if (!container) return;

        let html = `<ul class="plan-perks-list">`;
        plan.features.forEach(feat => {
            const statusClass = feat.active ? 'active' : 'locked';
            const icon = feat.active ? 'check' : 'lock';
            html += `
                <li class="plan-perk-item ${statusClass}">
                    <div class="perk-icon"><i class="material-icons-round" style="font-size: 14px;">${icon}</i></div>
                    <span>${feat.name}</span>
                </li>
            `;
        });
        html += `</ul>`;

        container.innerHTML = html;
    }

    // Call this on init to show current plan details
    const initPlan = user.plan || 'Basic';
    renderPlanDetails(initPlan);

    window.selectPanelPlan = (planName) => {
        user.plan = planName;
        // Update visual state immediately
        document.querySelectorAll('.plan-option').forEach(opt => opt.classList.remove('selected'));
        const activePlanEl = document.getElementById(`plan-${planName.toLowerCase()}`);
        if (activePlanEl) activePlanEl.classList.add('selected');

        // Render details
        renderPlanDetails(planName);
    }

    window.resetAppProgress = () => {
        if (confirm("Are you sure? This will delete all course progress. This cannot be undone.")) {
            // Clear course data but keep user profile
            localStorage.removeItem('aslEnrolledCourses');
            alert("Progress reset.");
            location.reload();
        }
    };

    window.logoutUser = () => {
        if (confirm('Are you sure you want to log out?')) {
            alert('Logged out.');
            // Reset or redirect logic here
            localStorage.removeItem('wlasUser');
            location.reload();
        }
    }


    // --- ENROLLED COURSES LOGIC ---
    const learningSection = document.getElementById('learning-section');
    if (learningSection) {
        const enrolledIds = JSON.parse(localStorage.getItem('aslEnrolledCourses')) || [];
        // Helper mapping for titles (simplified version of Education Data)
        // In a real app, this data would be shared more robustly.
        const COURSE_TITLES = {
            1: "ASL Level 1: The Basics",
            2: "Daily Conversations",
            3: "Deaf Culture & Community",
            4: "Mastering Fingerspelling",
            5: "Baby Sign Language 101"
            // Add more as needed or fetch from a shared source
        };

        if (enrolledIds.length > 0) {
            learningSection.innerHTML = `
                <div class="section-header">
                    <h3>My Learning</h3>
                    <span class="see-all" onclick="location.href='education.html'">Go to Classroom</span>
                </div>
            `;

            // Show top 2 recent courses
            enrolledIds.slice(-2).reverse().forEach(id => {
                const title = COURSE_TITLES[id] || `Course #${id}`;
                const progress = Math.floor(Math.random() * 80) + 10; // Mock progress

                learningSection.innerHTML += `
                    <div class="learning-card" onclick="location.href='education.html'">
                        <div class="learning-icon">
                            <i class="material-icons-round" style="font-size: 28px;">school</i>
                        </div>
                        <div class="learning-info">
                            <h4>${title}</h4>
                            <p style="font-size: 12px; color: #64748B;">In Progress • ${progress}%</p>
                            <div class="progress-container">
                                <div class="progress-bar" style="width: ${progress}%;"></div>
                            </div>
                        </div>
                        <i class="material-icons-round" style="color: #CBD5E1;">chevron_right</i>
                    </div>
                `;
            });
        } else {
            // Fallback default state
            learningSection.innerHTML = `
                <div class="section-header">
                    <h3>Start Learning</h3>
                </div>
                <div class="learning-card" onclick="location.href='education.html'">
                    <div class="learning-icon">
                        <i class="material-icons-round" style="font-size: 34px;">school</i>
                    </div>
                    <div class="learning-info">
                        <h4>ASL Fundamentals</h4>
                        <p style="font-size: 13px; color: #64748B;">Start your first course today!</p>
                    </div>
                    <i class="material-icons-round" style="color: #CBD5E1;">chevron_right</i>
                </div>
            `;
        }
    }


    // --- ANIMATIONS & EXISTING LOGIC ---
    // Staggered Entrance Animations for Catalog (Home) Page
    const homeContainer = document.querySelector('.home-container');
    if (homeContainer) {
        const animateElements = () => {
            const elements = [
                document.querySelector('.home-header'),
                document.querySelector('.hero-search'),
                ...document.querySelectorAll('.section-header'),
                ...document.querySelectorAll('.feature-card'), // This includes ALL feature cards, including SOS if it has this class
                ...document.querySelectorAll('.learning-card'),
                document.querySelector('.floating-nav')
            ];

            // Debug/Safety: Ensure sos card is picked up
            // The previous code used .feature-card which acts on all of them. 
            // If .card-sos has .feature-card class (which it does in html), it should work.
            // Let's verify if there is an issue with the selector or layout.
            // In the HTML view: <div class="feature-card card-sos" ...>
            // It should be picked up by querySelectorAll('.feature-card').
            // Converting to array to debug or ensure order? 
            // The user says "except the SOS help". 
            // Maybe it's the last one and the delay is too long? Or CSS issue?
            // Actually, let's just make sure the loop applies correctly.

            elements.forEach((el, index) => {
                if (el) {
                    el.style.animationDelay = `${index * 0.1}s`;
                    el.classList.add('animate-in');
                }
            });
        };

        animateElements();
    }

    // Interactive Hover & Ripple Effects (Optional but premium)
    const interactiveElements = document.querySelectorAll('.feature-card, .learning-card, .search-arrow-btn, .icon-btn-circle');
    interactiveElements.forEach(el => {
        el.addEventListener('touchstart', () => {
            el.style.transform = 'scale(0.95)';
        });
        el.addEventListener('touchend', () => {
            el.style.transform = '';
        });
    });

    // --- NEW: Global Loading Screen Logic (Refined) ---
    window.navigateToTranslate = (targetUrl) => {
        // 1. Skip loading screen entirely for Chatbot (Page 4) as requested
        if (targetUrl && targetUrl.includes('page4.html')) {
            window.location.href = targetUrl;
            return;
        }

        // Determine type based on URL
        // Page 2 = Sign to Text (Vision)
        // Page 3 = Text to Sign (Avatar)
        let type = 'vision'; // Default
        if (targetUrl.includes('page3.html')) {
            type = 'avatar';
        }

        injectLoadingOverlay(type);

        const overlay = document.getElementById('loading-overlay');

        if (overlay) {
            // Force reflow
            overlay.offsetHeight;
            overlay.classList.add('active');

            // Minimal wait time (5-6s delay requested previously, user said "add a loading screen", implies delay is still wanted but purely visual)
            setTimeout(() => {
                window.location.href = targetUrl;
            }, 4500);
        } else {
            window.location.href = targetUrl;
        }
    };

    function injectLoadingOverlay(type) {
        // Remove existing if any (to support switch types)
        const existing = document.getElementById('loading-overlay');
        if (existing) existing.remove();

        let innerContent = '';

        if (type === 'vision') {
            // Sign-to-Text: Scanning Ring
            innerContent = `
                <div class="loader-vision-ring"></div>
                <div class="loader-vision-scanline" style="position:absolute;"></div>
            `;
        } else {
            // Text-to-Sign: Morphing Orb
            innerContent = `
                <div class="loader-avatar-orb"></div>
            `;
        }

        const overlayHtml = `
            <div id="loading-overlay" class="loading-overlay">
                <div class="loader-content">
                    ${innerContent}
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', overlayHtml);
    }

    // Auto-inject styles for loading if needed, or rely on profile-style.css handling it globally
    // We should probably ensure profile-style.css is loaded or these styles are global.
    // For safety, let's check if profile-style is loaded, if not add it dynamically?
    // actually, best to add it to style.css for global access.

    // --- NEW: Profile Page Specific Logic ---
    window.initProfilePage = () => {
        // Re-run UI update in case we are on profile.html
        updateProfileUI();

        const planCards = document.querySelectorAll('.plan-card');
        planCards.forEach(card => {
            card.addEventListener('click', () => {
                // Visual selection handling
                const planId = card.id.replace('plan-', '');
                // Capitalize
                const planName = planId.charAt(0).toUpperCase() + planId.slice(1);
                selectProfilePlan(planName);
            });
        });
    };

    // If we are on profile.html, init immediately
    if (window.location.pathname.includes('profile.html')) {
        window.initProfilePage();
    }
});

// Helper for Profile Page
window.selectProfilePlan = (planName) => {
    // Re-use logic from app.js but adapted for direct calls
    // Update USER object
    let user = JSON.parse(localStorage.getItem('wlasUser')) || {};
    user.plan = planName;
    localStorage.setItem('wlasUser', JSON.stringify(user));

    // Visual update
    document.querySelectorAll('.plan-card').forEach(c => c.classList.remove('selected'));
    const activeCard = document.getElementById(`plan-${planName.toLowerCase()}`);
    if (activeCard) activeCard.classList.add('selected');

    // Update Details
    // We need to define renderPlanDetails globally or attach to window
    // (It was defined inside DOMContentLoaded scope previously, need to be careful)
    // The previous implementation had it inside. I should refactor or duplicate for safety.
    // For now, let's reload the page to apply changes cleanly or define a renderer here.

    const detailsBox = document.getElementById('active-plan-details');
    if (detailsBox) {
        // Simple internal renderer
        const PLANS_DATA_GLOBAL = {
            'Basic': [{ name: "Core Translations", a: true }, { name: "5 Daily Scans", a: true }, { name: "Offline Mode", a: false }],
            'Premium': [{ name: "Unlimited Translations", a: true }, { name: "Unlimited Scans", a: true }, { name: "Offline Mode", a: true }],
            'Ultra': [{ name: "Everything in Premium", a: true }, { name: "Priority Support", a: true }, { name: "24/7 Human Assist", a: true }]
        };
        const feats = PLANS_DATA_GLOBAL[planName] || PLANS_DATA_GLOBAL['Basic'];
        let html = `<ul class="plan-perks-list" style="list-style:none; padding:0;">`;
        feats.forEach(f => {
            const icon = f.a ? 'check_circle' : 'lock';
            const color = f.a ? 'var(--primary-color)' : '#ccc';
            html += `<li style="display:flex; align-items:center; gap:8px; margin-bottom:6px; color:${f.a ? '#333' : '#999'}">
                <i class="material-icons-round" style="font-size:16px; color:${color}">${icon}</i> ${f.name}
            </li>`;
        });
        html += `</ul>`;
        detailsBox.innerHTML = html;
    }
};

window.saveProfileName = () => {
    const input = document.getElementById('profile-name-input');
    if (input) {
        let user = JSON.parse(localStorage.getItem('wlasUser'));
        user.name = input.value;
        localStorage.setItem('wlasUser', JSON.stringify(user));
    }
};

window.saveSettings = () => {
    let user = JSON.parse(localStorage.getItem('wlasUser'));
    const notif = document.getElementById('notif-toggle');
    const lang = document.getElementById('lang-select');

    if (notif) user.notifications = notif.checked;
    if (lang) user.language = lang.value;

    localStorage.setItem('wlasUser', JSON.stringify(user));
};
