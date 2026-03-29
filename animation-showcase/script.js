/* ═══════════════════════════════════════════════════════════════
   Animation Showcase — JavaScript
   ═══════════════════════════════════════════════════════════════
   Libraries: GSAP 3.14.2, ScrollTrigger, SplitText, Lenis
   Effects:   Canvas Particles, Parallax, Text Split, Typewriter,
              Text Scramble, SVG Morphing, Counter, Stagger Grid,
              Custom Cursor, Magnetic Buttons, Marquee, Glassmorphism
   ═══════════════════════════════════════════════════════════════ */

// ── Register GSAP Plugins ───────────────────────────────────
gsap.registerPlugin(ScrollTrigger);
if (typeof SplitText !== "undefined") gsap.registerPlugin(SplitText);

// ── 1. LENIS SMOOTH SCROLL ──────────────────────────────────
// Creates butter-smooth scrolling with momentum. Lenis intercepts
// native scroll events and applies its own physics simulation.
const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smooth: true,
  smoothTouch: false,
});

function raf(time) {
  lenis.raf(time);
  requestAnimationFrame(raf);
}
requestAnimationFrame(raf);

// Sync Lenis with GSAP ScrollTrigger
lenis.on("scroll", ScrollTrigger.update);
gsap.ticker.add((time) => { lenis.raf(time * 1000); });
gsap.ticker.lagSmoothing(0);

// ── 2. CUSTOM CURSOR ────────────────────────────────────────
// Two elements: a small dot (fast) and a ring (slower, trailing).
// The ring uses GSAP's quickTo for that satisfying elastic trail.
const cursorDot = document.getElementById("cursor-dot");
const cursorRing = document.getElementById("cursor-ring");

if (cursorDot && cursorRing) {
  const moveDot = gsap.quickTo(cursorDot, "left", { duration: 0.05, ease: "power3" });
  const moveDotY = gsap.quickTo(cursorDot, "top", { duration: 0.05, ease: "power3" });
  const moveRing = gsap.quickTo(cursorRing, "left", { duration: 0.3, ease: "power3" });
  const moveRingY = gsap.quickTo(cursorRing, "top", { duration: 0.3, ease: "power3" });

  window.addEventListener("mousemove", (e) => {
    moveDot(e.clientX);
    moveDotY(e.clientY);
    moveRing(e.clientX);
    moveRingY(e.clientY);
  });
}

// ── 3. GLASSMORPHISM NAVBAR ─────────────────────────────────
// The navbar starts transparent and gains a frosted-glass
// backdrop-filter only after scrolling past 100px.
const navbar = document.getElementById("navbar");
ScrollTrigger.create({
  start: 100,
  onUpdate: (self) => {
    navbar.classList.toggle("scrolled", self.scroll() > 100);
  },
});

// ── 4. MAGNETIC BUTTONS (Hover Push/Pull) ───────────────────
// Elements with [data-magnetic] attract toward the cursor
// within their bounds. Uses getBoundingClientRect + GSAP.
document.querySelectorAll("[data-magnetic]").forEach((el) => {
  el.addEventListener("mousemove", (e) => {
    const rect = el.getBoundingClientRect();
    const x = e.clientX - rect.left - rect.width / 2;
    const y = e.clientY - rect.top - rect.height / 2;
    gsap.to(el, {
      x: x * 0.3,
      y: y * 0.3,
      duration: 0.3,
      ease: "power2.out",
    });
  });

  el.addEventListener("mouseleave", () => {
    gsap.to(el, { x: 0, y: 0, duration: 0.5, ease: "elastic.out(1, 0.3)" });
  });
});

// ── 5. HERO CANVAS PARTICLE VORTEX ──────────────────────────
// Canvas-based particle system with:
// - Orbital motion around center (vortex)
// - Mouse interaction (particles flee from cursor)
// - Connecting lines between nearby particles
;(function initHeroParticles() {
  const canvas = document.getElementById("hero-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let W, H, particles = [], mouse = { x: -9999, y: -9999 };

  function resize() {
    W = canvas.width = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }
  resize();
  window.addEventListener("resize", resize);
  canvas.addEventListener("mousemove", (e) => {
    const rect = canvas.getBoundingClientRect();
    mouse.x = e.clientX - rect.left;
    mouse.y = e.clientY - rect.top;
  });
  canvas.addEventListener("mouseleave", () => { mouse.x = -9999; mouse.y = -9999; });

  class Particle {
    constructor() {
      this.reset();
    }
    reset() {
      this.x = Math.random() * W;
      this.y = Math.random() * H;
      this.vx = (Math.random() - 0.5) * 0.5;
      this.vy = (Math.random() - 0.5) * 0.5;
      this.radius = Math.random() * 2 + 0.5;
      this.alpha = Math.random() * 0.6 + 0.2;
      const colors = ["66,133,244", "161,66,244", "245,56,160", "52,168,83"];
      this.color = colors[Math.floor(Math.random() * colors.length)];
    }
    update() {
      // Gentle vortex pull toward center
      const cx = W / 2, cy = H / 2;
      const dx = cx - this.x, dy = cy - this.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      this.vx += dx / dist * 0.002;
      this.vy += dy / dist * 0.002;

      // Mouse repulsion
      const mdx = this.x - mouse.x, mdy = this.y - mouse.y;
      const mDist = Math.sqrt(mdx * mdx + mdy * mdy);
      if (mDist < 150) {
        const force = (150 - mDist) / 150;
        this.vx += (mdx / mDist) * force * 0.5;
        this.vy += (mdy / mDist) * force * 0.5;
      }

      // Damping
      this.vx *= 0.99;
      this.vy *= 0.99;

      this.x += this.vx;
      this.y += this.vy;

      // Boundary wrap
      if (this.x < 0) this.x = W;
      if (this.x > W) this.x = 0;
      if (this.y < 0) this.y = H;
      if (this.y > H) this.y = 0;
    }
    draw() {
      ctx.beginPath();
      ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(${this.color},${this.alpha})`;
      ctx.fill();
    }
  }

  // Create particles
  const count = Math.min(150, Math.floor((W * H) / 8000));
  for (let i = 0; i < count; i++) particles.push(new Particle());

  function drawLines() {
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(100,130,200,${0.1 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }
  }

  function animate() {
    ctx.clearRect(0, 0, W, H);
    particles.forEach((p) => { p.update(); p.draw(); });
    drawLines();
    requestAnimationFrame(animate);
  }
  animate();
})();

// ── 6. HERO GSAP TIMELINE ───────────────────────────────────
// Orchestrated entrance animation using gsap.timeline()
// Each element enters in sequence with staggered timing.
const heroTL = gsap.timeline({ defaults: { ease: "power3.out" } });

heroTL
  .from("#hero-badge", { y: 30, opacity: 0, duration: 0.8 }, 0.3)
  .to("#hero-badge", { opacity: 1, duration: 0.8 }, 0.3)
  .from(".hero-title .line", { y: 80, opacity: 0, duration: 1, stagger: 0.15 }, 0.5)
  .to("#hero-desc", { opacity: 1, y: 0, duration: 0.8 }, 1)
  .from("#hero-desc", { y: 20 }, 1)
  .to("#hero-btns", { opacity: 1, y: 0, duration: 0.8 }, 1.2)
  .from("#hero-btns", { y: 20 }, 1.2)
  .to("#scroll-indicator", { opacity: 1, duration: 0.6 }, 1.5);

// ── 7. GSAP SPLITTEXT ANIMATIONS ────────────────────────────
// SplitText decomposes text into chars/words/lines, allowing
// per-element animation. Each type demonstrates a different method.

// 7a. Character-by-character reveal
if (typeof SplitText !== "undefined") {
  const charSplit = new SplitText(".split-chars", { type: "chars" });
  gsap.from(charSplit.chars, {
    y: 40, opacity: 0, rotateX: -90, duration: 0.6,
    stagger: 0.02,
    scrollTrigger: {
      trigger: ".split-chars",
      start: "top 80%",
      toggleActions: "play none none reverse",
    },
  });

  // 7b. Word-by-word fade up
  const wordSplit = new SplitText(".split-words", { type: "words" });
  gsap.from(wordSplit.words, {
    y: 30, opacity: 0, duration: 0.5,
    stagger: 0.04,
    scrollTrigger: {
      trigger: ".split-words",
      start: "top 80%",
      toggleActions: "play none none reverse",
    },
  });

  // 7c. Line-by-line reveal
  const lineSplit = new SplitText(".split-lines", { type: "lines" });
  gsap.from(lineSplit.lines, {
    y: 60, opacity: 0, duration: 0.8,
    stagger: 0.2,
    scrollTrigger: {
      trigger: ".split-lines",
      start: "top 80%",
      toggleActions: "play none none reverse",
    },
  });
} else {
  // Fallback if SplitText not available
  gsap.from(".split-chars", {
    y: 40, opacity: 0, duration: 1,
    scrollTrigger: { trigger: ".split-chars", start: "top 80%" },
  });
}

// ── 8. TYPEWRITER EFFECT ────────────────────────────────────
// Reveals text character by character at a fixed interval,
// simulating live typing. Uses recursive setTimeout.
;(function initTypewriter() {
  const el = document.getElementById("typewriter");
  if (!el) return;
  const fullText = el.textContent;
  el.textContent = "";
  let i = 0;

  ScrollTrigger.create({
    trigger: el,
    start: "top 85%",
    once: true,
    onEnter: () => {
      function type() {
        if (i < fullText.length) {
          el.textContent = fullText.slice(0, ++i);
          setTimeout(type, 40 + Math.random() * 30);
        }
      }
      type();
    },
  });
})();

// ── 9. TEXT SCRAMBLE EFFECT ──────────────────────────────────
// Characters scramble through random glyphs before settling
// on the correct letter. Creates a "decoding" aesthetic.
;(function initScramble() {
  const el = document.getElementById("scramble");
  if (!el) return;
  const finalText = el.textContent;
  const chars = "!<>-_\\/[]{}—=+*^?#ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz";
  let frame = 0;

  ScrollTrigger.create({
    trigger: el,
    start: "top 85%",
    once: true,
    onEnter: () => {
      const totalFrames = 40;
      function scramble() {
        if (frame >= totalFrames) {
          el.textContent = finalText;
          return;
        }
        const progress = frame / totalFrames;
        let result = "";
        for (let i = 0; i < finalText.length; i++) {
          if (i < finalText.length * progress) {
            result += finalText[i];
          } else {
            result += chars[Math.floor(Math.random() * chars.length)];
          }
        }
        el.textContent = result;
        frame++;
        requestAnimationFrame(scramble);
      }
      scramble();
    },
  });
})();

// ── 10. PARALLAX SCROLL LAYERS ──────────────────────────────
// Elements with [data-speed] move at different rates using
// ScrollTrigger scrub. Negative = moves opposite to scroll.
document.querySelectorAll("[data-speed]").forEach((el) => {
  const speed = parseFloat(el.dataset.speed);
  gsap.to(el, {
    y: () => speed * ScrollTrigger.maxScroll(window) * 0.3,
    ease: "none",
    scrollTrigger: {
      trigger: el.closest("section") || el,
      start: "top bottom",
      end: "bottom top",
      scrub: 1,
      invalidateOnRefresh: true,
    },
  });
});

// ── 11. HORIZONTAL SCROLL CARDS (ScrollTrigger Pin) ─────────
// The section is pinned while the card track scrolls horizontally.
// This is the signature GSAP ScrollTrigger "pin + scrub" effect.
;(function initHorizontalCards() {
  const track = document.getElementById("cards-track");
  if (!track) return;

  const totalWidth = track.scrollWidth - window.innerWidth;

  gsap.to(track, {
    x: () => -totalWidth,
    ease: "none",
    scrollTrigger: {
      trigger: ".cards-section",
      start: "top top",
      end: () => `+=${totalWidth}`,
      pin: true,
      scrub: 1,
      invalidateOnRefresh: true,
      anticipatePin: 1,
    },
  });
})();

// ── 12. INTERACTIVE PARTICLE CONSTELLATION ──────────────────
// Standalone particle system with mouse-following connections.
// Particles connect when within range AND near the cursor.
;(function initConstellationParticles() {
  const canvas = document.getElementById("particles-canvas");
  if (!canvas) return;
  const ctx = canvas.getContext("2d");
  let W, H, particles = [], mouseX = -999, mouseY = -999;

  function resize() {
    W = canvas.width = canvas.offsetWidth;
    H = canvas.height = canvas.offsetHeight;
  }
  resize();
  window.addEventListener("resize", resize);
  canvas.addEventListener("mousemove", (e) => {
    const r = canvas.getBoundingClientRect();
    mouseX = e.clientX - r.left;
    mouseY = e.clientY - r.top;
  });
  canvas.addEventListener("mouseleave", () => { mouseX = mouseY = -999; });

  const NUM = 200;
  for (let i = 0; i < NUM; i++) {
    particles.push({
      x: Math.random() * W,
      y: Math.random() * H,
      vx: (Math.random() - 0.5) * 0.8,
      vy: (Math.random() - 0.5) * 0.8,
      r: Math.random() * 2 + 1,
    });
  }

  function draw() {
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = "rgba(7, 8, 12, 0.95)";
    ctx.fillRect(0, 0, W, H);

    particles.forEach((p) => {
      p.x += p.vx;
      p.y += p.vy;
      if (p.x < 0 || p.x > W) p.vx *= -1;
      if (p.y < 0 || p.y > H) p.vy *= -1;

      // Mouse attraction
      const dx = mouseX - p.x, dy = mouseY - p.y;
      const dist = Math.sqrt(dx * dx + dy * dy);
      if (dist < 200) {
        p.vx += dx * 0.0003;
        p.vy += dy * 0.0003;
      }

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(100, 140, 255, ${0.6 - dist / 600})`;
      ctx.fill();
    });

    // Connect nearby particles
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const d = Math.sqrt(dx * dx + dy * dy);
        if (d < 100) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(66, 133, 244, ${0.15 * (1 - d / 100)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }

    requestAnimationFrame(draw);
  }
  draw();
})();

// ── 13. GSAP MARQUEE SPEED CONTROL ──────────────────────────
// Speed up/slow down marquee based on scroll velocity.
// This is a subtle touch that makes scrolling feel alive.
document.querySelectorAll(".marquee-track").forEach((track) => {
  const inner = track.querySelector(".marquee-inner");
  if (!inner) return;

  ScrollTrigger.create({
    trigger: track,
    start: "top bottom",
    end: "bottom top",
    onUpdate: (self) => {
      const velocity = Math.abs(self.getVelocity() / 1000);
      const speed = Math.min(velocity * 0.5, 3);
      gsap.to(inner, {
        timeScale: 1 + speed,
        duration: 0.3,
        overwrite: true,
      });
    },
  });
});

// ── 14. SVG MORPHING ────────────────────────────────────────
// Path transitions between pre-defined SVG path strings.
// GSAP morphs the "d" attribute on scroll scrub.
;(function initSVGMorph() {
  const path = document.getElementById("morph-path");
  const label = document.getElementById("morph-label");
  if (!path) return;

  const shapes = [
    { name: "Circle",   d: "M250,50 C350,50 450,150 450,250 C450,350 350,450 250,450 C150,450 50,350 50,250 C50,150 150,50 250,50Z" },
    { name: "Blob",     d: "M250,30 C380,30 470,120 460,230 C450,340 390,470 250,470 C110,470 40,350 40,240 C40,130 120,30 250,30Z" },
    { name: "Square",   d: "M100,80 C100,80 400,80 400,80 C400,80 400,420 400,420 C400,420 100,420 100,420 C100,420 100,80 100,80Z" },
    { name: "Diamond",  d: "M250,30 C250,30 470,250 470,250 C470,250 250,470 250,470 C250,470 30,250 30,250 C30,250 250,30 250,30Z" },
    { name: "Star",     d: "M250,30 C280,180 470,190 340,300 C380,460 250,380 120,460 C160,300 30,190 220,180 C220,180 250,30 250,30Z" },
  ];

  const tl = gsap.timeline({
    scrollTrigger: {
      trigger: ".morphing-section",
      start: "top center",
      end: "bottom center",
      scrub: 1,
    },
  });

  for (let i = 1; i < shapes.length; i++) {
    tl.to(path, {
      attr: { d: shapes[i].d },
      duration: 1,
      ease: "power2.inOut",
      onStart: () => { if (label) label.textContent = shapes[i].name; },
    });
  }
})();

// ── 15. COUNTER ANIMATION ───────────────────────────────────
// Numbers count up from 0 to target when scrolled into view.
// Uses GSAP's onUpdate to update the text content.
document.querySelectorAll(".count-up").forEach((el) => {
  const target = parseFloat(el.dataset.target) || 0;
  const isDecimal = String(target).includes(".");

  ScrollTrigger.create({
    trigger: el,
    start: "top 85%",
    once: true,
    onEnter: () => {
      gsap.to({ val: 0 }, {
        val: target,
        duration: 2,
        ease: "power2.out",
        onUpdate: function () {
          el.textContent = isDecimal
            ? this.targets()[0].val.toFixed(1)
            : Math.round(this.targets()[0].val).toLocaleString();
        },
      });
    },
  });
});

// ── 16. STAGGER GRID REVEAL ─────────────────────────────────
// Grid items appear one-by-one with a "from" stagger pattern
// that radiates from the center outward.
;(function initStaggerGrid() {
  const items = document.querySelectorAll("#stagger-grid .grid-item");
  if (!items.length) return;

  gsap.from(items, {
    scale: 0.5, opacity: 0, y: 40, duration: 0.6,
    stagger: { amount: 0.8, from: "center" },
    scrollTrigger: {
      trigger: "#stagger-grid",
      start: "top 80%",
      toggleActions: "play none none reverse",
    },
  });
})();

// ── 17. GENERIC REVEAL-UP ANIMATIONS ────────────────────────
// Any element with class="reveal-up" fades up on scroll.
document.querySelectorAll(".reveal-up").forEach((el) => {
  gsap.to(el, {
    y: 0, opacity: 1, duration: 0.8,
    ease: "power3.out",
    scrollTrigger: {
      trigger: el,
      start: "top 85%",
      toggleActions: "play none none reverse",
    },
  });
});

// ── 18. SCROLL-DRIVEN NAVBAR HIDE/SHOW ──────────────────────
// Navbar hides when scrolling down, reveals when scrolling up.
let lastScroll = 0;
ScrollTrigger.create({
  onUpdate: (self) => {
    const dir = self.direction;
    const scroll = self.scroll();
    if (scroll > 200) {
      gsap.to(navbar, {
        y: dir > 0 ? -80 : 0,
        duration: 0.3,
        ease: "power2.out",
      });
    }
    lastScroll = scroll;
  },
});

console.log("✅ Animation Showcase loaded — 18 effects active.");
