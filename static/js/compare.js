/**
 * Aayu AI — Compare Reports JS
 */
(function() {
  if (typeof window.LIVE_HISTORY === 'undefined') return;
  const HISTORY = window.LIVE_HISTORY;

  if (HISTORY.reports.length < 2) {
      const container = document.querySelector('.compare-cards') || document.querySelector('.app-main');
      if (container) {
          container.innerHTML = `
            <div style="grid-column: 1 / -1; padding: 60px 40px; text-align: center; color: var(--text-dim); background: var(--bg-card); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px;">
              <h3 style="margin-bottom:10px; font-family: 'Outfit'; color: var(--text-primary);">Not enough data for comparison</h3>
              <p>You need to upload at least 2 blood test reports to compare them side-by-side.</p>
              <a href="/upload" class="btn btn-primary" style="margin-top:20px; display:inline-block;">Upload Another Report</a>
            </div>
          `;
      }
      return;
  }

  // Get the last two reports
  const r2 = HISTORY.reports[HISTORY.reports.length - 1];
  const r1 = HISTORY.reports[HISTORY.reports.length - 2];

  // Update header titles
  const headerEls = document.querySelectorAll('.page-header-left p');
  if(headerEls.length > 0) {
      headerEls[0].textContent = `Comparing ${r1.date} vs ${r2.date}`;
  }

  if (document.getElementById('cmp-ring-1')) {
    drawHealthRing('cmp-ring-1', r1.score, 70);
  }
  if (document.getElementById('cmp-ring-2')) {
    drawHealthRing('cmp-ring-2', r2.score, 70);
  }

  // Find overlapping parameters
  const comparison = [];
  Object.keys(r1.params).forEach(k => {
      if (r2.params[k]) {
          const v1 = r1.params[k].value;
          const v2 = r2.params[k].value;
          
          let trend = 'same';
          let isImp = false;
          
          if (v1 !== v2) {
             const diff = v2 - v1;
             // Assume lower is better if high status, higher is better if low status
             const stat1 = r1.params[k].status;
             const stat2 = r2.params[k].status;
             
             if (stat2 === 'NORMAL' && stat1 !== 'NORMAL') isImp = true;
             else if (stat1 === 'NORMAL' && stat2 !== 'NORMAL') isImp = false;
             else if (stat2 === 'HIGH' && diff < 0) isImp = true;
             else if (stat2 === 'LOW' && diff > 0) isImp = true;
             else if (stat2 === 'NORMAL') {
                 // Even if both normal, we can just say improved if it moved closer to middle
                 isImp = true;
             }
             trend = isImp ? 'improved' : 'worsened';
          }
          
          comparison.push({
              test: k,
              v1: v1,
              v2: v2,
              unit: r2.params[k].unit,
              s1: r1.params[k].status,
              s2: r2.params[k].status,
              trend: trend
          });
      }
  });

  const cmpTbody = document.getElementById('cmp-tbody');
  if (cmpTbody) {
    if (comparison.length === 0) {
        cmpTbody.innerHTML = `<tr><td colspan="5" style="text-align:center; padding: 20px; color: var(--text-dim);">No overlapping tests found between these two reports.</td></tr>`;
        return;
    }

    cmpTbody.innerHTML = comparison.map(r => {
      const diff = (r.v2 - r.v1).toFixed(1);
      const pct = r.v1 !== 0 ? ((Math.abs(r.v2 - r.v1) / r.v1) * 100).toFixed(1) : '0.0';
      const imp = r.trend === 'improved';
      const rowCls = imp || r.trend === 'same' ? '' : 'row-high';
      
      let trendText = r.trend === 'same' ? '— Same' : (imp ? '↑ Improved' : '↓ Worsened');
      let trendBadgeClass = r.trend === 'same' ? 'trend-improved' : (imp ? 'trend-improved' : 'trend-worsened');
      if(r.trend === 'same') {
          trendBadgeClass = '';
      }
      
      return `<tr class="${rowCls}">
        <td style="font-weight:600; color:var(--text-primary);">${r.test} <span style="font-size:10px; color:var(--text-dim);">(${r.unit})</span></td>
        <td><span style="font-size:14px; font-weight:700; color:var(--text-dim); margin-right:6px;">${r.v1}</span>${statusBadge(r.s1)}</td>
        <td><span style="font-size:14px; font-weight:700; color:var(--text-primary); margin-right:6px;">${r.v2}</span>${statusBadge(r.s2)}</td>
        <td style="font-weight:700; color:${imp || r.trend==='same' ? 'var(--status-normal)' : 'var(--status-high)'};">${diff > 0 ? '+' : ''}${diff} (${pct}%)</td>
        <td><span class="trend-badge ${trendBadgeClass}">${trendText}</span></td>
      </tr>`;
    }).join('');
  }
})();
