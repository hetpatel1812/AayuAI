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
          <div class="empty-state-icon"><svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="opacity: 0.5;"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg></div>
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
        <span class="alert-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg></span>
        <span><strong>Action needed:</strong> ${abnormalCount} abnormal values — ${topTests}${abnormalCount > 5 ? ' and more' : ''} require attention.</span>
      `;
    } else {
      alertBanner.className = 'alert alert-success animate-fade-in-down';
      alertBanner.innerHTML = `
        <span class="alert-icon"><svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg></span>
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
      
      const iconBase = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">';
      const catIcons = {
        'CBC': iconBase + '<path d="M12 2.69l5.66 5.66a8 8 0 1 1-11.31 0z"/></svg>', // drop
        'KFT': iconBase + '<path d="M12 22a7 7 0 0 0 7-7c0-2-1-3.9-3-5.5s-3.5-4-4-6.5c-.5 2.5-2 4.9-4 6.5C6 11.1 5 13 5 15a7 7 0 0 0 7 7z"/></svg>', // droplet (kidney fluid)
        'LFT': iconBase + '<path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2v1c0 5.6-4.5 10.1-10.1 10.1v7Z"/></svg>', // leaf (liver)
        'Glucose': iconBase + '<circle cx="12" cy="12" r="10"/><path d="m4.93 4.93 4.24 4.24"/><path d="m14.83 9.17 4.24-4.24"/><path d="m14.83 14.83 4.24 4.24"/><path d="m9.17 14.83-4.24 4.24"/><circle cx="12" cy="12" r="4"/></svg>', // sun (energy/glucose)
        'Lipid': iconBase + '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>', // info/alert (cholesterol)
        'Thyroid': iconBase + '<path d="M13 2L3 14h9l-1 8 10-12h-9l1-8z"/></svg>', // zap (metabolism)
        'Vitamins': iconBase + '<rect width="16" height="6" x="4" y="9" rx="3"/><path d="M4 12h16"/></svg>', // pill
        'Other': iconBase + '<circle cx="12" cy="12" r="10"/><path d="M12 16v-4"/><path d="M12 8h.01"/></svg>' // info
      };
      const icon = catIcons[p.cat] || catIcons['Other'];
      
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
          ${m.conditions ? `<div class="family-cond" style="display: flex; align-items: center; gap: 4px;"><svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg> ${m.conditions}</div>` : ''}
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
