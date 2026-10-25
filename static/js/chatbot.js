/* ==========================================================================
   KK_COLLECTIONS — AI Shopping Assistant ("KK AI") Frontend Logic
   Natural language interaction, embedded product cards, quick chips
   ========================================================================== */

(function() {
  let modal = null;
  let messagesContainer = null;
  let inputField = null;
  let sendBtn = null;
  let chipsContainer = null;
  let currentProductId = null;

  document.addEventListener('DOMContentLoaded', () => {
    initChatbotDOM();
    detectPageContext();
  });

  function initChatbotDOM() {
    modal = document.getElementById('kk-ai-modal');
    messagesContainer = document.getElementById('kk-ai-messages');
    inputField = document.getElementById('kk-ai-input');
    sendBtn = document.getElementById('kk-ai-send-btn');
    chipsContainer = document.getElementById('kk-ai-chips');

    const triggerBtn = document.getElementById('kk-ai-floating-btn');
    const headerTriggerBtn = document.getElementById('header-ai-btn');
    const closeBtn = document.getElementById('ai-close-btn');
    const resetBtn = document.getElementById('ai-reset-btn');

    if (triggerBtn) {
      triggerBtn.addEventListener('click', toggleChatbot);
    }
    if (headerTriggerBtn) {
      headerTriggerBtn.addEventListener('click', toggleChatbot);
    }
    if (closeBtn) {
      closeBtn.addEventListener('click', closeChatbot);
    }
    if (resetBtn) {
      resetBtn.addEventListener('click', resetChat);
    }

    if (sendBtn && inputField) {
      sendBtn.addEventListener('click', handleSend);
      inputField.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
          e.preventDefault();
          handleSend();
        }
      });
    }

    // Attach listeners to chips
    document.querySelectorAll('.ai-chip').forEach(chip => {
      chip.addEventListener('click', () => {
        const query = chip.dataset.query || chip.textContent.trim();
        sendMessage(query);
      });
    });

    // Check if initial greeting needs to be rendered
    if (messagesContainer && messagesContainer.children.length === 0) {
      renderGreeting();
    }
  }

  function detectPageContext() {
    // If on product page, detect product id
    const productEl = document.querySelector('[data-current-product-id]');
    if (productEl) {
      currentProductId = parseInt(productEl.dataset.currentProductId);
    }

    // "Ask KK AI About This Product" button on product detail page
    const askAiDetailBtn = document.getElementById('ask-ai-detail-btn');
    if (askAiDetailBtn) {
      askAiDetailBtn.addEventListener('click', () => {
        openChatbot();
        const productName = askAiDetailBtn.dataset.productName || 'this piece';
        sendMessage(`Tell me about ${productName}: what sizes and materials are available?`);
      });
    }
  }

  function toggleChatbot() {
    if (!modal) return;
    if (modal.classList.contains('active')) {
      closeChatbot();
    } else {
      openChatbot();
    }
  }

  function openChatbot() {
    if (!modal) return;
    modal.classList.add('active');
    setTimeout(() => {
      if (inputField) inputField.focus();
      scrollToBottom();
    }, 150);
  }

  function closeChatbot() {
    if (!modal) return;
    modal.classList.remove('active');
  }

  function renderGreeting() {
    const greetingHTML = `
      <div class="chat-msg msg-ai">
        <div class="msg-avatar"><i class="fas fa-sparkles"></i></div>
        <div class="msg-bubble">
          Hi! 👋 I'm your <strong>KK_COLLECTIONS</strong> personal shopping assistant.<br>
          What are you looking for today? 💕<br><br>
          <em>Ask me about thread bangles, saree matching colors, budget combos, or order tracking!</em>
        </div>
      </div>
    `;
    messagesContainer.innerHTML = greetingHTML;
  }

  function resetChat() {
    if (!messagesContainer) return;
    renderGreeting();
    renderChips(["Shop Bangles", "Shop Earrings", "Under ₹300", "Wedding Collection", "Track My Order", "New Arrivals"]);
  }

  function handleSend() {
    if (!inputField) return;
    const msg = inputField.value.trim();
    if (!msg) return;
    inputField.value = '';
    sendMessage(msg);
  }

  async function sendMessage(text) {
    if (!text || !messagesContainer) return;

    // 1. Render user message bubble
    appendMessage(text, 'user');
    scrollToBottom();

    // 2. Show typing indicator
    const typingEl = showTypingIndicator();
    scrollToBottom();

    try {
      const res = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: text,
          current_product_id: currentProductId
        })
      });

      const data = await res.json();
      removeTypingIndicator(typingEl);

      if (data.text) {
        appendMessage(data.text, 'ai', data.products, data.order_info, data.combo_info);
      } else {
        appendMessage("I'm here to help! Could you please repeat that?", 'ai');
      }

      // Update action chips dynamically
      if (data.action_chips && data.action_chips.length) {
        renderChips(data.action_chips);
      }

      scrollToBottom();
    } catch (err) {
      console.error('Chat error:', err);
      removeTypingIndicator(typingEl);
      appendMessage("I couldn't reach the server right now. Please try asking again in a moment! 💕", 'ai');
      scrollToBottom();
    }
  }

  function appendMessage(text, sender, products = [], orderInfo = null, comboInfo = null) {
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg msg-${sender}`;

    const avatarHTML = sender === 'ai' 
      ? '<div class="msg-avatar"><i class="fas fa-sparkles"></i></div>' 
      : '<div class="msg-avatar" style="background:#5B1426;color:#FFF;"><i class="fas fa-user"></i></div>';

    // Parse Markdown-like bold and linebreaks
    let formattedText = escapeHTML(text)
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\*(.*?)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br>');

    let cardsHTML = '';
    if (products && products.length > 0) {
      cardsHTML = `
        <div class="chat-product-carousel">
          ${products.map(p => `
            <div class="chat-product-card">
              <div class="chat-prod-img-wrap">
                <img src="/static/images/products/${p.image}" alt="${escapeHTML(p.product_name)}">
                ${p.discount > 0 ? `<span class="chat-prod-badge">${p.discount}% OFF</span>` : ''}
              </div>
              <div class="chat-prod-body">
                <div class="chat-prod-name" title="${escapeHTML(p.product_name)}">${escapeHTML(p.product_name)}</div>
                <div class="chat-prod-price-row">
                  <span class="chat-prod-price">₹${p.final_price || p.price}</span>
                  ${p.discount > 0 ? `<span class="chat-prod-orig">₹${p.price}</span>` : ''}
                </div>
                <div class="chat-prod-actions">
                  <button class="chat-btn-add" data-product-id="${p.product_id}">
                    <i class="fas fa-cart-plus"></i> Add
                  </button>
                  <a href="/product/${p.product_id}" class="chat-btn-view">
                    <i class="fas fa-eye"></i>
                  </a>
                </div>
              </div>
            </div>
          `).join('')}
        </div>
      `;
    }

    let orderBadgeHTML = '';
    if (orderInfo) {
      orderBadgeHTML = `
        <div style="margin-top:10px;padding:10px;background:#F7F2EA;border-radius:6px;border:1px solid #E8DFD3;font-size:0.8rem;">
          <a href="/track/${orderInfo.tracking_number}" style="color:#5B1426;font-weight:700;text-decoration:underline;">
            <i class="fas fa-map-marker-alt"></i> View Full Live Timeline (#${orderInfo.tracking_number})
          </a>
        </div>
      `;
    }

    msgDiv.innerHTML = `
      ${avatarHTML}
      <div class="msg-bubble">
        <div>${formattedText}</div>
        ${orderBadgeHTML}
        ${cardsHTML}
      </div>
    `;

    messagesContainer.appendChild(msgDiv);

    // Bind Add to Cart buttons inside this newly created bubble
    msgDiv.querySelectorAll('.chat-btn-add').forEach(btn => {
      btn.addEventListener('click', async () => {
        const pid = btn.dataset.productId;
        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';
        try {
          const res = await fetch('/api/cart/add', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ product_id: pid, quantity: 1 })
          });
          const data = await res.json();
          if (data.success) {
            btn.innerHTML = '<i class="fas fa-check"></i> Added';
            btn.style.backgroundColor = '#198754';
            const countBadge = document.getElementById('header-cart-count');
            if (countBadge) countBadge.textContent = data.cart.total_items;
            if (window.showToast) window.showToast('Added to bag! 💕');
          }
        } catch (e) {
          btn.disabled = false;
          btn.innerHTML = '<i class="fas fa-cart-plus"></i> Add';
        }
      });
    });
  }

  function renderChips(chipsList) {
    if (!chipsContainer) return;
    chipsContainer.innerHTML = '';
    chipsList.forEach(chipText => {
      const btn = document.createElement('button');
      btn.className = 'ai-chip';
      btn.textContent = chipText;
      btn.addEventListener('click', () => sendMessage(chipText));
      chipsContainer.appendChild(btn);
    });
  }

  function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'chat-msg msg-ai typing-msg';
    typingDiv.innerHTML = `
      <div class="msg-avatar"><i class="fas fa-sparkles"></i></div>
      <div class="msg-bubble">
        <div class="typing-dots">
          <span></span><span></span><span></span>
        </div>
      </div>
    `;
    messagesContainer.appendChild(typingDiv);
    return typingDiv;
  }

  function removeTypingIndicator(el) {
    if (el && el.parentNode) {
      el.parentNode.removeChild(el);
    }
  }

  function scrollToBottom() {
    if (messagesContainer) {
      messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
  }

  function escapeHTML(str) {
    return str
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // Expose global opener
  window.openKKAssistant = function(query) {
    openChatbot();
    if (query) {
      sendMessage(query);
    }
  };
})();
