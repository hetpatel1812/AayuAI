/**
 * Aayu AI — Results Page JavaScript
 */
(function() {
  if (typeof window.LIVE_DATA === 'undefined') return;
  const DATA = window.LIVE_DATA;

  // Update param count
  const pCount = document.getElementById('param-count');
  if(pCount) pCount.textContent = DATA.params.length;

  // Dynamic Alerts
  const alertContainer = document.getElementById('dynamic-alerts');
  if (alertContainer) {
    const abnormal = DATA.params.filter(p => p.status !== 'NORMAL');
    if (abnormal.length > 0) {
      const tests = abnormal.map(p => p.test).join(', ');
      alertContainer.innerHTML = `
        <div class="alert alert-danger">
          <span class="alert-icon">🚨</span>
          <span><strong>Action required:</strong> Found ${abnormal.length} abnormal values (${tests}). Please review details below.</span>
        </div>`;
    } else {
      alertContainer.innerHTML = `
        <div class="alert alert-success" style="background: rgba(16, 185, 129, 0.1); border: 1px solid rgba(16, 185, 129, 0.2); color: #047857; padding: 12px 16px; border-radius: 8px; display: flex; align-items: flex-start; gap: 12px;">
          <span class="alert-icon">✅</span>
          <span><strong>Great news!</strong> All ${DATA.params.length} extracted parameters are within normal ranges. Keep up the healthy lifestyle!</span>
        </div>`;
    }
  }

  // Health ring
  if (document.getElementById('results-ring')) {
    drawHealthRing('results-ring', DATA.health_score, 110);
  }

  // Dynamic Sub-Scores
  if (document.getElementById('results-subscores')) {
    const categories = [...new Set(DATA.params.map(p => p.cat).filter(c => c))];
    const subScores = categories.map(cat => {
      const catParams = DATA.params.filter(p => p.cat === cat);
      const normalCount = catParams.filter(p => p.status === 'NORMAL').length;
      const score = Math.round((normalCount / catParams.length) * 100);
      return { name: cat, score: score, color: scoreColor(score) };
    });
    renderSubScores('results-subscores', subScores);
  }

  // Abnormal grid
  const abGrid = document.getElementById('ab-grid');
  if (abGrid) {
    const abnormal = DATA.params.filter(p => p.status !== 'NORMAL');
    abGrid.innerHTML = abnormal.length > 0 ? abnormal.map(p => {
      const bg = p.status === 'HIGH' ? 'var(--status-high-bg)' : 'var(--status-low-bg)';
      const bc = p.status === 'HIGH' ? 'rgba(239,68,68,0.2)' : 'rgba(96,165,250,0.2)';
      const vc = statusColor(p.status);
      return `<div class="ab-card" style="background:${bg}; border:1px solid ${bc};">
        <div class="ab-card-name">${p.test}</div>
        <div class="ab-card-value" style="color:${vc};">${p.value}<span class="ab-card-unit">${p.unit}</span></div>
        <div style="margin-top:4px;">${statusBadge(p.status)}</div>
      </div>`;
    }).join('') : '<div style="color:var(--text-dim);font-size:13px;padding:10px;">No abnormal values found! 🎉</div>';
    
    // Update abnormal count in title
    const statLabels = document.querySelectorAll('.stat-label');
    if(statLabels.length > 1) {
       statLabels[1].textContent = `Abnormal Values (${abnormal.length})`;
    }
  }

  // Category filters
  const filterBar = document.getElementById('filter-bar');
  if (filterBar) {
    const cats = ['All', 'CBC', 'KFT', 'LFT', 'Glucose', 'Lipid', 'Thyroid', 'Vitamins', 'Other'];
    filterBar.innerHTML = cats.map((c, i) =>
      `<button class="pill ${i === 0 ? 'active' : ''}" data-cat="${c}">${c}</button>`
    ).join('');

    document.querySelectorAll('#filter-bar .pill').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#filter-bar .pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        buildTable(btn.dataset.cat);
      });
    });
  }

  function buildTable(cat) {
    const tbody = document.getElementById('results-tbody');
    if (!tbody) return;
    
    const list = cat === 'All' ? DATA.params : DATA.params.filter(p => p.cat === cat);
    if(list.length === 0) {
        tbody.innerHTML = `<tr><td colspan="6" style="text-align:center;color:var(--text-dim);padding:20px;">No parameters found for this category.</td></tr>`;
        return;
    }
    
    tbody.innerHTML = list.map(p => {
      const rowClass = p.status === 'HIGH' ? 'row-high' : p.status === 'LOW' ? 'row-low' : '';
      const vc = statusColor(p.status);
      const range = (p.refLow && p.refHigh) ? `${p.refLow}–${p.refHigh}` : p.refHigh ? `< ${p.refHigh}` : '-';
      const dietHtml = p.diet ? `
        <div class="diet-box">
          <div class="diet-title">🍛 Indian Diet Tip</div>
          <p class="diet-text">${p.diet}</p>
        </div>` : '';

      return `
        <tr class="${rowClass}" style="cursor:pointer;" onclick="toggleExpand(${p.id})">
          <td style="font-weight:600; color:var(--text-primary);">${p.test}</td>
          <td><span class="badge badge-blue">${p.cat || 'Other'}</span></td>
          <td style="font-weight:800; color:${vc};">${p.value} <span style="font-size:10px; color:var(--text-dim);">${p.unit}</span></td>
          <td>${range}</td>
          <td>${statusBadge(p.status)}</td>
          <td><span class="detail-link">${p.status !== 'NORMAL' ? '→ Details' : '✓ Good'} <span id="arr-${p.id}">▼</span></span></td>
        </tr>
        <tr class="expand-row" id="xrow-${p.id}">
          <td colspan="6">
            <div class="expand-content">
              <div>
                <div class="ai-tag">🤖 AI Explanation (Groq · Llama 3.3 70B)</div>
                <p class="ai-text">${p.explanation || 'No explanation available.'}</p>
              </div>
              ${dietHtml}
            </div>
          </td>
        </tr>`;
    }).join('');
  }

  if (filterBar) {
    buildTable('All');
  }

  // Toggle expand
  window.toggleExpand = function(id) {
    const row = document.getElementById('xrow-' + id);
    const arr = document.getElementById('arr-' + id);
    if (!row) return;
    const isOpen = row.classList.contains('open');
    document.querySelectorAll('.expand-row').forEach(r => r.classList.remove('open'));
    document.querySelectorAll('[id^="arr-"]').forEach(a => a.textContent = '▼');
    if (!isOpen) { row.classList.add('open'); if (arr) arr.textContent = '▲'; }
  };
})();
