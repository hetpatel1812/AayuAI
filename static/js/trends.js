/**
 * Aayu AI — Trends JS
 */
(function() {
  if (typeof window.LIVE_HISTORY === 'undefined') return;
  const HISTORY = window.LIVE_HISTORY;

  // Check if enough data
  if (HISTORY.reports.length < 2) {
      document.querySelector('.dash-body').innerHTML = `
        <div style="grid-column: 1 / -1; padding: 60px 40px; text-align: center; color: var(--text-dim); background: var(--bg-card); border: 1px solid rgba(255,255,255,0.1); border-radius: 16px;">
          <h3 style="margin-bottom:10px; font-family: 'Outfit'; color: var(--text-primary);">Not enough data for trends</h3>
          <p>You need to upload at least 2 blood test reports to unlock longitudinal trend charts.</p>
          <a href="/upload" class="btn btn-primary" style="margin-top:20px; display:inline-block;">Upload Another Report</a>
        </div>
      `;
      const sidebar = document.querySelector('.dash-sidebar');
      if (sidebar) sidebar.style.display = 'none';
      return;
  }

  // Build dynamic trends object
  const trendsData = {};
  const allTestNames = new Set();
  HISTORY.reports.forEach(r => Object.keys(r.params).forEach(k => allTestNames.add(k)));

  const colors = ['#3B82F6', '#EF4444', '#8B5CF6', '#F59E0B', '#10B981', '#EAB308', '#06B6D4'];
  let cIdx = 0;

  allTestNames.forEach(testName => {
      // Find a report that has this test to get units/refs
      const refReport = HISTORY.reports.find(r => r.params[testName]);
      if (!refReport) return;
      const paramRef = refReport.params[testName];
      
      const dataPoints = HISTORY.reports.map(r => {
          return r.params[testName] ? r.params[testName].value : null;
      });
      
      // Only include if present in multiple reports
      if (dataPoints.filter(d => d !== null).length > 1) {
          trendsData[testName] = {
              data: dataPoints,
              color: colors[cIdx % colors.length],
              unit: paramRef.unit,
              refLow: paramRef.refLow,
              refHigh: paramRef.refHigh
          };
          cIdx++;
      }
  });

  let tChart = null, mChart = null;
  const chartDefaults = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: {
      x: { grid: { color: 'rgba(15,23,42,0.06)' }, ticks: { font: { size: 11 }, color: '#64748B' } },
      y: { grid: { color: 'rgba(15,23,42,0.06)' }, ticks: { font: { size: 11 }, color: '#64748B' } }
    }
  };

  // Build parameter buttons
  const trendBtns = document.getElementById('trend-btns');
  if (trendBtns) {
    const keys = Object.keys(trendsData);
    trendBtns.innerHTML = keys.map((k, i) =>
      `<button class="pill ${i === 0 ? 'active' : ''}" data-key="${k}">${k}</button>`
    ).join('');

    document.querySelectorAll('#trend-btns .pill').forEach(btn => {
      btn.addEventListener('click', () => {
        document.querySelectorAll('#trend-btns .pill').forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
        renderTrend(btn.dataset.key);
      });
    });
  }

  function renderTrend(key) {
    const t = trendsData[key];
    if (!t) return;
    
    document.getElementById('trend-title').textContent = key + ' Trend';
    document.getElementById('trend-range').textContent = (t.refLow && t.refHigh) ? 'Normal: ' + t.refLow + '–' + t.refHigh + ' ' + t.unit : t.refHigh ? 'Normal: < ' + t.refHigh + ' ' + t.unit : '';

    // Data cards
    document.getElementById('trend-cards').innerHTML = HISTORY.months.map((m, i) => {
      const v = t.data[i];
      if (v === null) return '';
      
      let st = 'NORMAL';
      if (t.refHigh && v > parseFloat(t.refHigh)) st = 'HIGH';
      if (t.refLow && v < parseFloat(t.refLow)) st = 'LOW';
      
      const col = st === 'HIGH' ? '#EF4444' : st === 'LOW' ? '#60A5FA' : '#10B981';
      
      // Find previous valid value
      let prev = null;
      for (let j = i - 1; j >= 0; j--) {
          if (t.data[j] !== null) { prev = t.data[j]; break; }
      }
      
      return `<div class="glass-card--solid glass-card--no-hover trend-card" style="padding:12px 14px;">
        <div class="tc-month">${m}</div>
        <div class="tc-value" style="color:${col};">${v}<span class="tc-unit">${t.unit}</span></div>
        <div style="margin-top:4px;">${statusBadge(st)}</div>
        ${prev !== null ? `<div class="tc-change">${v > prev ? '↑' : '↓'} ${Math.abs(v - prev).toFixed(1)} from prev</div>` : ''}
      </div>`;
    }).join('');

    // Main chart
    if (tChart) tChart.destroy();
    const trendChartEl = document.getElementById('trend-chart');
    if (trendChartEl) {
      tChart = new Chart(trendChartEl, {
        type: 'line',
        data: {
          labels: HISTORY.months,
          datasets: [{
            label: key, data: t.data, borderColor: t.color,
            backgroundColor: t.color + '22', borderWidth: 2.5,
            pointBackgroundColor: t.color, pointRadius: 5, fill: true, tension: 0.3,
            spanGaps: true
          }]
        },
        options: chartDefaults
      });
    }
  }

  // Multi chart
  function renderMulti() {
    const datasets = Object.entries(trendsData).map(([k, t]) => ({
      label: k, data: t.data, borderColor: t.color,
      borderWidth: 2, pointRadius: 3, fill: false, tension: 0.3, spanGaps: true
    }));

    if (mChart) mChart.destroy();
    const multiChartEl = document.getElementById('multi-chart');
    if (multiChartEl) {
      mChart = new Chart(multiChartEl, {
        type: 'line',
        data: { labels: HISTORY.months, datasets },
        options: {
          ...chartDefaults,
          plugins: { legend: { position: 'bottom', labels: { font: { size: 11 }, boxWidth: 12, color: '#334155' } } }
        }
      });
    }
  }

  if (document.getElementById('trend-chart')) {
    const firstKey = Object.keys(trendsData)[0];
    if (firstKey) {
        renderTrend(firstKey);
        renderMulti();
    }
  }
})();
