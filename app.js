const $ = (selector) => document.querySelector(selector);

const tabs = document.querySelectorAll('.project-tab');
const panels = {
  hangman: $('#hangmanDemo'), portfolio: $('#portfolioDemo'),
  organizer: $('#organizerDemo'), chatbot: $('#chatbotDemo')
};
const titles = { hangman: 'Hangman', portfolio: 'Portfolio Tracker', organizer: 'File Organizer', chatbot: 'Customer Chatbot' };
const sources = {
  hangman: 'Task1_Hangman', portfolio: 'Task2_Portfolio_Tracker',
  organizer: 'Task3_File_Organizer', chatbot: 'Task4_Customer_Chatbot'
};

tabs.forEach((tab, index) => tab.addEventListener('click', () => {
  tabs.forEach(item => item.classList.remove('active'));
  tab.classList.add('active');
  Object.values(panels).forEach(panel => panel.classList.remove('active'));
  panels[tab.dataset.project].classList.add('active');
  $('#demoNumber').textContent = String(index + 1).padStart(2, '0');
  $('#demoTitle').textContent = titles[tab.dataset.project];
  $('#sourceLink').href = `https://github.com/AmjadAzward/Datheon_Python_Programming_Internship/tree/main/${sources[tab.dataset.project]}`;
}));

// Hangman
const words = [
  ['Technology','PYTHON'], ['Nature','WATERFALL'], ['Animals','ELEPHANT'],
  ['Food','PINEAPPLE'], ['Technology','ALGORITHM'], ['Animals','BUTTERFLY']
];
const stages = [
`  +---+\n  |   |\n      |\n      |\n      |\n=========`,
`  +---+\n  |   |\n  O   |\n      |\n      |\n=========`,
`  +---+\n  |   |\n  O   |\n  |   |\n      |\n=========`,
`  +---+\n  |   |\n  O   |\n /|   |\n      |\n=========`,
`  +---+\n  |   |\n  O   |\n /|\\  |\n      |\n=========`,
`  +---+\n  |   |\n  O   |\n /|\\  |\n /    |\n=========`,
`  +---+\n  |   |\n  O   |\n /|\\  |\n / \\  |\n=========`
];
let hangmanWord, hangmanGuesses, hangmanWrong, hangmanIndex = 0;
let hangmanMaxAttempts = 8, hangmanHintUsed = false, hangmanFinished = false;
let hangmanPlayed = 0, hangmanWon = 0;

function updateHangmanStats() {
  $('#hangmanPlayed').textContent = hangmanPlayed;
  $('#hangmanWon').textContent = hangmanWon;
  $('#hangmanRate').textContent = `${hangmanPlayed ? Math.round(hangmanWon / hangmanPlayed * 100) : 0}%`;
}

function newHangman() {
  if (hangmanWord && !hangmanFinished) {
    hangmanPlayed++;
    updateHangmanStats();
  }
  hangmanIndex = (hangmanIndex + 1) % words.length;
  hangmanWord = words[hangmanIndex][1];
  hangmanGuesses = new Set(); hangmanWrong = 0;
  hangmanHintUsed = false; hangmanFinished = false;
  $('#hangmanCategory').textContent = words[hangmanIndex][0];
  $('#hangmanStatus').textContent = `Guess the word — ${hangmanMaxAttempts} incorrect guesses allowed.`;
  $('#hintHangman').disabled = false;
  renderHangman();
}
function renderHangman() {
  const stageIndex = hangmanMaxAttempts === 6
    ? hangmanWrong
    : Math.min(6, Math.round(hangmanWrong * 6 / hangmanMaxAttempts));
  $('#hangmanDrawing').textContent = stages[stageIndex];
  $('#wordDisplay').textContent = [...hangmanWord].map(letter => hangmanGuesses.has(letter) ? letter : '_').join(' ');
  $('#keyboard').innerHTML = '';
  'ABCDEFGHIJKLMNOPQRSTUVWXYZ'.split('').forEach(letter => {
    const button = document.createElement('button'); button.textContent = letter;
    if (hangmanGuesses.has(letter)) {
      button.disabled = true;
      button.className = hangmanWord.includes(letter) ? 'used' : 'wrong';
    }
    button.addEventListener('click', () => guessLetter(letter));
    $('#keyboard').appendChild(button);
  });
}
function finishHangman(won) {
  hangmanFinished = true;
  hangmanPlayed++;
  if (won) hangmanWon++;
  updateHangmanStats();
}
function guessLetter(letter) {
  if (hangmanFinished || hangmanGuesses.has(letter)) return;
  hangmanGuesses.add(letter);
  if (!hangmanWord.includes(letter)) hangmanWrong++;
  if ([...hangmanWord].every(char => hangmanGuesses.has(char))) {
    $('#hangmanStatus').textContent = 'Congratulations — you found the word!';
    finishHangman(true);
  } else if (hangmanWrong >= hangmanMaxAttempts) {
    $('#hangmanStatus').textContent = `Game over — the word was ${hangmanWord}.`;
    finishHangman(false);
  } else {
    $('#hangmanStatus').textContent = `${hangmanMaxAttempts - hangmanWrong} incorrect guesses remaining.`;
  }
  renderHangman();
}
$('#hintHangman').addEventListener('click', () => {
  if (hangmanFinished || hangmanHintUsed) return;
  const available = [...new Set(hangmanWord)].filter(letter => !hangmanGuesses.has(letter));
  if (!available.length) return;
  const letter = available[Math.floor(Math.random() * available.length)];
  hangmanGuesses.add(letter); hangmanHintUsed = true;
  $('#hintHangman').disabled = true;
  $('#hangmanStatus').textContent = `Hint: the word contains the letter ${letter}.`;
  if ([...hangmanWord].every(char => hangmanGuesses.has(char))) {
    $('#hangmanStatus').textContent = 'Congratulations — the hint completed the word!';
    finishHangman(true);
  }
  renderHangman();
});
document.querySelectorAll('.difficulty').forEach(button => {
  button.addEventListener('click', () => {
    document.querySelectorAll('.difficulty').forEach(item => item.classList.remove('active'));
    button.classList.add('active');
    hangmanMaxAttempts = { easy: 8, medium: 6, hard: 4 }[button.dataset.difficulty];
    newHangman();
  });
});
$('#newHangman').addEventListener('click', newHangman);
newHangman();

// Portfolio
let holdings = JSON.parse(localStorage.getItem('datheon-holdings') || '[]');
let editingHolding = -1;
function saveHoldings() { localStorage.setItem('datheon-holdings', JSON.stringify(holdings)); renderHoldings(); }
function clearHoldingForm() {
  editingHolding = -1;
  $('#tickerInput').value = $('#sharesInput').value = $('#buyInput').value = $('#currentInput').value = '';
  $('#tickerInput').disabled = false;
  $('#addHolding').innerHTML = 'Add holding <span>＋</span>';
}
function holdingMetrics(item) {
  const invested = item.shares * item.buy;
  const value = item.shares * item.current;
  return { invested, value, gain: invested ? ((value - invested) / invested) * 100 : 0, profit: value - invested };
}
function renderHoldings() {
  const invested = holdings.reduce((sum, item) => sum + item.shares * item.buy, 0);
  const value = holdings.reduce((sum, item) => sum + item.shares * item.current, 0);
  const gain = invested ? ((value - invested) / invested) * 100 : 0;
  $('#investedMetric').textContent = invested.toLocaleString('en-US',{style:'currency',currency:'USD'});
  $('#valueMetric').textContent = value.toLocaleString('en-US',{style:'currency',currency:'USD'});
  $('#returnMetric').textContent = `${gain >= 0 ? '+' : ''}${gain.toFixed(2)}%`;
  $('#returnMetric').className = gain >= 0 ? 'positive' : 'negative';
  $('#holdingsBody').innerHTML = holdings.length ? holdings.map((item, i) => {
    const metric = holdingMetrics(item);
    return `<tr><td>${item.ticker}</td><td>${item.shares}</td><td>${metric.value.toLocaleString('en-US',{style:'currency',currency:'USD'})}</td><td class="${metric.gain >= 0 ? 'positive' : 'negative'}">${metric.gain >= 0 ? '+' : ''}${metric.gain.toFixed(2)}%</td><td><button class="edit-holding" data-index="${i}" aria-label="Edit">Edit</button> <button class="remove-holding" data-index="${i}" aria-label="Remove">×</button></td></tr>`;
  }).join('') : '<tr><td class="empty-row" colspan="5">Add a holding to start tracking</td></tr>';
  document.querySelectorAll('.remove-holding').forEach(button => button.addEventListener('click', () => {
    holdings.splice(Number(button.dataset.index),1); if (editingHolding === Number(button.dataset.index)) clearHoldingForm(); saveHoldings();
  }));
  document.querySelectorAll('.edit-holding').forEach(button => button.addEventListener('click', () => {
    editingHolding = Number(button.dataset.index); const item = holdings[editingHolding];
    $('#tickerInput').value = item.ticker; $('#tickerInput').disabled = true;
    $('#sharesInput').value = item.shares; $('#buyInput').value = item.buy; $('#currentInput').value = item.current;
    $('#addHolding').innerHTML = 'Save changes <span>✓</span>';
  }));
}
$('#addHolding').addEventListener('click', () => {
  const ticker = $('#tickerInput').value.trim().toUpperCase();
  const shares = Number($('#sharesInput').value), buy = Number($('#buyInput').value), current = Number($('#currentInput').value);
  if (!ticker || !(shares > 0) || !(buy > 0) || !(current > 0)) return;
  if (editingHolding >= 0) {
    holdings[editingHolding] = { ...holdings[editingHolding], shares, buy, current };
  } else {
    const existing = holdings.findIndex(item => item.ticker === ticker);
    if (existing >= 0) holdings[existing] = { ticker, shares, buy, current }; else holdings.push({ticker, shares, buy, current});
  }
  clearHoldingForm(); saveHoldings();
});
$('#portfolioRanking').addEventListener('click', () => {
  if (!holdings.length) { alert('Add holdings before viewing the ranking.'); return; }
  const ranking = holdings.map(item => ({ ticker: item.ticker, gain: holdingMetrics(item).gain }))
    .sort((a,b) => b.gain - a.gain);
  alert(ranking.map((item,index) => `${index + 1}. ${item.ticker} — ${item.gain >= 0 ? '+' : ''}${item.gain.toFixed(2)}%`).join('\n'));
});
$('#exportPortfolio').addEventListener('click', () => {
  if (!holdings.length) { alert('There are no holdings to export.'); return; }
  const rows = [['ticker','shares','buy_price','current_price','invested','market_value','gain_loss','percentage']];
  holdings.forEach(item => {
    const metric = holdingMetrics(item);
    rows.push([item.ticker,item.shares,item.buy,item.current,metric.invested.toFixed(2),metric.value.toFixed(2),metric.profit.toFixed(2),metric.gain.toFixed(2)]);
  });
  const csv = rows.map(row => row.join(',')).join('\n');
  const link = document.createElement('a');
  link.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv;charset=utf-8' }));
  link.download = 'portfolio_summary.csv'; link.click(); URL.revokeObjectURL(link.href);
});
renderHoldings();

// File organizer
let organizedFiles = [];
let organizationHistory = [];
const categories = { Documents:['pdf','doc','docx','txt','csv','xlsx'], Images:['jpg','jpeg','png','gif','svg','webp'], Videos:['mp4','mov','mkv','avi'], Archives:['zip','rar','7z','tar','gz'], Code:['py','js','html','css','json','java','c','cpp'], Audio:['mp3','wav','aac','flac','ogg'] };
function categoryFor(file) { const ext = file.name.split('.').pop().toLowerCase(); return Object.entries(categories).find(([, exts]) => exts.includes(ext))?.[0] || 'Others'; }
function groupedFiles() {
  const grouped = {};
  organizedFiles.forEach(file => { const category = categoryFor(file); (grouped[category] ||= []).push(file.name); });
  return grouped;
}
function addFiles(files) { organizedFiles = [...organizedFiles, ...Array.from(files)]; renderFiles(); }
function renderFiles() {
  const grouped = groupedFiles();
  $('#fileCount').textContent = organizedFiles.length ? `${organizedFiles.length} file${organizedFiles.length === 1 ? '' : 's'} selected` : 'No files selected';
  const allCategories = ['Documents','Images','Videos','Archives','Code','Audio','Others'];
  $('#folderGrid').innerHTML = allCategories.map(category => `<article class="folder-card"><strong>${category}</strong><span>${(grouped[category] || []).length} items</span><small>${(grouped[category] || []).join(', ') || 'Empty'}</small></article>`).join('');
}
$('#chooseFiles').addEventListener('click', () => $('#fileInput').click());
$('#fileInput').addEventListener('change', event => addFiles(event.target.files));
$('#clearFiles').addEventListener('click', () => { organizedFiles = []; organizationHistory = []; $('#fileInput').value = ''; renderFiles(); $('#fileCount').textContent = 'No files selected'; });
const dropZone = $('#dropZone');
['dragenter','dragover'].forEach(name => dropZone.addEventListener(name, event => { event.preventDefault(); dropZone.classList.add('dragging'); }));
['dragleave','drop'].forEach(name => dropZone.addEventListener(name, event => { event.preventDefault(); dropZone.classList.remove('dragging'); }));
dropZone.addEventListener('drop', event => addFiles(event.dataTransfer.files));
$('#organizePreview').addEventListener('click', () => {
  if (!organizedFiles.length) { alert('Choose files before running a dry-run preview.'); return; }
  const preview = organizedFiles.map(file => `${file.name} -> ${categoryFor(file)}/`).join('\n');
  alert(`DRY-RUN PREVIEW\n\n${preview}`);
});
$('#organizeFiles').addEventListener('click', () => {
  if (!organizedFiles.length) { alert('Choose files before organizing.'); return; }
  organizationHistory.push([...organizedFiles]);
  $('#fileCount').textContent = `${organizedFiles.length} file${organizedFiles.length === 1 ? '' : 's'} organized`;
  alert('Organization completed. You can undo this operation.');
});
$('#undoOrganize').addEventListener('click', () => {
  if (!organizationHistory.length) { alert('There is no organization operation to undo.'); return; }
  organizedFiles = organizationHistory.pop();
  renderFiles(); alert('Latest organization operation undone.');
});
$('#organizeStats').addEventListener('click', () => {
  const grouped = groupedFiles();
  const stats = Object.entries(grouped).map(([category, names]) => `${category}: ${names.length} file${names.length === 1 ? '' : 's'}`).join('\n');
  alert(stats || 'No files to analyze.');
});
renderFiles();

// Chatbot
const faqs = [
  [/hours|open|close|time/i, 'Our business hours are Monday to Friday, 9:00 AM to 5:00 PM. We are closed on weekends and public holidays.'],
  [/where|location|address|direction/i, 'Our main office is at 25 Main Street. Contact support for directions or additional location information.'],
  [/deliver|shipping|track|order/i, 'Standard delivery usually takes 3–5 business days. Share your order number with support for an update.'],
  [/pay|payment|card|cash/i, 'We accept major debit cards, credit cards, and cash payments where available.'],
  [/return|refund|exchange/i, 'Unused eligible products can be returned within 14 days with proof of purchase.'],
  [/product|catalog|item/i, 'We offer a range of products. Tell me the product name or category you are interested in.'],
  [/contact|support|email|phone/i, 'You can reach support at support@example.com or call +1 555 0100.'],
  [/thank|thanks/i, 'You’re welcome! Happy to help.'],
];
let chatHistory = JSON.parse(localStorage.getItem('datheon-chat-history') || '[]');
function saveChatHistory() { localStorage.setItem('datheon-chat-history', JSON.stringify(chatHistory)); }
function appendChatMessage(role, text) {
  const message = document.createElement('div');
  message.className = `message ${role}`; message.textContent = text;
  $('#chatMessages').appendChild(message);
  $('#chatMessages').scrollTop = $('#chatMessages').scrollHeight;
  chatHistory.push({ role, text, time: new Date().toISOString() }); saveChatHistory();
}
function restoreChatHistory() {
  if (!chatHistory.length) return;
  $('#chatMessages').innerHTML = '';
  chatHistory.forEach(item => {
    const message = document.createElement('div');
    message.className = `message ${item.role}`; message.textContent = item.text;
    $('#chatMessages').appendChild(message);
  });
  $('#chatMessages').scrollTop = $('#chatMessages').scrollHeight;
}
function chatbotResponse(message) {
  const greeting = /^(hi|hello|hey|good morning|good afternoon)[.!]?$/i.test(message.trim());
  if (greeting) return 'Hello! Welcome to customer support. How can I help you today?';
  if (/help|menu|options/i.test(message)) return 'You can ask about business hours, location, delivery, payments, returns, products, or contact information.';
  const match = faqs.find(([pattern]) => pattern.test(message));
  return match ? match[1] : "I'm sorry, I didn’t understand that. Try asking about hours, delivery, payments, returns, or contact details.";
}
function endChat() {
  appendChatMessage('bot', 'Thank you for chatting with us. Have a great day!');
  const rating = prompt('Rate this chat from 1 to 5, or leave blank to skip:', '');
  if (/^[1-5]$/.test(rating || '')) {
    appendChatMessage('bot', `Thank you for your ${rating}/5 rating!`);
  }
  $('#chatInput').disabled = true;
}
$('#chatForm').addEventListener('submit', event => {
  event.preventDefault();
  const input = $('#chatInput'); const message = input.value.trim(); if (!message || input.disabled) return;
  appendChatMessage('user', message); input.value = '';
  if (/^(bye|goodbye|exit|quit)$/i.test(message)) { endChat(); return; }
  setTimeout(() => appendChatMessage('bot', chatbotResponse(message)), 320);
});
$('#chatEnd').addEventListener('click', () => {
  if (!$('#chatInput').disabled) endChat();
});
$('#chatClear').addEventListener('click', () => {
  chatHistory = []; saveChatHistory();
  $('#chatMessages').innerHTML = '<div class="message bot">Hello! I’m your customer support assistant. How can I help you today?</div>';
  $('#chatInput').disabled = false;
});
document.addEventListener('keydown', event => { if (event.key === 'Escape') $('#chatInput')?.blur(); });
$('#footerTime').textContent = new Date().toLocaleDateString('en-US',{month:'short',year:'numeric'});
