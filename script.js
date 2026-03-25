const API_BASE = (typeof API_BASE_URL !== 'undefined') ? API_BASE_URL : '';
const BOT_AVATAR = "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='64' height='64' viewBox='0 0 64 64'%3E%3Crect width='64' height='64' rx='18' fill='%23111827'/%3E%3Ctext x='50%25' y='55%25' dominant-baseline='middle' text-anchor='middle' font-family='Arial' font-size='24' fill='white'%3EPA%3C/text%3E%3C/svg%3E";

const chatMessages = document.getElementById('chatMessages');
const messageInput = document.getElementById('messageInput');
const sendBtn = document.getElementById('sendBtn');
const typingIndicator = document.getElementById('typingIndicator');
const fileInput = document.getElementById('fileInput');

const chatBar = document.getElementById('chatBar');
const chatPopup = document.getElementById('chatPopup');
const chatWidget = document.getElementById('chatWidget');
const expandPopup = document.getElementById('expandPopup');
const closePopup = document.getElementById('closePopup');
const chatBarInput = document.getElementById('chatBarInput');
const chatBarSend = document.getElementById('chatBarSend');
const popupInput = document.getElementById('popupInput');
const popupSendBtn = document.getElementById('popupSendBtn');
const minimizeBtn = document.getElementById('minimizeBtn');
const closeBtn = document.getElementById('closeBtn');
const clearHistoryBtn = document.getElementById('clearHistoryBtn');

let conversationHistory = [];

const STARTER_TOPICS = [
    { name: "Project Overview", icon: "Overview", prompt: "Give me a quick overview of this personal AI project." },
    { name: "Features", icon: "Features", prompt: "What can this assistant do right now?" },
    { name: "Tech Stack", icon: "Stack", prompt: "Explain the tech stack used in this project." },
    { name: "Data Flow", icon: "Flow", prompt: "How does the app process messages and return answers?" },
    { name: "Customization", icon: "Edit", prompt: "How can I customize this assistant for my own needs?" },
    { name: "Uploads", icon: "Files", prompt: "How do file uploads and project notes fit into this assistant?" }
];

function loadChatHistory() {
    const saved = localStorage.getItem('personal_project_chat_history');
    if (!saved) return;

    try {
        conversationHistory = JSON.parse(saved);
        conversationHistory.forEach((msg) => {
            addMessage(msg.content, msg.role, msg.image || null, msg.suggestions || [], false);
        });
    } catch (e) {
        console.error(e);
    }
}

if (chatBarSend) {
    chatBarSend.addEventListener('click', (e) => {
        e.stopPropagation();
        const query = chatBarInput.value.trim();
        if (query) {
            showWidget();
            messageInput.value = query;
            handleSend();
            chatBarInput.value = '';
        } else {
            showPopup();
        }
    });
}

if (chatBar) {
    chatBar.addEventListener('click', (e) => {
        if (e.target.classList.contains('chat-bar-btn')) {
            showWidget();
            messageInput.value = e.target.dataset.query;
            handleSend();
        } else if (!e.target.classList.contains('chat-bar-input') && !e.target.classList.contains('chat-bar-send')) {
            showPopup();
        }
    });
}

if (expandPopup) expandPopup.addEventListener('click', showWidget);
if (closePopup) {
    closePopup.addEventListener('click', () => {
        chatPopup.style.display = 'none';
        chatBar.style.display = 'block';
    });
}
if (minimizeBtn) {
    minimizeBtn.addEventListener('click', () => {
        chatWidget.style.display = 'none';
        chatPopup.style.display = 'block';
    });
}
if (closeBtn) {
    closeBtn.addEventListener('click', () => {
        chatWidget.style.display = 'none';
        chatBar.style.display = 'block';
    });
}

if (popupSendBtn) {
    popupSendBtn.addEventListener('click', () => {
        const query = popupInput.value.trim();
        if (query) {
            showWidget();
            messageInput.value = query;
            handleSend();
            popupInput.value = '';
        }
    });
}

function showPopup() {
    chatBar.style.display = 'none';
    chatPopup.style.display = 'block';
    chatWidget.style.display = 'none';
}

function showWidget() {
    chatBar.style.display = 'none';
    chatPopup.style.display = 'none';
    chatWidget.style.display = 'flex';
    messageInput.focus();
    if (conversationHistory.length === 0) showStarterSelection();
}

function showStarterSelection() {
    if (document.querySelector('.industry-grid')) return;

    const container = document.createElement('div');
    container.className = 'message-container assistant';

    const contentWrapper = document.createElement('div');
    contentWrapper.className = 'message-content-wrapper';

    const text = document.createElement('div');
    text.className = 'message-bubble assistant';
    text.innerHTML = 'To get started, choose a topic:';
    contentWrapper.appendChild(text);

    const grid = document.createElement('div');
    grid.className = 'industry-grid';

    STARTER_TOPICS.forEach((topic) => {
        const card = document.createElement('button');
        card.className = 'industry-card';
        card.innerHTML = `<span class="ind-icon">${topic.icon}</span> <span class="ind-name">${topic.name}</span>`;
        card.onclick = () => {
            grid.style.display = 'none';
            text.innerHTML = `You selected <b>${topic.name}</b>.`;
            messageInput.value = topic.prompt;
            handleSend();
        };
        grid.appendChild(card);
    });

    contentWrapper.appendChild(grid);
    container.appendChild(contentWrapper);
    chatMessages.appendChild(container);
}

function createLightbox(imgSrc) {
    const modal = document.createElement('div');
    modal.className = 'image-modal';
    modal.style.display = 'flex';

    const img = document.createElement('img');
    img.src = imgSrc;
    img.className = 'image-modal-content';

    const close = document.createElement('span');
    close.className = 'image-modal-close';
    close.innerHTML = '&times;';

    modal.onclick = () => document.body.removeChild(modal);
    modal.appendChild(close);
    modal.appendChild(img);
    document.body.appendChild(modal);
}

function addLiveChatOption() {
    const container = document.createElement('div');
    container.className = 'message-container assistant';
    const wrapper = document.createElement('div');
    wrapper.className = 'message-content-wrapper';
    const btn = document.createElement('button');
    btn.className = 'live-chat-btn';
    btn.innerHTML = '<span>Draft</span> Draft a Follow-Up';
    btn.onclick = () => {
        btn.innerHTML = 'Ready to help';
        btn.disabled = true;
        btn.style.backgroundColor = '#ccc';
        setTimeout(() => addMessage('Tell me who you want to contact and I can help draft a follow-up message.', 'assistant'), 300);
    };
    wrapper.appendChild(btn);
    container.appendChild(wrapper);
    chatMessages.appendChild(container);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addMessage(content, role = 'assistant', imageUrl = null, suggestions = [], save = true) {
    const container = document.createElement('div');
    container.className = 'message-container ' + (role === 'user' ? 'user' : 'assistant');

    const avatar = document.createElement('div');
    avatar.className = role === 'user' ? 'user-avatar' : 'bot-avatar';
    avatar.innerHTML = role === 'user' ? 'You' : `<img src="${BOT_AVATAR}" alt="bot" />`;

    const bubble = document.createElement('div');
    bubble.className = 'message-bubble ' + (role === 'user' ? 'user' : 'assistant');

    let html = content.replace(/\n/g, '<br>').replace(/(https?:\/\/[^\s<]+)/g, '<a href="$1" target="_blank">$1</a>');

    if (imageUrl) {
        html += `
            <div class="message-image-container">
                <img src="${imageUrl}" class="message-image" onclick="createLightbox('${imageUrl}')">
            </div>
            <div style="font-size:10px; color:#888;">Click to expand</div>
        `;
    }
    bubble.innerHTML = html;

    const wrapper = document.createElement('div');
    wrapper.className = 'message-content-wrapper';
    wrapper.appendChild(bubble);

    if (suggestions && suggestions.length > 0) {
        const suggestionBox = document.createElement('div');
        suggestionBox.className = 'inline-suggestions';
        suggestions.forEach((txt) => {
            const chip = document.createElement('button');
            chip.className = 'suggestion-chip';
            chip.textContent = txt;
            chip.onclick = () => {
                messageInput.value = txt;
                handleSend();
            };
            suggestionBox.appendChild(chip);
        });
        wrapper.appendChild(suggestionBox);
    }

    container.appendChild(avatar);
    container.appendChild(wrapper);
    chatMessages.appendChild(container);
    chatMessages.scrollTop = chatMessages.scrollHeight;

    if (save) {
        conversationHistory.push({ role, content, image: imageUrl, suggestions });
        localStorage.setItem('personal_project_chat_history', JSON.stringify(conversationHistory));
    }
}

async function handleSend() {
    const msg = messageInput.value.trim();
    if (!msg) return;

    addMessage(msg, 'user');
    messageInput.value = '';

    typingIndicator.classList.add('active');
    chatMessages.scrollTop = chatMessages.scrollHeight;

    try {
        const resp = await fetch(API_BASE + '/api/chat', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: msg, history: conversationHistory.slice(-6) })
        });

        const data = await resp.json();
        typingIndicator.classList.remove('active');
        addMessage(data.response, 'assistant', data.image, data.suggestions);

        if (data.handoff) addLiveChatOption();
    } catch (e) {
        typingIndicator.classList.remove('active');
        addMessage('Connection error. Please try again.', 'assistant');
    }
}

loadChatHistory();
if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener('click', () => {
        if (confirm('Clear history?')) {
            localStorage.removeItem('personal_project_chat_history');
            location.reload();
        }
    });
}
if (sendBtn) sendBtn.addEventListener('click', handleSend);
if (messageInput) {
    messageInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') handleSend();
    });
}
