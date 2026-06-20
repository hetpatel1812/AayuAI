/**
 * Aayu AI — App Utilities
 * Toast notifications, Disclaimer logic, etc.
 */

const AppUtils = {
  // Toast Notification System
  showToast(title, message, type = 'info') {
    let container = document.getElementById('toast-container');
    if (!container) {
      container = document.createElement('div');
      container.id = 'toast-container';
      container.className = 'toast-container';
      document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    let icon = 'ℹ️';
    if (type === 'success') icon = '✅';
    if (type === 'error') icon = '🚨';
    if (type === 'warning') icon = '⚠️';

    toast.innerHTML = `
      <div class="toast-icon">${icon}</div>
      <div class="toast-content">
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
      </div>
      <button class="toast-close" onclick="this.parentElement.remove()">✕</button>
    `;

    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.classList.add('show'), 10);

    // Auto remove after 5s
    setTimeout(() => {
      toast.classList.remove('show');
      setTimeout(() => toast.remove(), 400);
    }, 5000);
  },

  // Medical Disclaimer System
  initDisclaimer() {
    // Check if user has already accepted
    if (localStorage.getItem('aayu_disclaimer_accepted')) {
      return;
    }

    const overlay = document.createElement('div');
    overlay.className = 'disclaimer-overlay';
    overlay.innerHTML = `
      <div class="disclaimer-modal">
        <div class="disclaimer-icon">⚕️</div>
        <div class="disclaimer-title">Medical Disclaimer</div>
        <div class="disclaimer-text">
          Aayu AI provides educational health insights based on your blood reports. It is <strong>not a substitute for professional medical advice, diagnosis, or treatment.</strong><br><br>
          Always seek the advice of your physician or other qualified health provider with any questions you may have regarding a medical condition.
        </div>
        <button class="btn btn-primary w-full" id="btn-accept-disclaimer">I Understand and Agree</button>
      </div>
    `;

    document.body.appendChild(overlay);

    // Show with animation
    setTimeout(() => overlay.classList.add('show'), 500);

    document.getElementById('btn-accept-disclaimer').addEventListener('click', () => {
      localStorage.setItem('aayu_disclaimer_accepted', 'true');
      overlay.classList.remove('show');
      setTimeout(() => overlay.remove(), 400);
      this.showToast('Welcome to Aayu AI', 'Your preferences have been saved.', 'success');
    });
  }
};

// Initialize app-wide utilities when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  // Only show disclaimer on app pages, not landing/auth
  const isAppPage = document.querySelector('.app-sidebar') !== null;
  if (isAppPage) {
    AppUtils.initDisclaimer();
  }
});

// ── UI Formatting Functions ────────────────────────────────
function scoreColor(score) {
  if (score >= 70) return '#10B981';
  if (score >= 50) return '#F59E0B';
  return '#EF4444';
}

function statusColor(status) {
  switch (status) {
    case 'HIGH': return '#EF4444';
    case 'LOW': return '#60A5FA';
    case 'CRITICAL': return '#F43F5E';
    default: return '#10B981';
  }
}

function statusBadge(status) {
  const map = {
    NORMAL: {cls: 'badge-normal', text: '✓ Normal'},
    HIGH:   {cls: 'badge-high',   text: '↑ High'},
    LOW:    {cls: 'badge-low',    text: '↓ Low'},
    CRITICAL: {cls: 'badge-critical', text: '⚠ Critical'}
  };
  const d = map[status] || map.NORMAL;
  return `<span class="badge ${d.cls}">${d.text}</span>`;
}

function drawHealthRing(svgId, score, size) {
  const el = document.getElementById(svgId);
  if (!el) return;
  const sw = size <= 80 ? 7 : 9;
  const r = (size - sw) / 2;
  const cx = size / 2;
  const cy = size / 2;
  const C = 2 * Math.PI * r;
  const offset = C - (score / 100) * C;
  const col = scoreColor(score);
  const fs1 = size <= 80 ? 18 : 24;
  const fs2 = size <= 80 ? 8 : 10;

  el.innerHTML = `
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="rgba(15,23,42,0.06)" stroke-width="${sw}"/>
    <circle cx="${cx}" cy="${cy}" r="${r}" fill="none" stroke="${col}" stroke-width="${sw}"
            stroke-dasharray="${C}" stroke-dashoffset="${offset}" stroke-linecap="round"
            transform="rotate(-90 ${cx} ${cy})" style="transition: stroke-dashoffset 1.5s ease;"/>
    <text x="${cx}" y="${cy - 4}" text-anchor="middle" font-family="Outfit" font-size="${fs1}" font-weight="800" fill="${col}">${score}</text>
    <text x="${cx}" y="${cy + fs2 + 4}" text-anchor="middle" font-size="${fs2}" fill="#94A3B8">/100</text>
  `;
}

function renderSubScores(containerId, scores) {
  const el = document.getElementById(containerId);
  if (!el) return;
  el.innerHTML = scores.map(s => `
    <div style="margin-bottom: 8px;">
      <div style="display:flex; justify-content:space-between; margin-bottom:3px;">
        <span style="font-size:12px; color:var(--text-muted);">${s.name}</span>
        <span style="font-size:12px; font-weight:700; color:${s.color};">${s.score}</span>
      </div>
      <div class="progress-bar">
        <div class="progress-fill" style="width:${s.score}%; background:${s.color};"></div>
      </div>
    </div>
  `).join('');
}
