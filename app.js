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
let hangmanMaxAttempts = 8;

function newHangman() {
  hangmanIndex = (hangmanIndex + 1) % words.length;
  hangmanWord = words[hangmanIndex][1];
  hangmanGuesses = new Set(); hangmanWrong = 0;
  $('#hangmanCategory').textContent = words[hangmanIndex][0];
  $('#hangmanStatus').textContent = `Guess the word — ${hangmanMaxAttempts} incorrect guesses allowed.`;
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
function guessLetter(letter) {
  if (hangmanGuesses.has(letter)) return;
  hangmanGuesses.add(letter);
  if (!hangmanWord.includes(letter)) hangmanWrong++;
  if ([...hangmanWord].every(char => hangmanGuesses.has(char))) {
    $('#hangmanStatus').textContent = 'Congratulations — you found the word!';
  } else if (hangmanWrong >= hangmanMaxAttempts) {
    $('#hangmanStatus').textContent = `Game over — the word was ${hangmanWord}.`;
  } else {
    $('#hangmanStatus').textContent = `${hangmanMaxAttempts - hangmanWrong} incorrect guesses remaining.`;
  }
  renderHangman();
}
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
function saveHoldings() { localStorage.setItem('datheon-holdings', JSON.stringify(holdings)); renderHoldings(); }
function renderHoldings() {
  const invested = holdings.reduce((sum, item) => sum + item.shares * item.buy, 0);
  const value = holdings.reduce((sum, item) => sum + item.shares * item.current, 0);
  const gain = invested ? ((value - invested) / invested) * 100 : 0;
  $('#investedMetric').textContent = invested.toLocaleString('en-US',{style:'currency',currency:'USD'});
  $('#valueMetric').textContent = value.toLocaleString('en-US',{style:'currency',currency:'USD'});
  $('#returnMetric').textContent = `${gain >= 0 ? '+' : ''}${gain.toFixed(2)}%`;
  $('#returnMetric').className = gain >= 0 ? 'positive' : 'negative';
  $('#holdingsBody').innerHTML = holdings.length ? holdings.map((item, i) => {
    const holdingValue = item.shares * item.current;
    const holdingReturn = ((item.current - item.buy) / item.buy) * 100;
    return `<tr><td>${item.ticker}</td><td>${item.shares}</td><td>${holdingValue.toLocaleString('en-US',{style:'currency',currency:'USD'})}</td><td class="${holdingReturn >= 0 ? 'positive' : 'negative'}">${holdingReturn >= 0 ? '+' : ''}${holdingReturn.toFixed(2)}%</td><td><button class="remove-holding" data-index="${i}" aria-label="Remove">×</button></td></tr>`;
  }).join('') : '<tr><td class="empty-row" colspan="5">Add a holding to start tracking</td></tr>';
  document.querySelectorAll('.remove-holding').forEach(button => button.addEventListener('click', () => { holdings.splice(Number(button.dataset.index),1); saveHoldings(); }));
}
$('#addHolding').addEventListener('click', () => {
  const ticker = $('#tickerInput').value.trim().toUpperCase();
  const shares = Number($('#sharesInput').value); const buy = Number($('#buyInput').value); const current = Number($('#currentInput').value);
  if (!ticker || !(shares > 0) || !(buy > 0) || !(current > 0)) return;
  holdings.push({ticker, shares, buy, current});
  $('#tickerInput').value = $('#sharesInput').value = $('#buyInput').value = $('#currentInput').value = '';
  saveHoldings();
});
renderHoldings();

// File organizer
let organizedFiles = [];
const categories = { Documents:['pdf','doc','docx','txt','csv','xlsx'], Images:['jpg','jpeg','png','gif','svg','webp'], Videos:['mp4','mov','mkv','avi'], Archives:['zip','rar','7z','tar','gz'], Code:['py','js','html','css','json','java','c','cpp'], Audio:['mp3','wav','aac','flac','ogg'] };
function categoryFor(file) { const ext = file.name.split('.').pop().toLowerCase(); return Object.entries(categories).find(([, exts]) => exts.includes(ext))?.[0] || 'Others'; }
function addFiles(files) { organizedFiles = [...organizedFiles, ...Array.from(files)]; renderFiles(); }
function renderFiles() {
  const grouped = {};
  organizedFiles.forEach(file => { const category = categoryFor(file); (grouped[category] ||= []).push(file.name); });
  $('#fileCount').textContent = organizedFiles.length ? `${organizedFiles.length} file${organizedFiles.length === 1 ? '' : 's'} organized` : 'No files selected';
  const allCategories = ['Documents','Images','Videos','Archives','Code','Audio','Others'];
  $('#folderGrid').innerHTML = allCategories.map(category => `<article class="folder-card"><strong>${category}</strong><span>${(grouped[category] || []).length} items</span><small>${(grouped[category] || []).join(', ') || 'Empty'}</small></article>`).join('');
}
$('#chooseFiles').addEventListener('click', () => $('#fileInput').click());
$('#fileInput').addEventListener('change', event => addFiles(event.target.files));
$('#clearFiles').addEventListener('click', () => { organizedFiles = []; $('#fileInput').value = ''; renderFiles(); });
const dropZone = $('#dropZone');
['dragenter','dragover'].forEach(name => dropZone.addEventListener(name, event => { event.preventDefault(); dropZone.classList.add('dragging'); }));
['dragleave','drop'].forEach(name => dropZone.addEventListener(name, event => { event.preventDefault(); dropZone.classList.remove('dragging'); }));
dropZone.addEventListener('drop', event => addFiles(event.dataTransfer.files));
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
function chatbotResponse(message) {
  const greeting = /^(hi|hello|hey|good morning|good afternoon)[.!]?$/i.test(message.trim());
  if (greeting) return 'Hello! Welcome to customer support. How can I help you today?';
  if (/help|menu|options/i.test(message)) return 'You can ask about business hours, location, delivery, payments, returns, products, or contact information.';
  const match = faqs.find(([pattern]) => pattern.test(message));
  return match ? match[1] : "I'm sorry, I didn’t understand that. Try asking about hours, delivery, payments, returns, or contact details.";
}
$('#chatForm').addEventListener('submit', event => {
  event.preventDefault();
  const input = $('#chatInput'); const message = input.value.trim(); if (!message) return;
  $('#chatMessages').insertAdjacentHTML('beforeend', `<div class="message user"></div>`);
  $('#chatMessages').lastElementChild.textContent = message; input.value = '';
  setTimeout(() => { const bot = document.createElement('div'); bot.className = 'message bot'; bot.textContent = chatbotResponse(message); $('#chatMessages').appendChild(bot); $('#chatMessages').scrollTop = $('#chatMessages').scrollHeight; }, 320);
});

document.addEventListener('keydown', event => { if (event.key === 'Escape') $('#chatInput')?.blur(); });
$('#footerTime').textContent = new Date().toLocaleDateString('en-US',{month:'short',year:'numeric'});
