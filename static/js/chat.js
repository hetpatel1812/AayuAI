/**
 * Aayu AI — Chat JS
 */
(function() {
  if (typeof DEMO === 'undefined') return;

  const chatWindow = document.getElementById('chat-window');
  const chatInput = document.getElementById('chat-input');
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

  function getResponse(msg) {
    const m = msg.toLowerCase();
    const r = DEMO.chatResponses;
    if (m.includes('hemoglobin') || m.includes('anemia') || m.includes('iron')) return r.hemoglobin;
    if (m.includes('glucose') || m.includes('sugar') || m.includes('diabetes') || m.includes('hba1c')) return r.glucose;
    if (m.includes('tsh') || m.includes('thyroid')) return r.tsh;
    if (m.includes('vitamin') || m.includes('vit d')) return r.vitamin;
    if (m.includes('uric') || m.includes('gout')) return r.uric;
    return r.default;
  }

  function sendMessage() {
    const msg = chatInput.value.trim();
    if (!msg) return;
    addMessage('user', msg);
    chatInput.value = '';
    showTyping();
    setTimeout(() => {
      removeTyping();
      addMessage('ai', getResponse(msg));
    }, 1200);
  }

  // Initial message
  addMessage('ai', "Hi there 👋 I'm Aayu — your health AI. I have full context of your July 2024 report (20 parameters, 9 abnormal). Ask me anything about your results or what to do next.");

  // Suggestions
  const suggestions = [
    'Why is my TSH elevated?',
    'Explain my glucose levels',
    'What helps low Vitamin D?',
    'Is my hemoglobin dangerous?',
    'High uric acid — what to eat?'
  ];

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

  // Send button
  const chatSendBtn = document.getElementById('chat-send');
  if (chatSendBtn) {
    chatSendBtn.addEventListener('click', sendMessage);
  }
  
  chatInput.addEventListener('keydown', e => { 
    if (e.key === 'Enter') sendMessage(); 
  });
})();
