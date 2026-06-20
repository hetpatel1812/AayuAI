/**
 * Aayu AI — Dashboard JavaScript
 */
(function() {
  if (typeof window.LIVE_DATA === 'undefined') return;
  const DATA = window.LIVE_DATA;

  // If no report uploaded yet, show empty state
  if (!DATA.id) {
    document.querySelector('.dash-body').innerHTML = `
      <div style="grid-column: 1 / -1; padding: 40px; text-align: center; color: var(--text-dim);">
        <h3 style="margin-bottom:10px;">No reports found</h3>
        <p>Upload your first blood test report to see your dashboard insights.</p>
        <a href="/upload" class="btn btn-primary" style="margin-top:20px; display:inline-block;">Upload Report</a>
      </div>
    `;
    const alertBanner = document.querySelector('.alert-warning');
    if(alertBanner) alertBanner.style.display = 'none';
    
    // Update header
    const pageHeaderP = document.querySelector('.page-header-left p');
    if(pageHeaderP) pageHeaderP.textContent = `Family health overview · Welcome ${DATA.patient_name}`;
    
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
  const alertBanner = document.querySelector('.alert-warning');
  if (alertBanner) {
    if (abnormalCount > 0) {
      const topTests = abnormalParams.slice(0, 5).map(p => p.test).join(', ');
      alertBanner.innerHTML = `
        <span class="alert-icon">⚠️</span>
        <span><strong>Action needed:</strong> ${abnormalCount} abnormal values — ${topTests}${abnormalCount > 5 ? ' and more' : ''} require attention.</span>
      `;
    } else {
      alertBanner.className = 'alert alert-success';
      alertBanner.style.background = 'rgba(16, 185, 129, 0.1)';
      alertBanner.style.border = '1px solid rgba(16, 185, 129, 0.2)';
      alertBanner.style.color = '#047857';
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

  // Table (first 12 params)
  const dashTableBody = document.getElementById('dash-table-body');
  if (dashTableBody) {
    // Show abnormal first, then rest
    const sortedParams = [...DATA.params].sort((a,b) => (a.status==='NORMAL'?1:0) - (b.status==='NORMAL'?1:0)).slice(0, 12);
    dashTableBody.innerHTML = sortedParams.map(p => {
      const rowClass = p.status === 'HIGH' ? 'row-high' : p.status === 'LOW' ? 'row-low' : '';
      const vc = statusColor(p.status);
      const range = (p.refLow && p.refHigh) ? `${p.refLow}–${p.refHigh}` : p.refHigh ? `< ${p.refHigh}` : '-';
      return `<tr class="${rowClass}">
        <td style="font-weight:600; color:var(--text-primary);">${p.test}</td>
        <td style="font-weight:800; color:${vc};">${p.value} <span style="font-size:10px; color:var(--text-dim);">${p.unit}</span></td>
        <td>${range}</td>
        <td>${statusBadge(p.status)}</td>
      </tr>`;
    }).join('');
    
    const badgesContainer = document.querySelector('.dash-table-header div');
    if(badgesContainer) {
        badgesContainer.innerHTML = `
            <span class="badge ${abnormalCount > 0 ? 'badge-high' : 'badge-normal'}">${abnormalCount} Abnormal</span>
            <span class="badge badge-warning">${DATA.lab_name}</span>
        `;
    }
  }

  // Family
  const dashFamily = document.getElementById('dash-family');
  if (dashFamily && typeof window.LIVE_FAMILY !== 'undefined') {
    dashFamily.innerHTML = window.LIVE_FAMILY.map(m => `
      <div class="family-member">
        <div class="avatar avatar-lg" style="background:${m.color};">${m.initial}</div>
        <div class="family-info">
          <div class="family-name">${m.name}</div>
          <div class="family-meta">${m.age}y · ${m.gender === 'M' ? 'Male' : 'Female'}</div>
          ${m.conditions ? `<div class="family-cond">⚠ ${m.conditions}</div>` : ''}
          <div class="family-score" style="color:${m.color};">${m.score}/100 · ${m.reports} reports</div>
        </div>
      </div>
    `).join('');
  }

})();
