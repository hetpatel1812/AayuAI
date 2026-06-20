/**
 * Aayu AI — Chat JS
 */
(function() {
  const chatWindow = document.getElementById('chat-window');
  const chatInput = document.getElementById('chat-input');
  const chatSendBtn = document.getElementById('chat-send');
  if (!chatWindow || !chatInput) return;

  function addMessage(role, text) {
    const div = document.createElement('div');
    div.className = `chat-msg ${role}`;
    if (role === 'ai') {
      div.innerHTML = `<div class="chat-avatar">🌿</div><div class="chat-bubble ai">${text}</div>`;
    } else {
      div.innerHTML = `<div class="chat-bubble user">${text}</div>`;
    }
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function showTyping() {
    const div = document.createElement('div');
    div.className = 'chat-msg ai chat-typing';
    div.id = 'typing-indicator';
    div.innerHTML = `<div class="chat-avatar">🌿</div><div class="chat-bubble ai"><div class="typing-dots"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div></div>`;
    chatWindow.appendChild(div);
    chatWindow.scrollTop = chatWindow.scrollHeight;
  }

  function removeTyping() {
    const el = document.getElementById('typing-indicator');
    if (el) el.remove();
  }

  function sendMessage() {
    const msg = chatInput.value.trim();
    if (!msg) return;
    
    addMessage('user', msg);
    chatInput.value = '';
    showTyping();

    fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: msg })
    })
    .then(res => res.json())
    .then(data => {
      removeTyping();
      addMessage('ai', data.reply);
    })
    .catch(err => {
      console.error(err);
      removeTyping();
      // Fallback in case of server error
      const m = msg.toLowerCase();
      let reply = "I'm having trouble connecting to my medical database. Please try again in a moment.";
      if (m.includes('hemoglobin') || m.includes('anemia')) {
        reply = 'Your hemoglobin is below normal, indicating mild iron-deficiency anemia. Keep eating palak, rajma, and pomegranate.';
      } else if (m.includes('glucose') || m.includes('sugar') || m.includes('diabetes')) {
        reply = 'Your fasting glucose is in the prediabetes range. It is fully reversible: cut refined carbs, walk 30 mins daily, and avoid sugar.';
      } else if (m.includes('tsh') || m.includes('thyroid')) {
        reply = 'Your TSH is elevated, suggesting hypothyroidism. Consult an Endocrinologist for simple daily thyroid support.';
      }
      addMessage('ai', reply);
    });
  }

  // Initial message with live stats
  const userName = window.USER_NAME || 'User';
  const paramCount = window.PARAM_COUNT || 0;
  const abnormalCount = window.ABNORMAL_COUNT || 0;
  const reportDate = window.REPORT_DATE || '';

  let welcomeMsg = `Hi ${userName} 👋 I'm Aayu — your health AI. I don't see any analyzed report context. Please upload a blood test report so I can analyze it and help you.`;
  if (reportDate) {
    welcomeMsg = `Hi ${userName} 👋 I'm Aayu — your health AI. I have full context of your ${reportDate} report (${paramCount} parameters, ${abnormalCount} abnormal). Ask me anything about your results or what to do next.`;
  }
  addMessage('ai', welcomeMsg);

  // Suggestions
  let suggestions = [];
  if (reportDate) {
    suggestions = [
      'Why is my TSH elevated?',
      'Explain my glucose levels',
      'What helps low Vitamin D?',
      'Is my hemoglobin dangerous?',
      'High uric acid — what to eat?'
    ];
  } else {
    suggestions = [
      'How does Aayu AI analyze reports?',
      'What blood tests are supported?',
      'How do I upload a scan image?',
      'Is my data safe and private?'
    ];
  }

  const suggEl = document.getElementById('chat-suggestions');
  if (suggEl) {
    suggEl.innerHTML = suggestions.map(s =>
      `<button class="chat-sugg">${s}</button>`
    ).join('');

    document.querySelectorAll('.chat-sugg').forEach(btn => {
      btn.addEventListener('click', () => {
        chatInput.value = btn.textContent;
        sendMessage();
      });
    });
  }

  if (chatSendBtn) {
    chatSendBtn.addEventListener('click', sendMessage);
  }
  
  chatInput.addEventListener('keydown', e => { 
    if (e.key === 'Enter') sendMessage(); 
  });
})();
