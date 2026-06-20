/**
 * Aayu AI — Upload Page JavaScript
 */
(function() {
  let selectedMode = null;

  // Mode selection
  document.querySelectorAll('.upload-mode').forEach(card => {
    card.addEventListener('click', () => {
      document.querySelectorAll('.upload-mode').forEach(c => c.classList.remove('selected'));
      card.classList.add('selected');
      selectedMode = card.dataset.mode;
      document.getElementById('mode-input').value = selectedMode;

      const dz = document.getElementById('dropzone');
      if(dz) dz.classList.add('ready');
      
      const icons = {pdf: '📄', scan: '🖨️', phone: '📱'};
      const titles = {pdf: 'Ready for PDF upload', scan: 'Ready for scanned image', phone: 'Ready for phone camera photo'};
      const descs = {pdf: 'Drag and drop your PDF here or click to browse.', scan: 'Clear flat scan image required.', phone: 'Any photo — tilted, shadowed, blurry all OK.'};
      const tools = {pdf: 'pdfplumber', scan: 'EasyOCR', phone: 'Gemini Vision'};
      
      const dzIcon = document.getElementById('dz-icon');
      if(dzIcon) dzIcon.textContent = icons[selectedMode];
      
      const dzTitle = document.getElementById('dz-title');
      if(dzTitle) dzTitle.textContent = titles[selectedMode];
      
      const dzDesc = document.getElementById('dz-desc');
      if(dzDesc) dzDesc.textContent = descs[selectedMode];
      
      const btn = document.getElementById('btn-analyze');
      if(btn) {
        btn.textContent = '→ Analyze with ' + tools[selectedMode];
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.className = 'btn btn-primary';
      }
    });
  });

  // Member pills
  document.querySelectorAll('.member-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.member-pill').forEach(p => { 
        p.classList.remove('active'); 
        p.style.background = '#64748B'; 
      });
      pill.classList.add('active');
      pill.style.background = '#00D4AA';
    });
  });

  // Language pills
  document.querySelectorAll('.lang-pill').forEach(pill => {
    pill.addEventListener('click', () => {
      document.querySelectorAll('.lang-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const langMap = {'English': 'en', 'हिंदी': 'hi', 'ગુજ': 'gu'};
      document.getElementById('lang-input').value = langMap[pill.textContent] || 'en';
    });
  });

  // File selection
  const fileInput = document.getElementById('file-input');
  if (fileInput) {
    fileInput.addEventListener('change', (e) => {
      if (e.target.files.length > 0) {
        document.getElementById('file-name-display').textContent = 'Selected: ' + e.target.files[0].name;
      }
    });
  }

  // Analyze button
  const btnAnalyze = document.getElementById('btn-analyze');
  if (btnAnalyze) {
    btnAnalyze.addEventListener('click', startProcessing);
  }

  // Upload again
  const btnUploadAgain = document.getElementById('btn-upload-again');
  if (btnUploadAgain) {
    btnUploadAgain.addEventListener('click', () => {
      document.getElementById('upload-done').classList.add('hidden');
      document.getElementById('upload-main').classList.remove('hidden');
    });
  }

  function startProcessing() {
    if (!selectedMode) return;
    const file = document.getElementById('file-input').files[0];
    if (!file) {
      alert("Please select a file first.");
      return;
    }

    document.getElementById('upload-main').classList.add('hidden');
    document.getElementById('upload-proc').classList.remove('hidden');

    const subs = {pdf: 'Using pdfplumber to extract PDF text...', scan: 'Running OpenCV + EasyOCR...', phone: 'Sending to Gemini 1.5 Flash Vision API...'};
    document.getElementById('proc-sub').textContent = subs[selectedMode];

    const steps = [
      'Detecting file format...',
      selectedMode === 'phone' ? 'Sending to Gemini Vision API...' : selectedMode === 'pdf' ? 'Extracting text via pdfplumber...' : 'Running OpenCV + EasyOCR...',
      'Parsing 20 blood parameters...',
      'Classifying NORMAL / HIGH / LOW / CRITICAL...',
      'Generating explanations via Groq (Llama 3.3 70B)...',
      'Building health score and diet tips...',
      'Analysis complete!'
    ];

    const stepsEl = document.getElementById('proc-steps');
    stepsEl.innerHTML = steps.map((s, i) => `
      <div class="step-item" id="step-${i}">
        <div class="step-dot" id="dot-${i}">${i + 1}</div>
        <span class="step-text" id="stxt-${i}">${s}</span>
      </div>
    `).join('');

    // Fake progress UI while real fetch is happening
    let cur = 0;
    const total = steps.length - 1;
    let timer = setInterval(() => {
      if (cur < total - 1) { // Stop at second to last until done
        updateStep(cur);
        cur++;
      }
    }, 1500);

    function updateStep(c) {
      if (c > 0) {
        const prevDot = document.getElementById('dot-' + (c - 1));
        if (prevDot) { prevDot.className = 'step-dot done'; prevDot.textContent = '✓'; }
      }
      const step = document.getElementById('step-' + c);
      const dot = document.getElementById('dot-' + c);
      if (step) step.classList.add('active');
      if (dot) { dot.className = 'step-dot running'; dot.textContent = '⟳'; }
      
      const pct = Math.min(95, Math.round((c / total) * 100));
      document.getElementById('proc-pct').textContent = pct + '%';
      document.getElementById('proc-fill').style.width = pct + '%';
    }

    const formData = new FormData(document.getElementById('upload-form'));

    fetch('/upload', {
      method: 'POST',
      body: formData
    })
    .then(res => res.json())
    .then(data => {
      clearInterval(timer);
      if (data.error) {
        alert("Error: " + data.error);
        document.getElementById('upload-proc').classList.add('hidden');
        document.getElementById('upload-main').classList.remove('hidden');
      } else {
        // Finish progress
        updateStep(total - 1);
        setTimeout(() => {
          updateStep(total);
          document.getElementById('proc-pct').textContent = '100%';
          document.getElementById('proc-fill').style.width = '100%';
          const lastDot = document.getElementById('dot-' + total);
          if (lastDot) { lastDot.className = 'step-dot done'; lastDot.textContent = '✓'; }
          
          setTimeout(() => {
            // Redirect to results with the real report ID
            window.location.href = '/results/' + data.report_id;
          }, 800);
        }, 500);
      }
    })
    .catch(err => {
      clearInterval(timer);
      alert("Upload failed. Check console.");
      console.error(err);
      document.getElementById('upload-proc').classList.add('hidden');
      document.getElementById('upload-main').classList.remove('hidden');
    });
  }
})();
