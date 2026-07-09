/* ─── PAAI Global JavaScript ─────────────────────────────────────────────── */

'use strict';

// ─── CHATBOT ─────────────────────────────────────────────────────────────────
const Chatbot = {
  sessionId: null,
  isOpen: false,

  init() {
    this.sessionId = localStorage.getItem('paai_chat_session') || this.generateId();
    localStorage.setItem('paai_chat_session', this.sessionId);
    this.bindEvents();
  },

  generateId() {
    return 'sess_' + Math.random().toString(36).substr(2, 9);
  },

  bindEvents() {
    const input = document.getElementById('chatInput');
    if (input) {
      input.addEventListener('keydown', e => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.sendMessage();
        }
      });
    }
  },

  toggle() {
    const win = document.getElementById('chatWindow');
    if (!win) return;
    this.isOpen = !this.isOpen;
    win.classList.toggle('open', this.isOpen);
    if (this.isOpen) {
      document.getElementById('chatInput')?.focus();
    }
  },

async sendMessage(text) {
  const input = document.getElementById('chatInput');
  const message = text || (input?.value.trim());
  if (!message) return;
  if (input) input.value = '';

  this.addMessage(message, 'user');
  this.showTyping();

  try {
    const res = await fetch('/api/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.content || ''
      },
      body: JSON.stringify({ message, session_id: this.sessionId }),
    });
    const data = await res.json();
    this.hideTyping();
    this.addMessage(data.reply || 'Sorry, I could not process that.', 'bot');
  } catch (err) {
    this.hideTyping();
    this.addMessage('Sorry, something went wrong. Please try again.', 'bot');
  }
},

  addMessage(text, sender) {
    const msgs = document.getElementById('chatMessages');
    if (!msgs) return;
    const div = document.createElement('div');
    div.className = `chat-msg ${sender}`;
    div.innerHTML = `<div class="msg-bubble">${text.replace(/\n/g, '<br>')}</div>`;
    msgs.appendChild(div);
    msgs.scrollTop = msgs.scrollHeight;
  },

  showTyping() {
    const msgs = document.getElementById('chatMessages');
    if (!msgs) return;
    const typing = document.createElement('div');
    typing.className = 'chat-msg bot typing-indicator';
    typing.id = 'typingIndicator';
    typing.innerHTML = `<div class="msg-bubble"><span class="dot"></span><span class="dot"></span><span class="dot"></span></div>`;
    msgs.appendChild(typing);
    msgs.scrollTop = msgs.scrollHeight;
  },

  hideTyping() {
    document.getElementById('typingIndicator')?.remove();
  },
};


// ─── COUNTER ANIMATIONS ───────────────────────────────────────────────────────
function animateCounters(container) {
  const counters = (container || document).querySelectorAll('[data-count]');
  counters.forEach(el => {
    const target   = parseInt(el.dataset.count);
    const duration = 2000;
    const start    = performance.now();

    const update = (now) => {
      const pct  = Math.min((now - start) / duration, 1);
      const ease = 1 - Math.pow(1 - pct, 3);
      const val  = Math.round(ease * target);
      el.textContent = val.toLocaleString('en-IN') + '+';
      if (pct < 1) requestAnimationFrame(update);
    };
    requestAnimationFrame(update);
  });
}

// Trigger counters when they enter the viewport
const counterObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      animateCounters(e.target);
      counterObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.3 });

document.querySelectorAll('.hero-stats, .impact-grid').forEach(el => {
  counterObserver.observe(el);
});


// ─── NAVBAR SCROLL EFFECT ─────────────────────────────────────────────────────
const nav = document.querySelector('nav');
if (nav) {
  window.addEventListener('scroll', () => {
    nav.classList.toggle('scrolled', window.scrollY > 30);
  }, { passive: true });
}


// ─── SCROLL REVEAL ────────────────────────────────────────────────────────────
const revealObserver = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) {
      e.target.classList.add('revealed');
      revealObserver.unobserve(e.target);
    }
  });
}, { threshold: 0.1, rootMargin: '0px 0px -50px 0px' });

document.querySelectorAll('.impact-card, .prog-card, .test-card, .mv-card, .team-card').forEach(el => {
  el.classList.add('reveal-on-scroll');
  revealObserver.observe(el);
});


// ─── NEWSLETTER FORM ──────────────────────────────────────────────────────────
document.querySelectorAll('.newsletter-form').forEach(form => {
  const btn = form.querySelector('button');
  const input = form.querySelector('input');
  if (!btn || !input) return;

  btn.addEventListener('click', async () => {
    const email = input.value.trim();
    if (!email || !email.includes('@')) {
      showFlash('Please enter a valid email address.', 'warning');
      return;
    }

    btn.disabled = true;
    btn.textContent = 'Subscribing...';

    try {
      await fetch('/api/newsletter/subscribe', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email }),
      });
      input.value = '';
      showFlash('Subscribed! Thank you for joining our community.', 'success');
    } catch {
      showFlash('Something went wrong. Please try again.', 'danger');
    } finally {
      btn.disabled = false;
      btn.textContent = 'Subscribe';
    }
  });
});


// ─── FLASH MESSAGE HELPER ─────────────────────────────────────────────────────
function showFlash(message, type = 'info') {
  const container = document.getElementById('flashContainer') || createFlashContainer();
  const alert = document.createElement('div');
  alert.className = `flash-alert flash-${type}`;
  alert.innerHTML = `${message} <button onclick="this.parentElement.remove()">×</button>`;
  container.appendChild(alert);
  setTimeout(() => alert.remove(), 5000);
}

function createFlashContainer() {
  const div = document.createElement('div');
  div.id = 'flashContainer';
  div.style.cssText = 'position:fixed;top:80px;right:20px;z-index:9999;display:flex;flex-direction:column;gap:8px;max-width:360px;';
  document.body.appendChild(div);
  return div;
}


// ─── RESOURCE SAVE TOGGLE ─────────────────────────────────────────────────────
document.querySelectorAll('.save-resource-btn').forEach(btn => {
  btn.addEventListener('click', async (e) => {
    e.preventDefault();
    const resourceId = btn.dataset.resourceId;

    try {
      const res  = await fetch(`/dashboard/resources/save/${resourceId}`, { method: 'POST' });
      const data = await res.json();
      if (data.status === 'saved') {
        btn.textContent = '♥ Saved';
        btn.classList.add('saved');
      } else {
        btn.textContent = '♡ Save';
        btn.classList.remove('saved');
      }
    } catch {
      showFlash('Please sign in to save resources.', 'info');
    }
  });
});


// ─── ADMIN: CONFIRM DESTRUCTIVE ACTIONS ───────────────────────────────────────
document.querySelectorAll('[data-confirm]').forEach(el => {
  el.addEventListener('click', (e) => {
    const msg = el.dataset.confirm || 'Are you sure?';
    if (!confirm(msg)) e.preventDefault();
  });
});


// ─── INIT ─────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
  Chatbot.init();

  // Auto-dismiss flash messages after 5 seconds
  document.querySelectorAll('.alert').forEach(alert => {
    setTimeout(() => {
      alert.style.transition = 'opacity 0.5s';
      alert.style.opacity    = '0';
      setTimeout(() => alert.remove(), 500);
    }, 5000);
  });
});

// Expose to global scope for inline handlers
window.Chatbot = Chatbot;
