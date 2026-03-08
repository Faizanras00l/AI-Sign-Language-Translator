document.addEventListener('DOMContentLoaded', () => {
    lucide.createIcons();

    // --- DATA ---
    const ASL_COURSES = {
        1: {
            id: 1, title: "ASL Level 1: The Basics", instructor: "Sarah J.", category: "ASL Basics", rating: 4.9, img: "https://images.unsplash.com/photo-1456513080510-7bf3a84b82f8?q=80&w=600", desc: "Perfect for absolute beginners. Learn the alphabet, basic numbers, and everyday greetings.", lessons: 12, modules: [
                { title: "Introduction to ASL", duration: "15 min", desc: "History and linguistic foundations." },
                { title: "The Alpha-Numeric System", duration: "45 min", desc: "Letters A-Z and numbers 1-100." }
            ]
        },
        2: { id: 2, title: "Daily Conversations", instructor: "Mark T.", category: "ASL Basics", rating: 4.8, img: "https://images.unsplash.com/photo-1577896851231-70ef14603e80?q=80&w=600", desc: "Bridge the gap between vocabulary and fluid conversation.", lessons: 15, modules: [] },
        3: { id: 3, title: "Deaf Culture & Community", instructor: "Alice R.", category: "Deaf Culture", rating: 5.0, img: "https://images.unsplash.com/photo-1544650030-3c9baf624244?q=80&w=600", desc: "Understanding the rich history and social dynamics.", lessons: 8, modules: [] },
        4: { id: 4, title: "Mastering Fingerspelling", instructor: "Robert K.", category: "Fingerspelling", rating: 4.7, img: "https://images.unsplash.com/photo-1509062522246-3755977927d7?q=80&w=600", desc: "Drill your receptive and expressive skills.", lessons: 10, modules: [] },
        5: { id: 5, title: "Baby Sign Language 101", instructor: "Emma L.", category: "ASL Basics", rating: 4.9, img: "https://images.unsplash.com/photo-1596495573175-97affa20f7f3?q=80&w=600", desc: "Communicate with your little ones.", lessons: 12, modules: [] },
        6: { id: 6, title: "ASL for Workplace", instructor: "Kevin M.", category: "Interpreting", rating: 4.6, img: "https://images.unsplash.com/photo-1491336477066-31156b5e4f35?q=80&w=600", desc: "Industry-specific vocabulary.", lessons: 14, modules: [] },
        7: { id: 7, title: "Medical Interpreting", instructor: "Leo G.", category: "Interpreting", rating: 4.7, img: "https://images.unsplash.com/photo-1516533075015-a3838414c3ca?q=80&w=600", desc: "Clinical settings focus.", lessons: 18, modules: [] },
        8: { id: 8, title: "ASL Classifiers Mastery", instructor: "Diana P.", category: "ASL Basics", rating: 5.0, img: "https://images.unsplash.com/photo-1524178232363-1fb2b075b655?q=80&w=600", desc: "Advanced size and shape specifiers.", lessons: 20, modules: [] },
        9: { id: 9, title: "Sign Language for Kids", instructor: "Mia B.", category: "ASL Basics", rating: 4.9, img: "https://images.unsplash.com/photo-1543269664-56d93c1b41a6?q=80&w=600", desc: "Fun learning for children.", lessons: 15, modules: [] },
        10: { id: 10, title: "Art of Signed Poetry", instructor: "Chris H.", category: "Deaf Culture", rating: 5.0, img: "https://images.unsplash.com/photo-1492684223066-81342ee5ff30?q=80&w=600", desc: "Explore creative ASL.", lessons: 10, modules: [] },
        11: { id: 11, title: "Legal Interpreting", instructor: "Kevin M.", category: "Interpreting", rating: 4.8, img: "https://images.unsplash.com/photo-1505664194779-8beaceb93744?q=80&w=600", desc: "Courtroom ASL foundations.", lessons: 16, modules: [] },
        12: { id: 12, title: "ASL Level 2", instructor: "Sarah J.", category: "ASL Basics", rating: 4.7, img: "https://images.unsplash.com/photo-1516321497487-e288fb19713f?q=80&w=600", desc: "Intermediate grammatical structures.", lessons: 14, modules: [] },
        13: { id: 13, title: "Visual Storytelling", instructor: "Alice R.", category: "Deaf Culture", rating: 4.9, img: "https://images.unsplash.com/photo-1485846234645-a62644f84728?q=80&w=600", desc: "The art of ASL narratives.", lessons: 8, modules: [] },
        14: { id: 14, title: "Quick Fingerspelling", instructor: "Robert K.", category: "Fingerspelling", rating: 4.5, img: "https://images.unsplash.com/photo-1546410531-bb4caa6b424d?q=80&w=600", desc: "Receptive speed drills.", lessons: 12, modules: [] },
        15: { id: 15, title: "ASL Grammar Dive", instructor: "Diana P.", category: "ASL Basics", rating: 4.8, img: "https://images.unsplash.com/photo-1503676260728-1c00da094a0b?q=80&w=600", desc: "Non-manual markers focus.", lessons: 10, modules: [] }
    };

    const SCHOOLS_DATA = {
        1: {
            id: 1,
            name: "Gallaudet University",
            logo: "https://api.dicebear.com/7.x/initials/svg?seed=GU",
            location: "Washington, D.C.",
            about: "Gallaudet University is a federally chartered private university for the education of the deaf and hard of hearing. It was the first school for the advanced education of the deaf and hard of hearing in the world and remains the only higher education institution in which all programs and services are specifically designed to accommodate deaf and hard of hearing students.",
            hero: "https://images.unsplash.com/photo-1562774053-701939374585?q=80&w=1200",
            programs: [
                { name: "BA in ASL & Deaf Studies", degree: "Undergraduate" },
                { name: "MA in Interpretation", degree: "Graduate" },
                { name: "Doctor of Philosophy in Deaf Ed.", degree: "Doctoral" }
            ]
        },
        2: {
            id: 2,
            name: "RIT / NTID",
            logo: "https://api.dicebear.com/7.x/initials/svg?seed=NTID",
            location: "Rochester, NY",
            about: "The National Technical Institute for the Deaf (NTID) is the first and largest technological college in the world for students who are deaf or hard of hearing. NTID is one of nine colleges of the Rochester Institute of Technology (RIT), a privately endowed university.",
            hero: "https://images.unsplash.com/photo-1517048676732-d65bc937f952?q=80&w=1200",
            programs: [
                { name: "ASL-English Interpretation BS", degree: "Undergraduate" },
                { name: "Applied Arts & Sciences", degree: "Diploma/AAS" },
                { name: "MS in Secondary Education", degree: "Graduate" }
            ]
        },
        3: {
            id: 3,
            name: "CSU Northridge",
            logo: "https://api.dicebear.com/7.x/initials/svg?seed=CSUN",
            location: "Northridge, CA",
            about: "California State University, Northridge (CSUN) is home to the National Center on Deafness (NCOD). Since 1964, NCOD has provided communication access, academic advisement, and tutoring for more than 2,500 deaf and hard-of-hearing students.",
            hero: "https://images.unsplash.com/photo-1541339907198-e08756ebafe1?q=80&w=1200",
            programs: [
                { name: "Deaf Studies Department", degree: "Undergraduate" },
                { name: "Pre-Interpreting Program", degree: "Pathway" },
                { name: "Special Education Credential", degree: "Certificate" }
            ]
        },
        4: {
            id: 4,
            name: "Northeastern University",
            logo: "https://api.dicebear.com/7.x/initials/svg?seed=NEU",
            location: "Boston, MA",
            about: "Northeastern's American Sign Language (ASL) Program offers a major and a minor in ASL and a combined major in Human Services and ASL. The program focuses on linguistic fluency and cultural competence.",
            hero: "https://images.unsplash.com/photo-1574169208507-84376144848b?q=80&w=1200",
            programs: [
                { name: "ASL & Human Services BS", degree: "Undergraduate" },
                { name: "Linguistics of ASL", degree: "Minor" },
                { name: "Interpreting Concentration", degree: "Specialty" }
            ]
        },
        5: {
            id: 5,
            name: "University of Pennsylvania",
            logo: "https://api.dicebear.com/7.x/initials/svg?seed=UPenn",
            location: "Philadelphia, PA",
            about: "UPenn offers comprehensive ASL courses through its ASL Program. The curriculum is designed to teach students sign language and the sociology of the Deaf community, with a strong emphasis on community engagement.",
            hero: "https://images.unsplash.com/photo-1506784911077-50972ad5f40c?q=80&w=1200",
            programs: [
                { name: "ASL Language Studies", degree: "Undergraduate" },
                { name: "Deaf Culture Research", degree: "Graduate" },
                { name: "Community Service Learning", degree: "Elective" }
            ]
        }
    };

    // --- STATE ---
    let likedCourses = JSON.parse(localStorage.getItem('aslLikedCourses')) || [];
    let enrolledCourses = JSON.parse(localStorage.getItem('aslEnrolledCourses')) || [];
    let activeCourseId = null;

    // --- NAVIGATION ---
    window.navigateTo = (screenId) => {
        document.querySelectorAll('.screen').forEach(s => s.classList.remove('active'));
        const target = document.getElementById(screenId);
        if (target) {
            target.classList.add('active');
            target.scrollTo(0, 0);
        }

        // Navigation Highlight
        document.querySelectorAll('.nav-item').forEach(item => {
            item.classList.remove('active');
            if (screenId === 'home-screen' && item.classList.contains('home-nav')) item.classList.add('active');
            if (screenId === 'my-courses-screen' && item.classList.contains('courses-nav')) item.classList.add('active');
            if (screenId === 'favorites-screen' && item.classList.contains('favorites-nav')) item.classList.add('active');
        });

        if (screenId === 'favorites-screen') updateFavoritesUI();
        if (screenId === 'my-courses-screen') updateMyCoursesUI();
    };

    // --- COURSE DETAILS ---
    window.showCourseDetails = (id) => {
        const course = ASL_COURSES[id];
        if (!course) return;
        activeCourseId = id;

        document.getElementById('detail-title').textContent = course.title;
        document.getElementById('detail-instructor').textContent = `Instructor: ${course.instructor}`;
        document.getElementById('detail-lessons-count').innerHTML = `${course.lessons}<br><span style="font-size:11px; font-weight:500; opacity:0.8;">Lessons</span>`;
        document.getElementById('detail-hero-image').src = course.img;
        document.getElementById('detail-description').textContent = course.desc;

        const modulesList = document.getElementById('detail-modules-list');
        modulesList.innerHTML = '<h3 style="margin-bottom: 20px; font-weight: 800;">Curriculum</h3>';

        course.modules.forEach((mod, i) => {
            modulesList.innerHTML += `
                <div class="lesson-item locked">
                    <div class="status-icon"><i data-lucide="lock" style="width: 20px;"></i></div>
                    <div class="lesson-info">
                        <h4>Module ${i + 1}</h4>
                        <h3>${mod.title}</h3>
                        <div class="lesson-meta">
                            <span class="lesson-meta-item">
                                <i data-lucide="clock" style="width:14px; color:#B0B0C4;"></i> ${mod.duration}
                            </span>
                            <span class="lesson-meta-item">
                                <i data-lucide="info" style="width:14px; color:#B0B0C4;"></i> ${mod.desc}
                            </span>
                        </div>
                    </div>
                </div>
            `;
        });

        const enrollBtn = document.getElementById('enroll-btn');
        if (enrolledCourses.includes(id)) {
            enrollBtn.textContent = 'Already Enrolled';
            enrollBtn.classList.add('enrolled');
            enrollBtn.onclick = null;
        } else {
            enrollBtn.textContent = 'Enroll in Course';
            enrollBtn.classList.remove('enrolled');
            enrollBtn.onclick = () => enrollInCourse(id);
        }

        navigateTo('course-details-screen');
        lucide.createIcons();
    };

    // --- ENROLLMENT ---
    window.enrollInCourse = (id = activeCourseId) => {
        if (!id || enrolledCourses.includes(id)) return;

        enrolledCourses.push(id);
        localStorage.setItem('aslEnrolledCourses', JSON.stringify(enrolledCourses));

        const btn = document.getElementById('enroll-btn');
        btn.textContent = 'Processing...';
        setTimeout(() => {
            btn.textContent = 'Ready to Start!';
            btn.classList.add('enrolled');
            btn.onclick = null;
        }, 800);
    };

    // --- SCHOOL DETAILS ---
    window.showSchoolDetails = (id) => {
        const school = SCHOOLS_DATA[id];
        if (!school) return;

        document.getElementById('school-detail-logo').src = school.logo;
        document.getElementById('school-detail-hero').src = school.hero;
        document.getElementById('school-detail-name').textContent = school.name;
        document.getElementById('school-detail-location').innerHTML = `<i data-lucide="map-pin" style="width:14px; vertical-align: middle;"></i> ${school.location}`;
        document.getElementById('school-detail-about').textContent = school.about;

        const programsList = document.getElementById('school-programs-list');
        programsList.innerHTML = '';
        school.programs.forEach(prog => {
            // Create a safe class name from degree type (e.g., "Diploma/AAS" -> "diploma-aas")
            const badgeClass = prog.degree.toLowerCase().replace(/[^a-z0-9]/g, '-');

            programsList.innerHTML += `
                <div class="program-item">
                    <div class="program-content">
                        <h4>${prog.name}</h4>
                        <p>Specialized Accreditation Available</p>
                    </div>
                    <span class="badge ${badgeClass}">${prog.degree}</span>
                </div>
            `;
        });

        navigateTo('school-details-screen');
        lucide.createIcons();
    };

    // --- FAVORITES LOGIC ---
    window.toggleLike = (event, id) => {
        event.stopPropagation();
        const index = likedCourses.indexOf(id);
        if (index === -1) likedCourses.push(id);
        else likedCourses.splice(index, 1);

        localStorage.setItem('aslLikedCourses', JSON.stringify(likedCourses));
        updateLikeButtons();
    };

    function updateLikeButtons() {
        document.querySelectorAll('.course-card-premium').forEach(card => {
            const id = parseInt(card.dataset.id);
            const btn = card.querySelector('.like-btn');
            if (btn) {
                if (likedCourses.includes(id)) {
                    btn.classList.add('active');
                    btn.innerHTML = '<i data-lucide="heart" style="fill: currentColor;"></i>';
                } else {
                    btn.classList.remove('active');
                    btn.innerHTML = '<i data-lucide="heart"></i>';
                }
            }
        });
        lucide.createIcons();
    }

    function updateFavoritesUI() {
        const container = document.getElementById('favorites-list');
        if (likedCourses.length === 0) {
            container.innerHTML = `<div class="empty-state" style="text-align: center; padding: 60px 10px;">
                <i data-lucide="heart" style="width:50px; height:50px; color:#E0E0E0; margin-bottom:16px;"></i>
                <p style="color: var(--text-muted); font-size:14px;">No favorites yet.</p>
            </div>`;
            return;
        }

        container.innerHTML = '';
        likedCourses.forEach(id => {
            const course = ASL_COURSES[id];
            if (!course) return;
            const cardMarkup = `
                <div class="course-card-premium" style="flex: 1 1 100%; margin-bottom:16px;" onclick="showCourseDetails(${id})">
                    <div class="card-image-box" style="height:140px;">
                        <img src="${course.img}" style="width:100%; height:100%; object-fit:cover;">
                        <button class="like-btn active" onclick="toggleLike(event, ${id})">
                            <i data-lucide="heart" style="fill: currentColor;"></i>
                        </button>
                    </div>
                    <p class="card-category">${course.category}</p>
                    <h3>${course.title}</h3>
                    <div class="card-footer">
                         <div class="instructor-info">
                            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=${course.instructor}" class="instructor-avatar">
                            <span class="instructor-name">${course.instructor}</span>
                        </div>
                        <div class="rating"><i data-lucide="star" style="width:12px; fill:#FFD700; color:#FFD700;"></i> ${course.rating}</div>
                    </div>
                </div>
            `;
            container.innerHTML += cardMarkup;
        });
        lucide.createIcons();
    }

    // --- MY COURSES UI ---
    function updateMyCoursesUI() {
        const container = document.querySelector('.courses-list');
        const progressVal = document.querySelector('.value-container');

        if (enrolledCourses.length === 0) {
            container.innerHTML = '<div style="text-align:center; padding: 40px; color: var(--text-muted);"><i data-lucide="book-open" style="width:40px; margin-bottom:10px;"></i><p>No active courses.</p></div>';
            progressVal.textContent = "0%";
            return;
        }

        container.innerHTML = '';
        enrolledCourses.forEach(id => {
            const course = ASL_COURSES[id];
            if (!course) return;
            container.innerHTML += `
                <div class="course-item" onclick="showCourseDetails(${id})">
                    <div class="course-thumb" style="background: #F0F2FF; font-size: 24px;">🤟</div>
                    <div class="course-info">
                        <h3>${course.title}</h3>
                        <p>Completed 1 of ${course.lessons} Lessons</p>
                        <div class="progress-bar-container"><div class="progress-bar" style="width: 8%;"></div></div>
                    </div>
                </div>
            `;
        });

        const perc = Math.round((enrolledCourses.length / Object.keys(ASL_COURSES).length) * 100);
        progressVal.textContent = `${perc}%`;
        lucide.createIcons();
    }

    // --- SEARCH ---
    window.focusSearch = () => {
        navigateTo('home-screen');
        setTimeout(() => document.getElementById('course-search').focus(), 100);
    };

    window.searchByCategory = (cat) => {
        const input = document.getElementById('course-search');
        input.value = cat;
        input.dispatchEvent(new Event('input'));
    };

    const searchInput = document.getElementById('course-search');
    if (searchInput) {
        searchInput.addEventListener('input', (e) => {
            const q = e.target.value.toLowerCase();
            const allCoursesContainer = document.getElementById('all-courses-container');
            if (!allCoursesContainer) return;

            // Filter the existing cards based on category or title
            const cards = allCoursesContainer.querySelectorAll('.course-card-premium');
            cards.forEach(card => {
                const courseId = parseInt(card.dataset.id);
                const course = ASL_COURSES[courseId];
                if (!course) return;

                const match = course.title.toLowerCase().includes(q) ||
                    course.category.toLowerCase().includes(q) ||
                    course.instructor.toLowerCase().includes(q);

                card.style.display = match ? 'block' : 'none';
            });
        });
    }

    window.renderCourses = (filter = '') => {
        const container = document.getElementById('all-courses-container');
        if (!container) return;
        container.innerHTML = '';

        Object.values(ASL_COURSES).forEach(course => {
            if (filter && !course.category.toLowerCase().includes(filter.toLowerCase()) && !course.title.toLowerCase().includes(filter.toLowerCase())) {
                return;
            }

            const card = document.createElement('div');
            card.className = 'course-card-premium';
            card.dataset.id = course.id;
            card.setAttribute('onclick', `showCourseDetails(${course.id})`);
            card.innerHTML = `
                <div class="card-image-box">
                    <img src="${course.img}" alt="${course.title}" loading="lazy" onerror="this.onerror=null; this.src='https://images.unsplash.com/photo-1546410531-bb4caa6b424d?q=80&w=600';">
                    <button class="like-btn" onclick="toggleLike(event, ${course.id})">
                        <i data-lucide="heart"></i>
                    </button>
                </div>
                <div class="card-body">
                    <p class="card-category">${course.category}</p>
                    <h3>${course.title}</h3>
                    <div class="card-footer">
                        <div class="instructor-info">
                            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=${course.instructor.replace(' ', '')}" class="instructor-avatar">
                            <span class="instructor-name">${course.instructor}</span>
                        </div>
                        <div class="rating"><i data-lucide="star" style="width:12px; fill:#FFD700; color:#FFD700;"></i> ${course.rating}</div>
                    </div>
                </div>
            `;
            container.appendChild(card);
        });
        lucide.createIcons();
        updateLikeButtons();
    };

    window.searchByCategory = (cat) => {
        const input = document.getElementById('course-search');
        if (input) {
            input.value = cat;
            // Optionally, we can just render the filtered list directly
            renderCourses(cat);
        }
    };

    // --- INITIALIZE ---
    function init() {
        renderCourses();

        const schoolsContainer = document.getElementById('schools-container');
        if (schoolsContainer) {
            schoolsContainer.innerHTML = '';
            Object.values(SCHOOLS_DATA).forEach(school => {
                const card = document.createElement('div');
                card.className = 'school-card';
                card.setAttribute('onclick', `showSchoolDetails(${school.id})`);
                card.innerHTML = `
                    <img src="${school.logo}" class="school-logo" alt="${school.name}">
                    <div class="school-info">
                        <h3>${school.name}</h3>
                        <p>${school.location}</p>
                    </div>
                    <i data-lucide="chevron-right" style="width:16px; color:#B0B0C4;"></i>
                `;
                schoolsContainer.appendChild(card);
            });
        }

        updateLikeButtons();
        lucide.createIcons();

        const tags = document.querySelectorAll('.tag');
        tags.forEach(tag => tag.addEventListener('click', () => searchByCategory(tag.textContent)));
    }

    init();
});
