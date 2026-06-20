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
                <div class="ai-tag">🤖 AI Explanation</div>
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

  // Download PDF Report
  window.downloadReportPDF = function() {
    const DATA = window.LIVE_DATA;
    if (!DATA || !DATA.id) return;

    const abnormal = DATA.params.filter(p => p.status !== 'NORMAL');
    const categories = ['CBC', 'KFT', 'LFT', 'Glucose', 'Lipid', 'Thyroid', 'Vitamins', 'Other'];
    
    // Sub-scores format for Page 1
    const subScoresHtml = categories.map(cat => {
      const catParams = DATA.params.filter(p => p.cat === cat);
      if (catParams.length === 0) return '';
      const normalCount = catParams.filter(p => p.status === 'NORMAL').length;
      const score = Math.round((normalCount / catParams.length) * 100);
      let col = '#10B981'; // Green
      if (score < 50) col = '#EF4444'; // Red
      else if (score < 75) col = '#F59E0B'; // Amber
      return `
        <div style="margin-bottom: 8px;">
          <div style="display:flex; justify-content:space-between; font-size:11px; margin-bottom:2px;">
            <span style="color:#64748B; font-weight: 600;">${cat} Panel</span>
            <span style="font-weight:700; color:${col};">${score}%</span>
          </div>
          <div style="height:5px; background:#F1F5F9; border-radius:2px; overflow:hidden;">
            <div style="width:${score}%; height:100%; background:${col};"></div>
          </div>
        </div>
      `;
    }).join('');

    // Format abnormal list for Page 1 summary
    const abnormalSummaryHtml = abnormal.length > 0 ? abnormal.map(p => {
      const color = p.status === 'HIGH' ? '#EF4444' : '#3B82F6';
      return `<span style="display:inline-block; padding: 4px 8px; background:#FFF5F5; border:1px solid #FEE2E2; border-radius:4px; font-size:10.5px; margin-right:6px; margin-bottom:6px; color:${color}; font-weight:700;">${p.test}: ${p.value} ${p.unit} (${p.status})</span>`;
    }).join('') : '<span style="color:#10B981; font-weight:600; font-size:12px;">All parameters are normal! 🎉</span>';

    // Filter active categories
    const activeCats = categories.filter(cat => DATA.params.filter(p => p.cat === cat).length > 0);
    
    let categoriesDetailsHtml = '';
    activeCats.forEach((cat, idx) => {
      const catParams = DATA.params.filter(p => p.cat === cat);
      
      categoriesDetailsHtml += `
        <div style="margin-bottom: 24px;">
          <div style="font-size:14px; font-weight:800; color:#1E293B; border-bottom:2px solid #00D4AA; padding-bottom:6px; margin-bottom:12px; text-transform:uppercase; letter-spacing:0.5px; display:flex; justify-content:space-between; align-items:center; page-break-after: avoid;">
            <span>${cat} Panel</span>
            <span style="font-size:10px; color:#94A3B8; font-weight:500;">${catParams.length} parameters</span>
          </div>
          
          ${catParams.map(p => {
            const color = p.status === 'HIGH' ? '#EF4444' : p.status === 'LOW' ? '#3B82F6' : '#10B981';
            const range = (p.refLow && p.refHigh) ? `${p.refLow}–${p.refHigh}` : p.refHigh ? `< ${p.refHigh}` : '-';
            const statusLabel = p.status === 'HIGH' ? 'High' : p.status === 'LOW' ? 'Low' : 'Normal';
            return `
              <div style="padding: 12px 16px; background:#F8FAFC; border-left: 4px solid ${color}; border-radius: 6px; margin-bottom: 12px; font-size: 11.5px; page-break-inside: avoid; text-align: left; box-shadow: 0 1px 2px rgba(0,0,0,0.01);">
                <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:6px;">
                  <strong style="color:#1E293B; font-size:13px;">${p.test}</strong>
                  <div style="font-weight:700; color:${color}; font-size:12.5px;">
                    ${p.value} <span style="font-size:9.5px; color:#94A3B8; font-weight:400; margin-right:8px;">${p.unit}</span>
                    <span style="font-size:10px; text-transform:uppercase; letter-spacing:0.5px;">[${statusLabel}]</span>
                  </div>
                </div>
                <div style="font-size:10px; color:#64748B; margin-bottom:6px;">Expected Range: ${range} ${p.unit}</div>
                <div style="color:#334155; line-height:1.6; margin-bottom:6px;">🤖 **AI:** ${p.explanation || 'No explanation available.'}</div>
                ${p.diet ? `<div style="color:#0ea5e9; font-weight:600; line-height:1.6; background: rgba(14,165,233,0.04); padding: 6px 10px; border-radius: 4px; margin-top: 4px;">🍛 **Diet:** ${p.diet}</div>` : ''}
              </div>
            `;
          }).join('')}
        </div>
      `;
    });

    const reportHtml = `
      <div style="font-family:'Outfit', 'Inter', system-ui, sans-serif; color:#1E293B; background:#fff; width:210mm; padding: 20mm 15mm; box-sizing:border-box; margin:0 auto; text-align: left;">
        
        <!-- PAGE 1: EXECUTIVE SUMMARY -->
        <div style="page-break-after: always; height: 255mm; display: flex; flex-direction: column; justify-content: space-between; box-sizing: border-box;">
          <div>
            <!-- Header -->
            <div style="display:flex; justify-content:space-between; align-items:center; border-bottom:3px solid #00D4AA; padding-bottom:15px; margin-bottom:20px;">
              <div>
                <div style="font-size:26px; font-weight:900; color:#1E293B; letter-spacing:-0.5px;">Aayu <span style="color:#00D4AA;">AI</span></div>
                <div style="font-size:10px; color:#64748B; letter-spacing:1px; text-transform:uppercase; font-weight:700;">Life Intelligence Report Summary</div>
              </div>
              <div style="text-align:right;">
                <div style="font-size:12px; font-weight:700; color:#1E293B;">Report Date: ${DATA.test_date}</div>
                <div style="font-size:10px; color:#94A3B8;">Diagnostic Analysis ID: #${DATA.id}</div>
              </div>
            </div>

            <!-- Patient Info Box -->
            <div style="background:#F8FAFC; border:1px solid #E2E8F0; border-radius:8px; padding:16px; display:grid; grid-template-columns:1fr 1fr 1fr; gap:16px; margin-bottom:20px;">
              <div><span style="font-size:9.5px; color:#94A3B8; text-transform:uppercase; font-weight:700;">Patient Name</span><br><strong style="font-size:13.5px; color:#1E293B; font-weight:800;">${DATA.patient_name}</strong></div>
              <div><span style="font-size:9.5px; color:#94A3B8; text-transform:uppercase; font-weight:700;">Age / Gender</span><br><strong style="font-size:13.5px; color:#1E293B; font-weight:800;">${DATA.patient_age || '--'} Years / ${DATA.patient_gender || 'Unknown'}</strong></div>
              <div><span style="font-size:9.5px; color:#94A3B8; text-transform:uppercase; font-weight:700;">Source Lab</span><br><strong style="font-size:13.5px; color:#1E293B; font-weight:800;">${DATA.lab_name}</strong></div>
            </div>

            <!-- Key Metrics Grid -->
            <div style="display:grid; grid-template-columns: 210px 1fr; gap:20px; margin-bottom:24px;">
              <!-- Health Score Card -->
              <div style="border:1px solid #E2E8F0; border-radius:8px; padding:24px 20px; text-align:center; display:flex; flex-direction:column; align-items:center; justify-content:center; background:#FFF; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                <div style="font-size:11.5px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:12px; letter-spacing:0.5px;">Health Score</div>
                <div style="width:105px; height:105px; border-radius:50%; border:8px solid #F1F5F9; display:flex; flex-direction:column; align-items:center; justify-content:center; position:relative; box-sizing:border-box;">
                  <div style="width:105px; height:105px; border-radius:50%; border:8px solid ${scoreColor(DATA.health_score)}; position:absolute; top:-8px; left:-8px; clip-path: polygon(0 0, 100% 0, 100% 100%, 0% 100%); box-sizing:border-box;"></div>
                  <div style="font-size:34px; font-weight:900; color:${scoreColor(DATA.health_score)};">${DATA.health_score}</div>
                  <div style="font-size:10px; color:#94A3B8; font-weight:600; margin-top:2px;">/ 100</div>
                </div>
                <div style="font-size:11px; font-weight:700; color:${scoreColor(DATA.health_score)}; margin-top:12px; text-transform:uppercase;">
                  ${DATA.health_score >= 80 ? 'Good Health' : DATA.health_score >= 50 ? 'Needs Attention' : 'Action Required'}
                </div>
              </div>
              
              <!-- System Scores Card -->
              <div style="border:1px solid #E2E8F0; border-radius:8px; padding:16px 20px; background:#FFF; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
                <div style="font-size:11.5px; font-weight:700; color:#64748B; text-transform:uppercase; margin-bottom:12px; letter-spacing:0.5px;">System Panel Breakdown</div>
                <div style="display:grid; grid-template-columns: 1fr 1fr; gap:24px 10px;">
                  ${subScoresHtml}
                </div>
              </div>
            </div>

            <!-- Key Findings Summary -->
            <div style="border:1px solid #E2E8F0; border-radius:8px; padding:16px 20px; background:#FFF; box-shadow:0 1px 3px rgba(0,0,0,0.02);">
              <div style="font-size:12px; font-weight:700; color:#EF4444; text-transform:uppercase; margin-bottom:12px; letter-spacing:0.5px;">🚨 Summary of Abnormal Findings (${abnormal.length})</div>
              <div>
                ${abnormalSummaryHtml}
              </div>
              <div style="font-size:11px; color:#64748B; margin-top:10px; line-height:1.5;">
                Detailed biomarker explanations, AI diagnostic insights, and Indian dietary tips for all normal and abnormal parameters are provided in the following sections.
              </div>
            </div>
          </div>

          <!-- Page 1 Footer -->
          <div style="border-top:1px solid #E2E8F0; padding-top:12px; text-align:center; font-size:9px; color:#94A3B8; font-weight:500;">
            Aayu AI — Comprehensive Health Report Analysis · Page 1
          </div>
        </div>

        <!-- PAGES 2-5: PARAMETER DETAILS -->
        <div style="padding-top:10px;">
          ${categoriesDetailsHtml}
        </div>

      </div>
    `;

    // Render inside temporary wrapper
    const worker = document.createElement('div');
    worker.innerHTML = reportHtml;
    document.body.appendChild(worker);

    // PDF options focusing on keeping it up to 4-5 pages cleanly
    const opt = {
      margin:       10,
      filename:     `AayuAI_Detailed_Report_${DATA.patient_name.replace(/\s+/g, '_')}_${DATA.test_date.replace(/\s+/g, '_')}.pdf`,
      image:        { type: 'jpeg', quality: 0.98 },
      html2canvas:  { scale: 2, useCORS: true, letterRendering: true, logging: false },
      jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' },
      pagebreak:    { mode: 'css' }
    };

    // Download PDF directly
    html2pdf().set(opt).from(worker).save().then(() => {
      worker.remove();
    });
  };
})();
