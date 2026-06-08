const buttons = document.querySelectorAll('.lang-btn');

function setLanguage(lang) {
  document.documentElement.lang = lang;

  document.querySelectorAll('[data-tr]').forEach((el) => {
    const value = lang === 'de' ? el.dataset.de : el.dataset.tr;
    if (value) el.textContent = value;
  });

  document.querySelectorAll('[data-placeholder-tr]').forEach((el) => {
    const value = lang === 'de' ? el.dataset.placeholderDe : el.dataset.placeholderTr;
    if (value) el.setAttribute('placeholder', value);
  });

  buttons.forEach(btn => btn.classList.toggle('active', btn.dataset.lang === lang));
  localStorage.setItem('siteLang', lang);
}

buttons.forEach(btn => {
  btn.addEventListener('click', () => setLanguage(btn.dataset.lang));
});

setLanguage(localStorage.getItem('siteLang') || 'tr');
document.getElementById('year').textContent = new Date().getFullYear();

const chat = document.getElementById('aiChat');
const chatToggle = document.getElementById('aiChatToggle');
const chatClose = document.getElementById('aiChatClose');
const chatForm = document.getElementById('aiChatForm');
const chatInput = document.getElementById('aiChatInput');
const chatMessages = document.getElementById('aiChatMessages');

function syncChatViewport() {
  if (!window.visualViewport) {
    document.documentElement.style.setProperty('--chat-vh', '100dvh');
    document.documentElement.style.setProperty('--chat-top', '0px');
    return;
  }

  document.documentElement.style.setProperty('--chat-vh', `${window.visualViewport.height}px`);
  document.documentElement.style.setProperty('--chat-top', `${window.visualViewport.offsetTop}px`);
}

function setChatOpen(isOpen) {
  const isMobileChat = window.matchMedia('(max-width: 520px)').matches;

  chat.classList.toggle('open', isOpen);
  document.body.classList.toggle('chat-lock', isOpen && isMobileChat);
  syncChatViewport();

  if (isOpen) {
    chatInput.focus({ preventScroll: true });
  } else {
    chatInput.blur();
  }
}

function getCurrentLanguage() {
  return localStorage.getItem('siteLang') || document.documentElement.lang || 'tr';
}

function addChatMessage(text, type = 'bot') {
  const message = document.createElement('div');
  message.className = `ai-chat-message ${type}`;
  message.textContent = text;
  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;
  return message;
}

function setChatLoading(isLoading) {
  chatInput.disabled = isLoading;
  chatForm.querySelector('button').disabled = isLoading;
}

function resizeChatInput() {
  const minHeight = window.matchMedia('(max-width: 520px)').matches ? 50 : 48;
  const maxHeight = window.matchMedia('(max-width: 520px)').matches ? 112 : 120;

  chatInput.style.height = 'auto';
  chatInput.style.height = `${Math.max(minHeight, Math.min(chatInput.scrollHeight, maxHeight))}px`;
}

chatToggle?.addEventListener('click', () => {
  setChatOpen(!chat.classList.contains('open'));
});

chatClose?.addEventListener('click', () => {
  setChatOpen(false);
});

window.visualViewport?.addEventListener('resize', syncChatViewport);
window.visualViewport?.addEventListener('scroll', syncChatViewport);
window.addEventListener('resize', () => {
  if (chat.classList.contains('open')) {
    setChatOpen(true);
  }
});

chatInput?.addEventListener('input', resizeChatInput);

chatForm?.addEventListener('submit', async (event) => {
  event.preventDefault();

  const message = chatInput.value.trim();
  if (!message) return;

  const language = getCurrentLanguage();
  const loadingText = language === 'de' ? 'Antwort wird vorbereitet...' : 'Cavab hazirlanir...';
  const errorText = language === 'de'
    ? 'Der Chat ist gerade nicht erreichbar. Bitte versuchen Sie es spater erneut.'
    : 'Chat hazirda cavab vere bilmir. Zehmet olmasa bir az sonra yeniden yoxlayin.';

  addChatMessage(message, 'user');
  chatInput.value = '';
  resizeChatInput();
  setChatLoading(true);
  const loadingMessage = addChatMessage(loadingText, 'bot');

  try {
    const response = await fetch('/api/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, language }),
    });

    const data = await response.json();
    if (!response.ok) {
      throw new Error(data.error || 'Chat request failed');
    }

    loadingMessage.textContent = data.reply || errorText;
  } catch (error) {
    loadingMessage.textContent = errorText;
    loadingMessage.classList.add('error');
  } finally {
    setChatLoading(false);
    chatInput.focus();
  }
});
