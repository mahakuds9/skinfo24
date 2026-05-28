// ========== MATRIX EFFECT ==========
const matrixCanvas = document.createElement('canvas');
matrixCanvas.id = 'matrix';
document.body.prepend(matrixCanvas);
const matrixCtx = matrixCanvas.getContext('2d');

matrixCanvas.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.07;
`;

matrixCanvas.width = window.innerWidth;
matrixCanvas.height = window.innerHeight;

const chars = '01アイウエオカキクケコサシスセソタチツテト';
const fontSize = 14;
const columns = matrixCanvas.width / fontSize;
const drops = Array(Math.floor(columns)).fill(1);

function drawMatrix() {
    matrixCtx.fillStyle = 'rgba(0, 0, 0, 0.05)';
    matrixCtx.fillRect(0, 0, matrixCanvas.width, matrixCanvas.height);
    matrixCtx.fillStyle = '#00d4ff';
    matrixCtx.font = fontSize + 'px monospace';
    drops.forEach((y, i) => {
        const char = chars[Math.floor(Math.random() * chars.length)];
        matrixCtx.fillText(char, i * fontSize, y * fontSize);
        if (y * fontSize > matrixCanvas.height && Math.random() > 0.975) {
            drops[i] = 0;
        }
        drops[i]++;
    });
}
setInterval(drawMatrix, 50);

// ========== GLOWING RINGS ==========
const ringCanvas = document.createElement('canvas');
ringCanvas.id = 'rings';
document.body.prepend(ringCanvas);
const ringCtx = ringCanvas.getContext('2d');

ringCanvas.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.15;
`;

ringCanvas.width = window.innerWidth;
ringCanvas.height = window.innerHeight;

let angle = 0;

function drawRings() {
    ringCtx.clearRect(0, 0, ringCanvas.width, ringCanvas.height);
    const cx = ringCanvas.width / 2;
    const cy = ringCanvas.height / 2;

    for (let i = 1; i <= 4; i++) {
        ringCtx.beginPath();
        ringCtx.ellipse(
            cx, cy,
            150 * i + Math.sin(angle + i) * 20,
            60 * i + Math.cos(angle + i) * 10,
            angle * (i % 2 === 0 ? 1 : -1),
            0, Math.PI * 2
        );
        ringCtx.strokeStyle = `rgba(0, 212, 255, ${0.4 - i * 0.07})`;
        ringCtx.lineWidth = 1.5;
        ringCtx.stroke();
    }
    angle += 0.005;
    requestAnimationFrame(drawRings);
}
drawRings();

// ========== GRADIENT WAVES ==========
const waveCanvas = document.createElement('canvas');
waveCanvas.id = 'waves';
document.body.prepend(waveCanvas);
const waveCtx = waveCanvas.getContext('2d');

waveCanvas.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.12;
`;

waveCanvas.width = window.innerWidth;
waveCanvas.height = window.innerHeight;

let waveAngle = 0;

function drawWaves() {
    waveCtx.clearRect(0, 0, waveCanvas.width, waveCanvas.height);

    for (let w = 0; w < 3; w++) {
        waveCtx.beginPath();
        waveCtx.moveTo(0, waveCanvas.height / 2);

        for (let x = 0; x < waveCanvas.width; x++) {
            const y = waveCanvas.height / 2 +
                Math.sin(x * 0.01 + waveAngle + w * 2) * (60 - w * 15) +
                Math.cos(x * 0.005 + waveAngle) * 30;
            waveCtx.lineTo(x, y);
        }

        waveCtx.strokeStyle = `rgba(0, 212, 255, ${0.4 - w * 0.1})`;
        waveCtx.lineWidth = 2;
        waveCtx.stroke();
    }
    waveAngle += 0.02;
    requestAnimationFrame(drawWaves);
}
drawWaves();

window.addEventListener('resize', () => {
    matrixCanvas.width = window.innerWidth;
    matrixCanvas.height = window.innerHeight;
    ringCanvas.width = window.innerWidth;
    ringCanvas.height = window.innerHeight;
    waveCanvas.width = window.innerWidth;
    waveCanvas.height = window.innerHeight;
});

// ========== SCROLL ANIMATION ==========
const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('show');
        }
    });
}, { threshold: 0.1 });

document.querySelectorAll('.skill, .skills, .experience, .hero-text').forEach(el => {
    el.classList.add('hidden');
    observer.observe(el);
});

// ========== TYPING EFFECT ==========
const titles = [
    "Application Support Engineer",
    "Linux & Python Enthusiast",
    "Incident Management Expert",
    "AWS Cloud Practitioner"
];

let titleIndex = 0;
let charIndex = 0;
let isDeleting = false;
const typingEl = document.querySelector('.typing');

function type() {
    if (!typingEl) return;
    const current = titles[titleIndex];

    if (isDeleting) {
        typingEl.textContent = current.substring(0, charIndex - 1);
        charIndex--;
    } else {
        typingEl.textContent = current.substring(0, charIndex + 1);
        charIndex++;
    }

    if (!isDeleting && charIndex === current.length) {
        setTimeout(() => isDeleting = true, 1500);
    } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        titleIndex = (titleIndex + 1) % titles.length;
    }

    setTimeout(type, isDeleting ? 50 : 100);
}
type();

// ========== PARTICLES BACKGROUND ==========
const canvas = document.createElement('canvas');
canvas.id = 'particles';
document.body.prepend(canvas);
const ctx = canvas.getContext('2d');

canvas.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    z-index: 0;
    pointer-events: none;
`;

let particles = [];

function resizeCanvas() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}
resizeCanvas();
window.addEventListener('resize', resizeCanvas);

class Particle {
    constructor() {
        this.reset();
    }
    reset() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.size = Math.random() * 2 + 0.5;
        this.speedX = (Math.random() - 0.5) * 0.5;
        this.speedY = (Math.random() - 0.5) * 0.5;
        this.opacity = Math.random() * 0.5 + 0.1;
    }
    update() {
        this.x += this.speedX;
        this.y += this.speedY;
        if (this.x < 0 || this.x > canvas.width ||
            this.y < 0 || this.y > canvas.height) {
            this.reset();
        }
    }
    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(0, 212, 255, ${this.opacity})`;
        ctx.fill();
    }
}

for (let i = 0; i < 100; i++) {
    particles.push(new Particle());
}

function animateParticles() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    particles.forEach(p => {
        p.update();
        p.draw();
    });

    // Draw lines between close particles
    particles.forEach((p1, i) => {
        particles.slice(i + 1).forEach(p2 => {
            const dx = p1.x - p2.x;
            const dy = p1.y - p2.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 100) {
                ctx.beginPath();
                ctx.strokeStyle = `rgba(0, 212, 255, ${0.1 * (1 - dist / 100)})`;
                ctx.lineWidth = 0.5;
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(p2.x, p2.y);
                ctx.stroke();
            }
        });
    });

    requestAnimationFrame(animateParticles);
}
animateParticles();

// ========== SMOOTH SCROLL ==========
document.querySelectorAll('a[href^="/"]').forEach(anchor => {
    anchor.addEventListener('click', function(e) {
        const href = this.getAttribute('href');
        if (href === '/') return;
    });
});

// ========== CURSOR GLOW EFFECT ==========
const cursor = document.createElement('div');
cursor.classList.add('cursor-glow');
document.body.appendChild(cursor);

document.addEventListener('mousemove', (e) => {
    cursor.style.left = e.clientX + 'px';
    cursor.style.top = e.clientY + 'px';
});

// ========== PROGRESS BAR ANIMATION ==========
const progressObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            const fill = entry.target;
            const width = fill.getAttribute('data-width');
            fill.style.width = width + '%';
        }
    });
}, { threshold: 0.3 });

document.querySelectorAll('.progress-fill').forEach(el => {
    progressObserver.observe(el);
});

// ========== SHOOTING STARS ==========
const starCanvas = document.createElement('canvas');
starCanvas.id = 'stars';
document.body.prepend(starCanvas);
const starCtx = starCanvas.getContext('2d');

starCanvas.style.cssText = `
    position: fixed;
    top: 0;
    left: 0;
    z-index: 0;
    pointer-events: none;
    opacity: 0.6;
`;

starCanvas.width = window.innerWidth;
starCanvas.height = window.innerHeight;

class ShootingStar {
    constructor() {
        this.reset();
    }
    reset() {
        this.x = Math.random() * starCanvas.width;
        this.y = Math.random() * starCanvas.height / 2;
        this.len = Math.random() * 150 + 50;
        this.speed = Math.random() * 8 + 4;
        this.opacity = Math.random() * 0.8 + 0.2;
        this.angle = Math.PI / 4;
    }
    update() {
        this.x += Math.cos(this.angle) * this.speed;
        this.y += Math.sin(this.angle) * this.speed;
        if (this.x > starCanvas.width || this.y > starCanvas.height) {
            this.reset();
        }
    }
    draw() {
        starCtx.beginPath();
        starCtx.moveTo(this.x, this.y);
        starCtx.lineTo(
            this.x - Math.cos(this.angle) * this.len,
            this.y - Math.sin(this.angle) * this.len
        );
        const gradient = starCtx.createLinearGradient(
            this.x, this.y,
            this.x - Math.cos(this.angle) * this.len,
            this.y - Math.sin(this.angle) * this.len
        );
        gradient.addColorStop(0, `rgba(0, 212, 255, ${this.opacity})`);
        gradient.addColorStop(1, 'rgba(0, 212, 255, 0)');
        starCtx.strokeStyle = gradient;
        starCtx.lineWidth = 2;
        starCtx.stroke();
    }
}

const shootingStars = Array(8).fill(null).map(() => new ShootingStar());

function animateStars() {
    starCtx.clearRect(0, 0, starCanvas.width, starCanvas.height);
    shootingStars.forEach(s => {
        s.update();
        s.draw();
    });
    requestAnimationFrame(animateStars);
}
animateStars();

// ========== MOUSE CLICK EXPLOSION ==========
document.addEventListener('click', (e) => {
    const count = 20;
    for (let i = 0; i < count; i++) {
        createParticleExplosion(e.clientX, e.clientY, i, count);
    }
});

function createParticleExplosion(x, y, i, total) {
    const particle = document.createElement('div');
    particle.classList.add('explosion-particle');
    document.body.appendChild(particle);

    const angle = (i / total) * Math.PI * 2;
    const distance = Math.random() * 80 + 40;
    const size = Math.random() * 6 + 3;
    const duration = Math.random() * 600 + 400;

    particle.style.cssText = `
        position: fixed;
        left: ${x}px;
        top: ${y}px;
        width: ${size}px;
        height: ${size}px;
        background: ${Math.random() > 0.5 ? '#00d4ff' : '#ffffff'};
        border-radius: 50%;
        pointer-events: none;
        z-index: 9999;
        transform: translate(-50%, -50%);
        transition: all ${duration}ms ease-out;
        box-shadow: 0 0 ${size * 2}px #00d4ff;
    `;

    document.body.appendChild(particle);

    requestAnimationFrame(() => {
        particle.style.left = `${x + Math.cos(angle) * distance}px`;
        particle.style.top = `${y + Math.sin(angle) * distance}px`;
        particle.style.opacity = '0';
        particle.style.transform = 'translate(-50%, -50%) scale(0)';
    });

    setTimeout(() => particle.remove(), duration);
}

// ========== GLOWING TEXT FLICKER ==========
const glowTargets = document.querySelectorAll('h1 span, .logo span, h2 span');

glowTargets.forEach(el => {
    el.style.cssText += `
        text-shadow: 0 0 10px #00d4ff, 0 0 20px #00d4ff, 0 0 40px #00d4ff;
        animation: flicker 3s infinite alternate;
    `;
});

// Add flicker keyframes dynamically
const flickerStyle = document.createElement('style');
flickerStyle.textContent = `
    @keyframes flicker {
        0%   { text-shadow: 0 0 5px #00d4ff, 0 0 10px #00d4ff; opacity: 1; }
        19%  { text-shadow: 0 0 5px #00d4ff, 0 0 10px #00d4ff; opacity: 1; }
        20%  { text-shadow: none; opacity: 0.8; }
        21%  { text-shadow: 0 0 5px #00d4ff, 0 0 10px #00d4ff; opacity: 1; }
        49%  { text-shadow: 0 0 5px #00d4ff, 0 0 10px #00d4ff; opacity: 1; }
        50%  { text-shadow: none; opacity: 0.85; }
        51%  { text-shadow: 0 0 20px #00d4ff, 0 0 40px #00d4ff; opacity: 1; }
        100% { text-shadow: 0 0 20px #00d4ff, 0 0 60px #00d4ff, 0 0 80px #00d4ff; opacity: 1; }
    }
`;
document.head.appendChild(flickerStyle);

// Resize all canvases
window.addEventListener('resize', () => {
    starCanvas.width = window.innerWidth;
    starCanvas.height = window.innerHeight;
});