/**
 * Aayu AI — Family Vault JS
 */
(function() {
  if (typeof window.LIVE_FAMILY === 'undefined') return;
  const FAM_DATA = window.LIVE_FAMILY;

  let selectedIdx = null;

  // Family cards
  const famGrid = document.getElementById('fam-grid');
  if (famGrid) {
    famGrid.innerHTML = FAM_DATA.map((m, i) => `
      <div class="fam-card" id="fc-${i}" data-idx="${i}">
        <div class="fam-top">
          <div class="avatar avatar-xl" style="background:${m.color};">${m.initial}</div>
          <div style="flex: 1;">
            <div class="fam-name" style="display: flex; justify-content: space-between; align-items: center;">
              ${m.name}
              ${!m.is_primary ? `
              <form action="/delete_patient" method="POST" style="margin:0;" onsubmit="return confirm('Are you sure you want to delete all reports for ${m.name}? This cannot be undone.');">
                <input type="hidden" name="patient_name" value="${m.name}">
                <button type="submit" class="btn btn-ghost" style="padding: 2px 6px; font-size: 10px; color: var(--danger); border: 1px solid var(--danger);" onclick="event.stopPropagation();">🗑 Delete</button>
              </form>
              ` : ''}
            </div>
            <div class="fam-meta">${m.age}y · ${m.gender}</div>
            ${m.conditions ? `<div class="fam-cond">⚠ ${m.conditions}</div>` : ''}
          </div>
        </div>
        <div class="fam-stats">
          <div class="fam-stat">
            <div class="fam-stat-value" style="color:${scoreColor(m.score)};">${m.score}<span style="font-size:9px; color:var(--text-dim);">/100</span></div>
            <div class="fam-stat-label">Score</div>
          </div>
          <div class="fam-stat">
            <div class="fam-stat-value" style="color:var(--accent-blue);">${m.reports}</div>
            <div class="fam-stat-label">Reports</div>
          </div>
          <div class="fam-stat">
            <div class="fam-stat-value" style="color:var(--text-muted); font-size:11px;">${m.lastReport}</div>
            <div class="fam-stat-label">Last</div>
          </div>
        </div>
        <div class="fam-concern">⚠ ${m.concern}</div>
        <div class="fam-actions">
          <button class="fam-action-btn">View Reports</button>
          <button class="fam-action-btn">Upload New</button>
          <button class="fam-action-btn">View Trends</button>
          <button class="fam-action-btn">Compare</button>
        </div>
      </div>
    `).join('');

    // Card selection
    document.querySelectorAll('.fam-card').forEach(card => {
      card.addEventListener('click', () => {
        const idx = parseInt(card.dataset.idx);
        document.querySelectorAll('.fam-card').forEach(c => c.classList.remove('selected'));
        if (selectedIdx === idx) { selectedIdx = null; }
        else { card.classList.add('selected'); selectedIdx = idx; }
      });
    });
  }

  // Summary table
  const famTbody = document.getElementById('fam-tbody');
  if (famTbody) {
    famTbody.innerHTML = FAM_DATA.map(m => `
      <tr>
        <td><div style="display:flex; align-items:center; gap:10px;">
          <div class="avatar avatar-sm" style="background:${m.color};">${m.initial}</div>
          <span style="font-weight:600; color:var(--text-primary);">${m.name}</span>
        </div></td>
        <td>${m.age}y</td>
        <td>${m.lastReport}</td>
        <td><span style="font-size:18px; font-weight:800; color:${scoreColor(m.score)};">${m.score}</span><span style="font-size:10px; color:var(--text-dim);">/100</span></td>
        <td style="color:var(--status-high);">${m.concern}</td>
        <td>
          <div style="display: flex; gap: 8px;">
            <button class="btn btn-sm btn-secondary" onclick="window.location.href='/dashboard?patient=${encodeURIComponent(m.name)}'">Dashboard</button>
            ${!m.is_primary ? `
            <form action="/delete_patient" method="POST" style="margin:0;" onsubmit="return confirm('Are you sure you want to delete all reports for ${m.name}? This cannot be undone.');">
              <input type="hidden" name="patient_name" value="${m.name}">
              <button type="submit" class="btn btn-sm btn-ghost" style="color: var(--danger); border: 1px solid var(--danger);">Delete</button>
            </form>
            ` : ''}
          </div>
        </td>
      </tr>
    `).join('');
  }
})();
