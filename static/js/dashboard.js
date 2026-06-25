/**
 * Aayu AI — Dashboard JavaScript
 */
(function() {
  if (typeof window.LIVE_DATA === 'undefined') return;
  const DATA = window.LIVE_DATA;

  // If no report uploaded yet, show empty state
  if (!DATA.id) {
    document.querySelector('.dash-body').innerHTML = `
      <div style="grid-column: 1 / -1;">
        <div class="glass-card empty-state animate-fade-in-up">
          <div class="empty-state-icon">📋</div>
          <h3>No reports found</h3>
          <p>Upload your first blood test report to see your dashboard insights.</p>
          <a href="/upload" class="btn btn-primary" style="margin-top: 10px;">+ Upload Report</a>
        </div>
      </div>
    `;
    const alertBanner = document.getElementById('dash-alert');
    if(alertBanner) alertBanner.style.display = 'none';
    
    // Update header
    const pageHeaderP = document.querySelector('.page-header-left p');
    if(pageHeaderP) pageHeaderP.textContent = `Family health overview · Welcome ${DATA.patient_name}`;
    
    // Hide export button
    const exportBtn = document.getElementById('dash-export-btn');
    if(exportBtn) exportBtn.style.display = 'none';
    
    // Stats for empty
    const dashStats = document.getElementById('dash-stats');
    if (dashStats) {
      dashStats.innerHTML = `
        <div class="stat-card"><div class="stat-label">Health Score</div><div class="stat-value" style="color: #94A3B8;">--</div><div class="stat-sub">No data</div></div>
        <div class="stat-card"><div class="stat-label">Abnormal Values</div><div class="stat-value" style="color: #94A3B8;">--</div><div class="stat-sub">No data</div></div>
      `;
    }
    return;
  }

  const abnormalParams = DATA.params.filter(p => p.status !== 'NORMAL');
  const abnormalCount = abnormalParams.length;

  // Update Alert Banner
  const alertBanner = document.getElementById('dash-alert');
  if (alertBanner) {
    alertBanner.style.display = 'flex';
    // Remove any previously set inline styles that were hardcoded
    alertBanner.style.background = '';
    alertBanner.style.border = '';
    alertBanner.style.color = '';
    
    if (abnormalCount > 0) {
      alertBanner.className = 'alert alert-warning animate-fade-in-down';
      const topTests = abnormalParams.slice(0, 5).map(p => p.test).join(', ');
      alertBanner.innerHTML = `
        <span class="alert-icon">⚠️</span>
        <span><strong>Action needed:</strong> ${abnormalCount} abnormal values — ${topTests}${abnormalCount > 5 ? ' and more' : ''} require attention.</span>
      `;
    } else {
      alertBanner.className = 'alert alert-success animate-fade-in-down';
      alertBanner.innerHTML = `
        <span class="alert-icon">✅</span>
        <span><strong>All good!</strong> No abnormal values detected in your recent report.</span>
      `;
    }
  }

  // Update header
  const pageHeaderP = document.querySelector('.page-header-left p');
  if(pageHeaderP) {
    pageHeaderP.textContent = `Family health overview · Latest: ${DATA.test_date} · ${DATA.lab_name}`;
  }
  
  const reportHeaderTitle = document.querySelector('.dash-table-header-title');
  if(reportHeaderTitle) {
      reportHeaderTitle.textContent = `Latest Report — ${DATA.patient_name} · ${DATA.test_date}`;
  }

  // Stat cards
  const stats = [
    {label: 'Health Score', value: DATA.health_score, suffix: '/100', color: scoreColor(DATA.health_score), sub: DATA.health_score >= 80 ? 'Good' : 'Needs attention'},
    {label: 'Abnormal Values', value: abnormalCount, suffix: `/${DATA.params.length}`, color: abnormalCount > 0 ? '#EF4444' : '#10B981', sub: abnormalCount > 0 ? 'Require action' : 'All normal'},
    {label: 'Reports Uploaded', value: 1, suffix: '', color: '#3B82F6', sub: 'Total reports'}
  ];

  const dashStats = document.getElementById('dash-stats');
  if (dashStats) {
    dashStats.innerHTML = stats.map(s => `
      <div class="stat-card">
        <div class="stat-label">${s.label}</div>
        <div class="stat-value" style="color: ${s.color};">${s.value}<span style="font-size:13px; color:var(--text-dim); font-weight:400;">${s.suffix}</span></div>
        <div class="stat-sub">${s.sub}</div>
      </div>
    `).join('');
  }

  // Health ring
  if (document.getElementById('dash-ring')) {
    drawHealthRing('dash-ring', DATA.health_score, 130);
  }

  // Sub-scores
  if (document.getElementById('dash-subscores')) {
    const categories = [...new Set(DATA.params.map(p => p.cat).filter(c => c))];
    const subScores = categories.map(cat => {
      const catParams = DATA.params.filter(p => p.cat === cat);
      const normalCount = catParams.filter(p => p.status === 'NORMAL').length;
      const score = Math.round((normalCount / catParams.length) * 100);
      return { name: cat, score: score, color: scoreColor(score) };
    });
    renderSubScores('dash-subscores', subScores);
  }

  // Parameter Grid Cards (first 10 parameters)
  const paramsGrid = document.getElementById('dash-params-grid');
  if (paramsGrid) {
    // Show abnormal first, then rest
    const sortedParams = [...DATA.params].sort((a,b) => (a.status==='NORMAL'?1:0) - (b.status==='NORMAL'?1:0)).slice(0, 10);
    paramsGrid.innerHTML = sortedParams.map(p => {
      const vc = statusColor(p.status);
      const range = (p.refLow && p.refHigh) ? `${p.refLow}–${p.refHigh}` : p.refHigh ? `< ${p.refHigh}` : '-';
      
      const catIcons = {
        'CBC': '🩸',
        'KFT': '💧',
        'LFT': '☘️',
        'Glucose': '🍬',
        'Lipid': '🥑',
        'Thyroid': '⚡',
        'Vitamins': '💊',
        'Other': '🔬'
      };
      const icon = catIcons[p.cat] || '🔬';
      
      const cardStatusClass = p.status === 'HIGH' ? 'param-status-high' : p.status === 'LOW' ? 'param-status-low' : 'param-status-normal';

      return `
        <div class="dash-param-item ${cardStatusClass}" onclick="window.location.href='/results/${DATA.id}'">
          <div class="param-item-left">
            <div class="param-icon">${icon}</div>
            <div>
              <div class="param-name">${p.test}</div>
              <span class="badge-mini">${p.cat || 'Other'}</span>
            </div>
          </div>
          <div class="param-item-right">
            <div class="param-value" style="color: ${vc};">
              ${p.value} <span class="param-unit">${p.unit}</span>
            </div>
            <div class="param-meta">
              <span style="font-size: 10px; color: var(--text-dim);">Normal: ${range}</span>
              <div style="margin-top: 3px;">${statusBadge(p.status)}</div>
            </div>
          </div>
        </div>
      `;
    }).join('');
    
    const badgesContainer = document.getElementById('dash-header-badges');
    if(badgesContainer) {
        badgesContainer.innerHTML = `
            <span class="badge ${abnormalCount > 0 ? 'badge-high' : 'badge-normal'}">${abnormalCount} Abnormal</span>
            <span class="badge badge-warning">${DATA.lab_name}</span>
        `;
    }
    
    const exportBtn = document.getElementById('dash-export-btn');
    if(exportBtn && DATA.id) {
        exportBtn.href = '/export/pdf/' + DATA.id;
        exportBtn.style.display = 'flex';
    }
  }

  // Family Vault Insights
  const dashFamily = document.getElementById('dash-family');
  if (dashFamily && typeof window.LIVE_FAMILY !== 'undefined') {
    dashFamily.innerHTML = window.LIVE_FAMILY.map(m => `
      <div class="family-member" style="cursor: pointer; ${m.selected ? 'border: 2px solid ' + m.color + ';' : ''}" onclick="window.location.href='/dashboard?patient=${encodeURIComponent(m.name)}'">
        <div class="avatar avatar-lg" style="background:${m.color};">${m.initial}</div>
        <div class="family-info" style="flex: 1;">
          <div class="family-name" style="display: flex; justify-content: space-between; align-items: center;">
            ${m.name}
            ${!m.is_primary ? `
            <form action="/delete_patient" method="POST" style="margin:0;" onsubmit="return confirm('Are you sure you want to delete all reports for ${m.name}? This cannot be undone.');">
              <input type="hidden" name="patient_name" value="${m.name}">
              <button type="submit" class="btn btn-ghost" style="padding: 2px 6px; font-size: 10px; color: var(--danger); border: 1px solid var(--danger);" onclick="event.stopPropagation();">🗑 Delete</button>
            </form>
            ` : ''}
          </div>
          <div class="family-meta">${m.age}y · ${m.gender}</div>
          ${m.conditions ? `<div class="family-cond">⚠ ${m.conditions}</div>` : ''}
          <div class="family-score" style="color:${m.color};">${m.score}/100 · ${m.reports} reports</div>
        </div>
      </div>
    `).join('');
    
    // Also render top tabs
    const tabsContainer = document.getElementById('dash-family-tabs');
    if(tabsContainer) {
      tabsContainer.innerHTML = window.LIVE_FAMILY.map(m => `
        <button class="btn btn-sm ${m.selected ? 'btn-primary' : 'btn-secondary'}" onclick="window.location.href='/dashboard?patient=${encodeURIComponent(m.name)}'" style="border-radius: 20px; padding: 6px 16px;">
          <div class="avatar avatar-sm" style="background:${m.color}; width: 20px; height: 20px; font-size: 10px; margin-right: 6px;">${m.initial}</div>
          ${m.name}
        </button>
      `).join('');
    }
  }

  // ML Risk
  const dashRisk = document.getElementById('dash-risk');
  if (dashRisk && typeof window.LIVE_RISK !== 'undefined') {
    const r = window.LIVE_RISK;
    if (r.status === 'insufficient_data') {
      dashRisk.innerHTML = `<div style="padding: 16px; font-size: 13px; color: var(--text-muted); text-align: center; border: 1px dashed var(--border); border-radius: 8px;">📊 ${r.message}</div>`;
    } else if (r.status === 'success') {
      const p = r.predictions[0];
      dashRisk.innerHTML = `
        <div style="display: flex; gap: 16px; align-items: stretch; background: var(--bg); padding: 16px; border-radius: 8px; border-left: 3px solid var(--${p.color});">
          <div style="flex-shrink: 0; display: flex; flex-direction: column; justify-content: center; align-items: center; background: var(--white); padding: 12px; border-radius: 6px; border: 1px solid var(--border); min-width: 90px;">
            <div style="font-size: 10px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; text-align: center;">${p.disease}</div>
            <div style="font-family: 'Sora', sans-serif; font-size: 24px; font-weight: 800; color: var(--${p.color});">${p.score}%</div>
            <div style="font-size: 10px; font-weight: 600; color: var(--${p.color});">${p.level} Risk</div>
          </div>
          <div style="display: flex; flex-direction: column; justify-content: center;">
            <div style="font-size: 13px; color: var(--text); font-weight: 500; margin-bottom: 6px;">${p.advice}</div>
            <div style="display: flex; gap: 12px; font-size: 11px;">
              <span style="background: white; padding: 2px 8px; border-radius: 4px; border: 1px solid var(--border);">Glucose: <strong style="text-transform: capitalize;">${p.trends.glucose}</strong></span>
              <span style="background: white; padding: 2px 8px; border-radius: 4px; border: 1px solid var(--border);">HbA1c: <strong style="text-transform: capitalize;">${p.trends.hba1c}</strong></span>
            </div>
          </div>
        </div>
      `;
    }
  }

})();
