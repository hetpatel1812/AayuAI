/**
 * Aayu AI — Splash Screen Animation
 * Canvas particle system + timed transition
 */

(function () {
  const splash = document.getElementById('splash-overlay');
  if (!splash) return;

  // Only show splash once per session
  if (sessionStorage.getItem('aayuSplashShown')) {
    splash.style.display = 'none';
    return;
  }
  sessionStorage.setItem('aayuSplashShown', 'true');

  const canvas = document.getElementById('splash-canvas');
  const ctx = canvas.getContext('2d');
  let particles = [];
  let animId = null;
  let w, h;

  function resize() {
    w = canvas.width = window.innerWidth;
    h = canvas.height = window.innerHeight;
  }

  function createParticles() {
    particles = [];
    const count = Math.min(Math.floor((w * h) / 15000), 80);
    for (let i = 0; i < count; i++) {
      particles.push({
        x: Math.random() * w,
        y: Math.random() * h,
        r: Math.random() * 1.5 + 0.5,
        vx: (Math.random() - 0.5) * 0.3,
        vy: (Math.random() - 0.5) * 0.3,
        alpha: Math.random() * 0.4 + 0.1
      });
    }
  }

  function drawParticles() {
    ctx.clearRect(0, 0, w, h);

    // Draw connections
    for (let i = 0; i < particles.length; i++) {
      for (let j = i + 1; j < particles.length; j++) {
        const dx = particles[i].x - particles[j].x;
        const dy = particles[i].y - particles[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 120) {
          ctx.beginPath();
          ctx.moveTo(particles[i].x, particles[i].y);
          ctx.lineTo(particles[j].x, particles[j].y);
          ctx.strokeStyle = `rgba(0, 212, 170, ${0.06 * (1 - dist / 120)})`;
          ctx.lineWidth = 0.5;
          ctx.stroke();
        }
      }
    }

    // Draw particles
    for (const p of particles) {
      p.x += p.vx;
      p.y += p.vy;

      if (p.x < 0) p.x = w;
      if (p.x > w) p.x = 0;
      if (p.y < 0) p.y = h;
      if (p.y > h) p.y = 0;

      ctx.beginPath();
      ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
      ctx.fillStyle = `rgba(0, 212, 170, ${p.alpha})`;
      ctx.fill();
    }

    animId = requestAnimationFrame(drawParticles);
  }

  function dismissSplash() {
    splash.classList.add('fade-out');
    setTimeout(() => {
      splash.style.display = 'none';
      cancelAnimationFrame(animId);
    }, 800);
  }

  // Init
  resize();
  createParticles();
  drawParticles();
  window.addEventListener('resize', () => { resize(); createParticles(); });

  // Auto-dismiss after 3.5 seconds
  setTimeout(dismissSplash, 3500);

  // Skip button
  const skipBtn = document.getElementById('splash-skip');
  if (skipBtn) {
    skipBtn.addEventListener('click', dismissSplash);
  }
})();
