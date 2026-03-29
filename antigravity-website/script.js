/* ============================================
   Google Antigravity Website - JavaScript
   Handles: Particles, Scroll Animations,
   IDE reveal, Carousel, A-Logo animation
   ============================================ */

document.addEventListener('DOMContentLoaded', () => {
    // Initialize all modules
    initParticles();
    initScrollAnimations();
    initIDEShowcase();
    initALogoAnimation();
    initHeader();
    initCarousel();
    initCTAParticles();
    initDownloadParticles();
});

/* ============================================
   PARTICLE BACKGROUND (Hero)
   ============================================ */
function initParticles() {
    const canvas = document.getElementById('particle-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let particles = [];
    let animFrame;
    
    const colors = [
        '#4285F4', '#4285F4', '#4285F4', // More blue 
        '#EA4335',
        '#FBBC05',
        '#34A853',
        '#7B68EE', // subtle purple accent
    ];
    
    function resize() {
        canvas.width = canvas.offsetWidth * window.devicePixelRatio;
        canvas.height = canvas.offsetHeight * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }
    
    function createParticles() {
        particles = [];
        const count = Math.min(200, Math.floor(canvas.offsetWidth * 0.15));
        
        for (let i = 0; i < count; i++) {
            // Create a vortex-like distribution
            const angle = Math.random() * Math.PI * 2;
            const radius = Math.random() * canvas.offsetWidth * 0.4;
            const centerX = canvas.offsetWidth * 0.3;
            const centerY = canvas.offsetHeight * 0.3;
            
            particles.push({
                x: centerX + Math.cos(angle) * radius,
                y: centerY + Math.sin(angle) * radius,
                size: Math.random() * 3 + 1,
                color: colors[Math.floor(Math.random() * colors.length)],
                vx: (Math.random() - 0.5) * 0.5,
                vy: (Math.random() - 0.5) * 0.3 + 0.2,
                angle: angle,
                radius: radius,
                speed: Math.random() * 0.003 + 0.001,
                opacity: Math.random() * 0.6 + 0.2,
            });
        }
    }
    
    function animate() {
        ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);
        
        const scrollY = window.scrollY;
        const maxScroll = canvas.offsetHeight;
        const scrollProgress = Math.min(scrollY / maxScroll, 1);
        
        particles.forEach(p => {
            // Orbital movement
            p.angle += p.speed;
            const centerX = canvas.offsetWidth * 0.3;
            const centerY = canvas.offsetHeight * 0.3;
            
            p.x = centerX + Math.cos(p.angle) * p.radius + p.vx;
            p.y = centerY + Math.sin(p.angle) * p.radius + p.vy;
            
            // Scatter on scroll
            p.x += scrollProgress * (Math.random() - 0.5) * 100;
            p.y += scrollProgress * 50;
            
            // Fade with scroll
            const alpha = p.opacity * (1 - scrollProgress * 0.8);
            
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = Math.max(0.05, alpha);
            ctx.fill();
        });
        
        ctx.globalAlpha = 1;
        animFrame = requestAnimationFrame(animate);
    }
    
    resize();
    createParticles();
    animate();
    
    window.addEventListener('resize', () => {
        resize();
        createParticles();
    });
}

/* ============================================
   SCROLL ANIMATIONS
   ============================================ */
function initScrollAnimations() {
    const observerOptions = {
        root: null,
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
            }
        });
    }, observerOptions);
    
    // Observe feature sections
    document.querySelectorAll('.feature-section').forEach(section => {
        observer.observe(section);
    });
    
    // Observe platform statement
    const statementText = document.getElementById('statement-text');
    if (statementText) {
        observer.observe(statementText);
    }
    
    // Observe all fade-in-up elements
    document.querySelectorAll('.fade-in-up').forEach(el => {
        observer.observe(el);
    });
}

/* ============================================
   IDE SHOWCASE
   ============================================ */
function initIDEShowcase() {
    const ideWindow = document.getElementById('ide-window');
    const ideOverlay = document.getElementById('ide-logo-overlay');
    if (!ideWindow) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                ideWindow.classList.add('visible');
                
                // Remove the A logo overlay after animation
                setTimeout(() => {
                    if (ideOverlay) {
                        ideOverlay.classList.add('hidden');
                    }
                }, 2500);
            }
        });
    }, { threshold: 0.1 });
    
    observer.observe(ideWindow);
}

/* ============================================
   A LOGO ANIMATION (Canvas)
   ============================================ */
function initALogoAnimation() {
    const canvas = document.getElementById('a-logo-canvas');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    const parent = canvas.parentElement;
    let particles = [];
    let startTime = Date.now();
    
    function resize() {
        canvas.width = parent.offsetWidth * window.devicePixelRatio;
        canvas.height = parent.offsetHeight * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }
    
    function createAParticles() {
        particles = [];
        const w = parent.offsetWidth;
        const h = parent.offsetHeight;
        const cx = w / 2;
        const cy = h / 2;
        const scale = Math.min(w, h) * 0.35;
        
        // A shape path points
        const aPath = [];
        const steps = 300;
        
        // Left leg of A
        for (let i = 0; i < steps / 4; i++) {
            const t = i / (steps / 4);
            aPath.push({
                x: cx - scale * 0.4 + t * scale * 0.4,
                y: cy + scale * 0.5 - t * scale
            });
        }
        
        // Top curve of A
        for (let i = 0; i < steps / 4; i++) {
            const t = i / (steps / 4);
            const angle = Math.PI + t * Math.PI;
            aPath.push({
                x: cx + Math.cos(angle) * scale * 0.08,
                y: cy - scale * 0.5 + Math.sin(angle) * scale * 0.05 + scale * 0.05
            });
        }
        
        // Right leg of A
        for (let i = 0; i < steps / 4; i++) {
            const t = i / (steps / 4);
            aPath.push({
                x: cx + t * scale * 0.4,
                y: cy - scale * 0.5 + t * scale
            });
        }
        
        // Cross bar
        for (let i = 0; i < steps / 4; i++) {
            const t = i / (steps / 4);
            aPath.push({
                x: cx - scale * 0.2 + t * scale * 0.4,
                y: cy + scale * 0.05
            });
        }
        
        // Scatter particles along the A path
        const colors = ['#4285F4', '#34A853', '#FBBC05', '#EA4335', '#4285F4', '#4285F4'];
        
        aPath.forEach((point, i) => {
            const scatter = 3;
            for (let j = 0; j < 2; j++) {
                const colorIdx = Math.floor((i / aPath.length) * colors.length);
                particles.push({
                    x: point.x + (Math.random() - 0.5) * scatter,
                    y: point.y + (Math.random() - 0.5) * scatter,
                    targetX: point.x,
                    targetY: point.y,
                    size: Math.random() * 2.5 + 1,
                    color: colors[colorIdx % colors.length],
                    delay: i * 3,
                    opacity: 0,
                    phase: Math.random() * Math.PI * 2
                });
            }
        });
        
        // Background scattered particles
        for (let i = 0; i < 100; i++) {
            particles.push({
                x: Math.random() * w,
                y: Math.random() * h,
                targetX: Math.random() * w,
                targetY: Math.random() * h,
                size: Math.random() * 1.5 + 0.5,
                color: colors[Math.floor(Math.random() * colors.length)],
                delay: Math.random() * 500,
                opacity: 0,
                phase: Math.random() * Math.PI * 2,
                isBackground: true
            });
        }
    }
    
    function animate() {
        const w = parent.offsetWidth;
        const h = parent.offsetHeight;
        const elapsed = Date.now() - startTime;
        
        ctx.clearRect(0, 0, w, h);
        
        particles.forEach(p => {
            const timeActive = elapsed - p.delay;
            if (timeActive < 0) return;
            
            // Fade in
            const fadeDuration = 300;
            p.opacity = Math.min(1, timeActive / fadeDuration);
            
            if (p.isBackground) {
                p.opacity *= 0.15;
            }
            
            // Glow effect
            const glow = Math.sin(elapsed * 0.003 + p.phase) * 0.3 + 0.7;
            
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size * glow, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.globalAlpha = p.opacity * glow;
            ctx.fill();
        });
        
        ctx.globalAlpha = 1;
        requestAnimationFrame(animate);
    }
    
    resize();
    createAParticles();
    animate();
    
    window.addEventListener('resize', () => {
        resize();
        createAParticles();
    });
}

/* ============================================
   HEADER SCROLL BEHAVIOR
   ============================================ */
function initHeader() {
    const header = document.getElementById('site-header');
    if (!header) return;
    
    let lastScrollY = 0;
    
    window.addEventListener('scroll', () => {
        const scrollY = window.scrollY;
        
        if (scrollY > 50) {
            header.classList.add('scrolled');
        } else {
            header.classList.remove('scrolled');
        }
        
        lastScrollY = scrollY;
    }, { passive: true });
}

/* ============================================
   DEVELOPER CARDS CAROUSEL
   ============================================ */
function initCarousel() {
    const carousel = document.getElementById('devs-carousel');
    const prevBtn = document.getElementById('carousel-prev');
    const nextBtn = document.getElementById('carousel-next');
    
    if (!carousel || !prevBtn || !nextBtn) return;
    
    const cardWidth = 564; // min-width + gap
    
    prevBtn.addEventListener('click', () => {
        carousel.scrollBy({ left: -cardWidth, behavior: 'smooth' });
    });
    
    nextBtn.addEventListener('click', () => {
        carousel.scrollBy({ left: cardWidth, behavior: 'smooth' });
    });
}

/* ============================================
   CTA SECTION PARTICLES
   ============================================ */
function initCTAParticles() {
    ['cta-particles-1', 'cta-particles-2'].forEach(id => {
        const canvas = document.getElementById(id);
        if (!canvas) return;
        
        const ctx = canvas.getContext('2d');
        let dots = [];
        
        function resize() {
            canvas.width = canvas.offsetWidth * window.devicePixelRatio;
            canvas.height = canvas.offsetHeight * window.devicePixelRatio;
            ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
        }
        
        function createDots() {
            dots = [];
            const w = canvas.offsetWidth;
            const h = canvas.offsetHeight;
            
            for (let i = 0; i < 80; i++) {
                dots.push({
                    x: Math.random() * w,
                    y: Math.random() * h,
                    size: Math.random() * 2 + 0.5,
                    vy: Math.random() * 0.3 + 0.1,
                    opacity: Math.random() * 0.4 + 0.1
                });
            }
        }
        
        function animate() {
            const w = canvas.offsetWidth;
            const h = canvas.offsetHeight;
            
            ctx.clearRect(0, 0, w, h);
            
            dots.forEach(d => {
                d.y += d.vy;
                if (d.y > h) {
                    d.y = 0;
                    d.x = Math.random() * w;
                }
                
                ctx.beginPath();
                ctx.arc(d.x, d.y, d.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(100, 100, 120, ${d.opacity})`;
                ctx.fill();
            });
            
            requestAnimationFrame(animate);
        }
        
        resize();
        createDots();
        animate();
        
        window.addEventListener('resize', () => {
            resize();
            createDots();
        });
    });
}

/* ============================================
   DOWNLOAD CTA PARTICLES
   ============================================ */
function initDownloadParticles() {
    const canvas = document.getElementById('download-particles');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    let particles = [];
    
    function resize() {
        canvas.width = canvas.offsetWidth * window.devicePixelRatio;
        canvas.height = canvas.offsetHeight * window.devicePixelRatio;
        ctx.scale(window.devicePixelRatio, window.devicePixelRatio);
    }
    
    function createParticles() {
        particles = [];
        const w = canvas.offsetWidth;
        const h = canvas.offsetHeight;
        
        // Create spiral/vortex pattern of blue dots
        for (let i = 0; i < 200; i++) {
            const angle = (i / 200) * Math.PI * 8;
            const radius = (i / 200) * Math.max(w, h) * 0.5;
            
            particles.push({
                x: w * 0.6 + Math.cos(angle) * radius + (Math.random() - 0.5) * 40,
                y: h * 0.4 + Math.sin(angle) * radius + (Math.random() - 0.5) * 40,
                size: Math.random() * 2 + 1,
                angle: angle,
                radius: radius,
                speed: 0.001 + Math.random() * 0.002,
                opacity: Math.random() * 0.4 + 0.1,
                centerX: w * 0.6,
                centerY: h * 0.4
            });
        }
        
        // Random scattered dots
        for (let i = 0; i < 60; i++) {
            particles.push({
                x: Math.random() * w,
                y: Math.random() * h,
                size: Math.random() * 1.5 + 0.5,
                angle: 0,
                radius: 0,
                speed: 0,
                opacity: Math.random() * 0.2 + 0.05,
                isStatic: true
            });
        }
    }
    
    function animate() {
        const w = canvas.offsetWidth;
        const h = canvas.offsetHeight;
        
        ctx.clearRect(0, 0, w, h);
        
        particles.forEach(p => {
            if (!p.isStatic) {
                p.angle += p.speed;
                p.x = p.centerX + Math.cos(p.angle) * p.radius;
                p.y = p.centerY + Math.sin(p.angle) * p.radius;
            }
            
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
            ctx.fillStyle = `rgba(80, 120, 220, ${p.opacity})`;
            ctx.fill();
        });
        
        requestAnimationFrame(animate);
    }
    
    resize();
    createParticles();
    animate();
    
    window.addEventListener('resize', () => {
        resize();
        createParticles();
    });
}

/* ============================================
   SMOOTH SCROLL LINKS
   ============================================ */
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const targetId = this.getAttribute('href');
        if (targetId === '#') return;
        
        const target = document.querySelector(targetId);
        if (target) {
            e.preventDefault();
            target.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    });
});
