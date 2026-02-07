const API = '';

let currentSessionId = null;

const $sessionList = document.getElementById('session-list');
const $messages = document.getElementById('messages');
const $emptyState = document.getElementById('empty-state');
const $chatForm = document.getElementById('chat-form');
const $input = document.getElementById('message-input');
const $sendBtn = document.getElementById('send-btn');
const $newChat = document.getElementById('new-chat');

// --- API helpers ---

async function api(method, path, body) {
  const opts = { method, headers: { 'Content-Type': 'application/json' } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API}${path}`, opts);
  if (!res.ok) throw new Error(`${res.status} ${res.statusText}`);
  if (res.status === 204) return null;
  return res.json();
}

// --- Sessions ---

async function loadSessions() {
  const sessions = await api('GET', '/sessions');
  $sessionList.innerHTML = '';
  sessions.forEach(s => {
    const el = document.createElement('div');
    el.className = 'session-item' + (s.id === currentSessionId ? ' active' : '');
    el.dataset.id = s.id;
    el.textContent = s.title;

    const del = document.createElement('button');
    del.className = 'delete-btn';
    del.textContent = '\u00d7';
    del.onclick = async (e) => {
      e.stopPropagation();
      await api('DELETE', `/sessions/${s.id}`);
      if (currentSessionId === s.id) {
        currentSessionId = null;
        showEmptyState();
      }
      loadSessions();
    };
    el.appendChild(del);

    el.onclick = () => openSession(s.id);
    $sessionList.appendChild(el);
  });
}

async function openSession(id) {
  currentSessionId = id;
  const session = await api('GET', `/sessions/${id}`);
  renderMessages(session.messages);
  $emptyState.style.display = 'none';
  $messages.style.display = 'flex';
  $chatForm.style.display = 'flex';
  highlightActiveSession();
  scrollToBottom();
  $input.focus();
}

function highlightActiveSession() {
  document.querySelectorAll('.session-item').forEach(el => {
    el.classList.toggle('active', el.dataset.id === currentSessionId);
  });
}

function showEmptyState() {
  $emptyState.style.display = 'flex';
  $messages.style.display = 'none';
  $chatForm.style.display = 'none';
  $messages.innerHTML = '';
}

// --- Messages ---

function renderMessages(messages) {
  $messages.innerHTML = '';
  messages.forEach(m => appendMessage(m.role, m.content));
}

function appendMessage(role, content) {
  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;

  const label = document.createElement('div');
  label.className = 'role-label';
  label.textContent = role === 'user' ? 'You' : 'Assistant';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';
  bubble.textContent = content;

  wrapper.appendChild(label);
  wrapper.appendChild(bubble);
  $messages.appendChild(wrapper);
  return bubble;
}

function scrollToBottom() {
  $messages.scrollTop = $messages.scrollHeight;
}

// --- Chat ---

async function sendMessage(text) {
  if (!currentSessionId || !text.trim()) return;

  appendMessage('user', text.trim());
  scrollToBottom();

  // Create assistant bubble for streaming.
  const bubble = appendMessage('assistant', '');
  bubble.classList.add('streaming');
  scrollToBottom();

  $sendBtn.disabled = true;
  $input.disabled = true;

  try {
    const res = await fetch(`${API}/sessions/${currentSessionId}/chat`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: text.trim(), stream: true }),
    });

    const reader = res.body.getReader();
    const decoder = new TextDecoder();
    let buffer = '';

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split('\n');
      buffer = lines.pop(); // keep incomplete line

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const data = line.slice(6).trim();
        if (!data) continue;

        try {
          const event = JSON.parse(data);
          if (event.type === 'delta') {
            bubble.textContent += event.content;
            scrollToBottom();
          } else if (event.type === 'done') {
            bubble.classList.remove('streaming');
          } else if (event.type === 'error') {
            bubble.textContent += `\n[Error: ${event.error}]`;
            bubble.classList.remove('streaming');
          }
        } catch (_) {
          // skip malformed JSON
        }
      }
    }

    bubble.classList.remove('streaming');
    loadSessions(); // refresh sidebar counts
  } catch (err) {
    bubble.textContent = `Error: ${err.message}`;
    bubble.classList.remove('streaming');
  } finally {
    $sendBtn.disabled = false;
    $input.disabled = false;
    $input.focus();
  }
}

// --- Events ---

$newChat.addEventListener('click', async () => {
  const session = await api('POST', '/sessions', { title: 'New Chat' });
  currentSessionId = session.id;
  await loadSessions();
  openSession(session.id);
});

$chatForm.addEventListener('submit', (e) => {
  e.preventDefault();
  const text = $input.value;
  $input.value = '';
  $input.style.height = 'auto';
  sendMessage(text);
});

$input.addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault();
    $chatForm.dispatchEvent(new Event('submit'));
  }
});

// Auto-resize textarea.
$input.addEventListener('input', () => {
  $input.style.height = 'auto';
  $input.style.height = Math.min($input.scrollHeight, 160) + 'px';
});

// Init
loadSessions();
