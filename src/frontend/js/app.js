// ─────────────────────────────────────────────
// 1. CITY-SPECIFIC DISPOSAL RULES & 5R DATASETS
// ─────────────────────────────────────────────
const CITY_TIPS = {
  "Delhi": {
    pet:     "Crush flat and drop in an NDMC/MCD Blue Dry Bin or sell to a local Delhi Kabadiwala.",
    cup:     "Carry a steel tumbler to Delhi cafes; PE-lined cups belong in Black Residual Bins.",
    peel:    "Compost in a balcony Khamba pot or hand over in MCD Green Wet Waste bins.",
    battery: "Drop at CPCB-authorized e-waste bins at Croma (CP / South Ex) or schedule Karo Sambhav pickup.",
    guide: {
      Refuse:  "Reject single-use plastic bags & toxic e-waste in household trash; use Croma / Karo Sambhav e-bins.",
      Reduce:  "Switch from PE-lined disposable coffee cups to reusable steel tumblers at Delhi metro cafes.",
      Reuse:   "Repurpose glass pickle jars and tin containers for kitchen storage or desk organizers.",
      Recycle: "Segregate clean PET #1 bottles & cardboard into NDMC/MCD Blue Bins or local Kabadiwalas.",
      Rot:     "Turn kitchen scraps into compost via RWA composters or MCD Green Wet Waste collection."
    }
  },
  "Greater Noida": {
    pet:     "Drop clean PET bottles in GNIDA Blue Dry Bins or hand over to society scrap collectors in Knowledge Park / Pari Chowk.",
    cup:     "Avoid PE-lined disposable cups at campus canteens; dispose used ones in Black Residual Bins.",
    peel:    "Place in GNIDA Green Wet Waste bins or residential society aerobic compost pits.",
    battery: "Drop spent cells at authorized e-waste collection points in Alpha/Beta Commercial Belts or Croma Greater Noida.",
    guide: {
      Refuse:  "Refuse single-use cutlery & polybags; route batteries to CPCB-authorized Greater Noida e-waste hubs.",
      Reduce:  "Carry reusable bottles & tumblers across university campuses and tech parks.",
      Reuse:   "Repurpose glass jars and cardboard delivery boxes before handing them to society raddi-walas.",
      Recycle: "Sort paper, PET, and metal into GNIDA Blue Dry Waste bins for MRF recovery.",
      Rot:     "Feed wet kitchen organics into society OWC (Organic Waste Converters) or GNIDA Green Bins."
    }
  },
  "Mumbai": {
    pet:     "Deposit in BMC Dry Waste Centers, Bisleri Bottles for Change, or local Mumbai raddi-walas.",
    cup:     "Use reusable cups at cafes; PE-lined paper cups cannot be pulped and go to BMC Reject Bins.",
    peel:    "Segregate into BMC Green Wet Bins or society vermicomposting pits.",
    battery: "Drop at BMC E-Waste collection vans or authorized Croma/Reliance Digital e-bins across Mumbai.",
    guide: {
      Refuse:  "Strictly avoid banned single-use plastics under Maharashtra Plastic Ban; isolate e-waste.",
      Reduce:  "Opt for refill packs and reusable dabbas to reduce landfill load on Deonar.",
      Reuse:   "Donate usable household items through Mumbai RaddiConnect or local NGOs.",
      Recycle: "Hand over clean dry recyclables to BMC Dry Waste Sorting Centers (DWCC).",
      Rot:     "Compost wet waste in society pits or hand over daily to BMC Green Wet Waste vans."
    }
  },
  "Bengaluru": {
    pet:     "Send clean PET bottles to BBMP Dry Waste Collection Centres (DWCC) or Hasiru Dala collectors.",
    cup:     "Carry a steel tumbler to Bengaluru cafes; soiled PE-lined cups belong in Black Reject Bins.",
    peel:    "Compost at home with Daily Dump Khamba pots or hand over in BBMP Green Wet Bins.",
    battery: "Drop spent batteries at Saahas Zero Waste Kasa Rasa centers or authorized e-waste bins.",
    guide: {
      Refuse:  "Refuse multi-layer plastics and send batteries to Saahas / E-Parisaraa e-waste hubs.",
      Reduce:  "Carry cloth bags and steel containers to Indiranagar/Koramangala zero-waste stores.",
      Reuse:   "Donate electronics and jars via Bengaluru reuse networks and community thrift swaps.",
      Recycle: "Use BBMP 2-bin-1-bag segregation; route dry waste directly to ward DWCCs.",
      Rot:     "Turn kitchen scraps into compost using balcony Khamba pots or BBMP Green Bins."
    }
  }
};

function getDemoItemsForCity(city) {
  const tips = CITY_TIPS[city] || CITY_TIPS["Delhi"];
  return [
    {
      item: "PET Plastic Water Bottle (500ml)",
      category: "Recycle",
      co2: 0.18,
      reason: "Clear #1 PET thermoplastic with high material recovery and recycling demand.",
      reuse_ideas: [
        "Cut bottom half into a self-watering desk herb planter",
        "Pierce cap to create a slow drip-irrigation spike for plants",
        "Store loose screws, stationery, or spare charging cables"
      ],
      local_tip: tips.pet
    },
    {
      item: "PE-Lined Disposable Coffee Cup",
      category: "Reduce",
      co2: 0.09,
      reason: "Paperboard bonded with thin polyethylene (PE) moisture film complicates standard pulping.",
      reuse_ideas: [
        "Use as a seedling starter pot before soil transplanting",
        "Repurpose as a disposable paint-mixing or brush-rinse cup",
        "Organize paperclips and binder pins inside a desk drawer"
      ],
      local_tip: tips.cup
    },
    {
      item: "Banana Peel (Organic Scrap)",
      category: "Rot",
      co2: 0.14,
      reason: "Potassium- and nitrogen-rich biodegradable wet waste ideal for rapid aerobic composting.",
      reuse_ideas: [
        "Soak in water for 48 hours to create potassium-rich liquid plant fertilizer",
        "Chop finely and bury in potted soil as a natural slow-release nutrient",
        "Layer with dry leaves in a home terracotta composter"
      ],
      local_tip: tips.peel
    },
    {
      item: "AA Alkaline Battery (1.5V)",
      category: "Refuse",
      co2: 0.42,
      reason: "Contains heavy metals that leach toxic compounds into groundwater if landfilled.",
      reuse_ideas: [
        "Switch to NiMH rechargeable AA cells to replace hundreds of disposables",
        "Tape both terminals with clear tape before safe dry storage",
        "Collect spent batteries in a labeled glass jar until e-waste drop-off"
      ],
      local_tip: tips.battery
    }
  ];
}

const CAT_STYLES = {
  Recycle: { border: 'border-l-catRecycle', top: 'border-t-catRecycle', badge: 'bg-catRecycle/15 text-catRecycle border-catRecycle/40', dot: 'bg-catRecycle' },
  Reuse:   { border: 'border-l-catReuse',   top: 'border-t-catReuse',   badge: 'bg-catReuse/15 text-catReuse border-catReuse/40',       dot: 'bg-catReuse' },
  Rot:     { border: 'border-l-catRot',     top: 'border-t-catRot',     badge: 'bg-catRot/15 text-catRot border-catRot/40',             dot: 'bg-catRot' },
  Refuse:  { border: 'border-l-catRefuse',  top: 'border-t-catRefuse',  badge: 'bg-catRefuse/15 text-catRefuse border-catRefuse/40',    dot: 'bg-catRefuse' },
  Reduce:  { border: 'border-l-catReduce',  top: 'border-t-catReduce',  badge: 'bg-catReduce/15 text-catReduce border-catReduce/40',    dot: 'bg-catReduce' }
};

// ─────────────────────────────────────────────
// 2. APPLICATION STATE & LOCALSTORAGE
// ─────────────────────────────────────────────
const STORAGE_KEY = 'ecolens_web_history_v1';
let currentCity    = 'Delhi';
let currentMode    = 'demo'; // 'demo' | 'webcam' | 'upload'
let bboxVisible    = true;
let isScanning     = false;
let webcamStream   = null;
let uploadedFile   = null;
let currentResults = [];
let scanHistory    = [];

function loadHistoryFromStorage() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      scanHistory = JSON.parse(raw);
      return;
    }
  } catch (e) {}

  scanHistory = [
    {
      id: 'seed-101',
      timestamp: '2026-11-19 18:24:10',
      city: 'Delhi',
      source: 'Demo Pile',
      results: getDemoItemsForCity('Delhi').slice(0, 3)
    },
    {
      id: 'seed-102',
      timestamp: '2026-11-20 09:12:45',
      city: 'Delhi',
      source: 'Webcam Scan',
      results: [
        {
          item: "Glass Pickle Jar (500g)",
          category: "Reuse",
          co2: 0.31,
          reason: "Infinitely recyclable, non-toxic, airtight pantry container.",
          reuse_ideas: ["Store dry lentils or spices", "Overnight oats jar", "Desk pen holder"],
          local_tip: "Wash and reuse at home; if broken, wrap in newspaper before placing in MCD Blue Bin."
        },
        {
          item: "Corrugated Delivery Box",
          category: "Recycle",
          co2: 0.25,
          reason: "Clean kraft paper fibers can be recycled up to 7 times.",
          reuse_ideas: ["Flatten for closet storage", "Shred as brown carbon for compost", "Floor mat for painting"],
          local_tip: "Remove plastic tape, flatten, and hand over to your local Delhi raddi-wala."
        }
      ]
    }
  ];
  saveHistoryToStorage();
}

function saveHistoryToStorage() {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(scanHistory));
  } catch (e) {}
}

// ─────────────────────────────────────────────
// 3. INITIALIZATION & DRAG-AND-DROP
// ─────────────────────────────────────────────
window.addEventListener('DOMContentLoaded', () => {
  loadHistoryFromStorage();
  render5RGuide();
  renderHistoryDashboard();
  setupDragAndDrop();
  initFloatingNavIndicator();
});

// ─────────────────────────────────────────────
// FLOATING NAVBAR SLIDING INDICATOR & SCROLL SPY
// ─────────────────────────────────────────────
let manualNavLock = false;
let manualNavTimer = null;

function updateNavIndicator(activeEl) {
  const indicator = document.getElementById('nav-indicator');
  if (!indicator || !activeEl) return;

  document.querySelectorAll('.nav-tab-btn').forEach(btn => {
    btn.classList.remove('active');
  });
  activeEl.classList.add('active');

  indicator.style.width = `${activeEl.offsetWidth}px`;
  indicator.style.transform = `translateX(${activeEl.offsetLeft}px)`;
}

function handleNavClick(el) {
  updateNavIndicator(el);
  manualNavLock = true;
  clearTimeout(manualNavTimer);
  manualNavTimer = setTimeout(() => {
    manualNavLock = false;
  }, 850);
}

function initFloatingNavIndicator() {
  const navButtons = Array.from(document.querySelectorAll('.nav-tab-btn'));
  if (!navButtons.length) return;

  const initialActive = document.querySelector('.nav-tab-btn.active') || navButtons[0];
  requestAnimationFrame(() => updateNavIndicator(initialActive));

  window.addEventListener('load', () => {
    const current = document.querySelector('.nav-tab-btn.active') || navButtons[0];
    updateNavIndicator(current);
  });

  window.addEventListener('resize', () => {
    const current = document.querySelector('.nav-tab-btn.active') || navButtons[0];
    updateNavIndicator(current);
  });

  const sectionIds = ['scanner', 'guide', 'history', 'how-it-works'];
  const sections = sectionIds.map(id => document.getElementById(id)).filter(Boolean);

  const updateActiveFromScroll = () => {
    if (manualNavLock) return;
    const scrollProbe = window.scrollY + 180;
    let currentSectionId = sectionIds[0];

    for (const sec of sections) {
      if (scrollProbe >= sec.offsetTop) {
        currentSectionId = sec.id;
      }
    }

    if (window.innerHeight + window.scrollY >= document.body.offsetHeight - 40) {
      currentSectionId = sectionIds[sectionIds.length - 1];
    }

    const targetBtn = document.querySelector(`.nav-tab-btn[data-section="${currentSectionId}"]`);
    if (targetBtn && !targetBtn.classList.contains('active')) {
      updateNavIndicator(targetBtn);
    }
  };

  window.addEventListener('scroll', updateActiveFromScroll, { passive: true });
}

function setupDragAndDrop() {
  const dz = document.getElementById('scanner-dropzone');
  if (!dz) return;
  ['dragenter', 'dragover'].forEach(evt => {
    dz.addEventListener(evt, e => {
      e.preventDefault();
      dz.classList.add('drop-active');
    });
  });
  ['dragleave', 'drop'].forEach(evt => {
    dz.addEventListener(evt, e => {
      e.preventDefault();
      dz.classList.remove('drop-active');
    });
  });
  dz.addEventListener('drop', e => {
    const file = e.dataTransfer.files && e.dataTransfer.files[0];
    if (file && file.type.startsWith('image/')) {
      displayUploadedFile(file);
    }
  });
}

// ─────────────────────────────────────────────
// 4. VIEWPORT MODES (WEBCAM, UPLOAD, DEMO PILE)
// ─────────────────────────────────────────────
async function startWebcam() {
  const videoEl = document.getElementById('webcam-video');
  const labelEl = document.getElementById('webcam-btn-label');

  if (webcamStream) {
    stopWebcam();
    loadDemoPile();
    return;
  }

  try {
    webcamStream = await navigator.mediaDevices.getUserMedia({
      video: { facingMode: 'environment' },
      audio: false
    });
    videoEl.srcObject = webcamStream;
    videoEl.classList.remove('hidden');
    document.getElementById('demo-pile-scene').classList.add('hidden');
    document.getElementById('uploaded-preview').classList.add('hidden');

    currentMode = 'webcam';
    labelEl.textContent = 'Stop Webcam';
    document.getElementById('viewport-mode-badge').textContent = 'LIVE WEBCAM • 16:9';
    showToast('Webcam connected — click Scan Waste');
  } catch (err) {
    showToast('Webcam unavailable or permission denied — using Demo Pile');
  }
}

function stopWebcam() {
  if (webcamStream) {
    webcamStream.getTracks().forEach(t => t.stop());
    webcamStream = null;
  }
  document.getElementById('webcam-video').classList.add('hidden');
  document.getElementById('webcam-btn-label').textContent = 'Start Webcam';
}

function handleImageUpload(event) {
  const file = event.target.files && event.target.files[0];
  if (file) displayUploadedFile(file);
}

function displayUploadedFile(file) {
  stopWebcam();
  uploadedFile = file;
  const reader = new FileReader();
  reader.onload = (e) => {
    const img = document.getElementById('uploaded-preview');
    img.src = e.target.result;
    img.classList.remove('hidden');
    document.getElementById('demo-pile-scene').classList.add('hidden');
    currentMode = 'upload';
    document.getElementById('viewport-mode-badge').textContent = 'UPLOADED IMAGE';
    showToast(`Loaded "${file.name}" — ready to scan`);
  };
  reader.readAsDataURL(file);
}

function loadDemoPile() {
  stopWebcam();
  uploadedFile = null;
  document.getElementById('uploaded-preview').classList.add('hidden');
  document.getElementById('demo-pile-scene').classList.remove('hidden');
  currentMode = 'demo';
  document.getElementById('viewport-mode-badge').textContent = 'DEMO PILE • 16:9';
  showToast('Demo Waste Pile loaded');
}

function toggleBoundingBoxes() {
  bboxVisible = !bboxVisible;
  const btn  = document.getElementById('btn-bbox-toggle');
  const text = document.getElementById('bbox-btn-text');
  const ov   = document.getElementById('bbox-overlay');

  if (bboxVisible) {
    text.textContent = 'BBox: ON';
    btn.classList.add('border-emeraldAccent/40', 'text-emeraldAccent');
    btn.classList.remove('border-borderSubtle', 'text-gray-400');
    if (currentResults.length > 0 && currentMode === 'demo') ov.classList.remove('opacity-0');
  } else {
    text.textContent = 'BBox: OFF';
    btn.classList.remove('border-emeraldAccent/40', 'text-emeraldAccent');
    btn.classList.add('border-borderSubtle', 'text-gray-400');
    ov.classList.add('opacity-0');
  }
}

// ─────────────────────────────────────────────
// 5. CORE COMMANDS & VOICE SIMULATOR
// ─────────────────────────────────────────────
function executeCommand(cmd) {
  if (cmd === 'scan') runScan();
  else if (cmd === 'save') saveCurrentScan();
  else if (cmd === 'clear') clearResults();
  else if (cmd === 'history') {
    document.getElementById('history').scrollIntoView({ behavior: 'smooth' });
    showToast('Scrolled to Scan History');
  }
}

function simulateVoice(phrase) {
  const allowed = ['scan', 'save', 'clear', 'history'];
  const cleaned = phrase.toLowerCase().trim();
  const statusEl = document.getElementById('voice-feedback-status');

  if (allowed.includes(cleaned)) {
    statusEl.innerHTML = `Heard: <strong class="text-emeraldAccent">"${cleaned}"</strong> ✓ Accepted`;
    executeCommand(cleaned);
  } else {
    statusEl.innerHTML = `Heard: <strong class="text-catRefuse">"${cleaned}"</strong> ✗ Rejected (invalid)`;
    showToast('Voice rejected — use strict commands only');
  }
}

async function runScan() {
  if (isScanning) return;
  isScanning = true;

  const laser = document.getElementById('scan-laser');
  const ov    = document.getElementById('bbox-overlay');
  const pill  = document.getElementById('viewport-status-pill');

  laser.classList.remove('hidden');
  ov.classList.add('opacity-0');
  pill.textContent = 'Analyzing with Gemini 2.5 Flash...';
  pill.classList.add('text-emeraldAccent');

  try {
    // If user uploaded an image and backend is reachable, send it to /api/scan
    if (currentMode === 'upload' && uploadedFile) {
      const fd = new FormData();
      fd.append('image', uploadedFile);
      fd.append('city', currentCity);
      const res = await fetch('/api/scan', { method: 'POST', body: fd });
      if (res.ok) {
        await new Promise(r => setTimeout(r, 1500));
        const rData = await fetch('/api/results').then(r => r.json());
        if (Array.isArray(rData.results) && rData.results.length > 0) {
          currentResults = rData.results;
        } else {
          currentResults = getDemoItemsForCity(currentCity);
        }
      } else {
        currentResults = getDemoItemsForCity(currentCity);
      }
    } else {
      await new Promise(r => setTimeout(r, 1200));
      currentResults = getDemoItemsForCity(currentCity);
    }
  } catch {
    currentResults = getDemoItemsForCity(currentCity);
  } finally {
    laser.classList.add('hidden');
    isScanning = false;
  }

  if (bboxVisible && currentMode === 'demo') {
    ov.classList.remove('opacity-0');
  }

  const nowTime = new Date().toTimeString().split(' ')[0];
  pill.textContent = `Scanned at ${nowTime} • ${currentResults.length} items`;
  renderResultsPanel(currentResults, nowTime);
  showToast(`Classified ${currentResults.length} waste items`);
}

async function saveCurrentScan() {
  if (!currentResults.length) {
    showToast('Run "Scan Waste" first before saving');
    return;
  }

  const now = new Date();
  const pad = n => String(n).padStart(2, '0');
  const ts  = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())} ${pad(now.getHours())}:${pad(now.getMinutes())}:${pad(now.getSeconds())}`;
  const sourceLabel = currentMode === 'webcam' ? 'Webcam Scan' : currentMode === 'upload' ? 'Uploaded Photo' : 'Demo Pile';

  const entry = {
    id: 'scan-' + Date.now(),
    timestamp: ts,
    city: currentCity,
    source: sourceLabel,
    results: JSON.parse(JSON.stringify(currentResults))
  };

  scanHistory.push(entry);
  saveHistoryToStorage();
  renderHistoryDashboard();

  // Best-effort sync to backend /api/save if running under Flask
  try {
    await fetch('/api/save', { method: 'POST' });
  } catch {}

  showToast('Scan saved to History & localStorage!');
}

function clearResults() {
  currentResults = [];
  document.getElementById('bbox-overlay').classList.add('opacity-0');
  document.getElementById('viewport-status-pill').textContent = 'Ready to Scan';
  document.getElementById('results-count-badge').textContent = '0 items';
  document.getElementById('results-subtitle').textContent = 'Click "Scan Waste" to classify visible items';

  document.getElementById('results-panel').innerHTML = `
    <div class="h-full min-h-[340px] flex flex-col items-center justify-center text-center p-6 animate-card">
      <h4 class="text-base font-bold text-white">Results Cleared</h4>
      <p class="text-xs text-gray-400 mt-1.5 max-w-xs">Click <strong class="text-emeraldAccent">Scan Waste</strong> to analyze the active viewport.</p>
    </div>
  `;
}

// ─────────────────────────────────────────────
// 6. RENDER 5R RESULTS PANEL
// ─────────────────────────────────────────────
function renderResultsPanel(items, scanTime) {
  const panel = document.getElementById('results-panel');
  document.getElementById('results-count-badge').textContent = `${items.length} items`;
  document.getElementById('results-subtitle').textContent = `Last scan: ${scanTime} • City: ${currentCity}`;
  panel.innerHTML = '';

  items.forEach((item, idx) => {
    const st = CAT_STYLES[item.category] || CAT_STYLES.Recycle;
    const card = document.createElement('article');
    card.style.animationDelay = `${idx * 70}ms`;
    card.className = `rounded-xl bg-obsidian border border-borderSubtle border-l-4 ${st.border} p-4 animate-card opacity-0`;

    const ideasHtml = (item.reuse_ideas || []).map(idea => `
      <li class="flex items-start gap-2 text-xs text-gray-300 leading-relaxed">
        <span class="text-emeraldAccent font-mono font-bold">+</span>
        <span>${idea}</span>
      </li>
    `).join('');

    card.innerHTML = `
      <div class="flex items-start justify-between gap-2 mb-1.5">
        <h4 class="text-sm font-bold text-white leading-snug">${item.item}</h4>
        <span class="px-2.5 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider border shrink-0 ${st.badge}">
          ${item.category}
        </span>
      </div>
      <p class="text-xs text-gray-400 mb-3 leading-relaxed">${item.reason}</p>
      <div class="mb-3">
        <div class="font-mono text-[10px] uppercase tracking-wider text-gray-500 mb-1.5">Creative Reuse Ideas</div>
        <ul class="space-y-1">${ideasHtml}</ul>
      </div>
      <div class="pt-2.5 border-t border-borderSubtle flex items-start gap-2 text-xs text-sky-300">
        <span class="font-mono font-bold text-cyanAccent shrink-0">@</span>
        <span class="leading-snug">${item.local_tip}</span>
      </div>
    `;
    panel.appendChild(card);
  });
}

// ─────────────────────────────────────────────
// 7. RENDER 5R FRAMEWORK GUIDE & CITY SWITCHER
// ─────────────────────────────────────────────
function render5RGuide() {
  const tips = CITY_TIPS[currentCity].guide;
  const cards = [
    { cat: 'Refuse',  title: '1. Refuse',  desc: 'Eliminate hazardous or non-recyclable single-use waste at the source.', ex: 'AA Batteries, Thermocol, Single-use bags', local: tips.Refuse },
    { cat: 'Reduce',  title: '2. Reduce',  desc: 'Minimize multi-material packaging that resists standard recycling.', ex: 'PE-lined coffee cups, Foil wraps', local: tips.Reduce },
    { cat: 'Reuse',   title: '3. Reuse',   desc: 'Extend product lifespan by repurposing durable containers.', ex: 'Glass pickle jars, Tin cans, Cloth bags', local: tips.Reuse },
    { cat: 'Recycle', title: '4. Recycle', desc: 'Recover clean dry materials back into circular manufacturing.', ex: 'PET #1 bottles, Cardboard, Aluminum', local: tips.Recycle },
    { cat: 'Rot',     title: '5. Rot',     desc: 'Return biodegradable wet organics back to nutrient-rich soil.', ex: 'Banana peels, Coffee grounds, Tea leaves', local: tips.Rot }
  ];

  const grid = document.getElementById('five-r-grid');
  grid.innerHTML = cards.map(c => {
    const st = CAT_STYLES[c.cat];
    return `
      <div class="rounded-2xl bg-card border border-borderSubtle border-t-4 ${st.top} p-5 flex flex-col justify-between hover:bg-cardHover transition">
        <div>
          <div class="flex items-center justify-between mb-3">
            <h3 class="text-base font-extrabold text-white">${c.title}</h3>
            <span class="w-2.5 h-2.5 rounded-full ${st.dot}"></span>
          </div>
          <p class="text-xs text-gray-400 leading-relaxed mb-3">${c.desc}</p>
          <div class="text-[11px] font-mono text-gray-300 bg-obsidian rounded-lg p-2.5 border border-borderSubtle mb-3">
            <span class="text-gray-500 block text-[10px] uppercase mb-0.5">Examples</span>
            ${c.ex}
          </div>
        </div>
        <div class="pt-3 border-t border-borderSubtle text-xs text-cyanAccent leading-relaxed">
          <span class="font-mono text-[10px] uppercase text-gray-500 block mb-0.5">${currentCity} Guidance</span>
          ${c.local}
        </div>
      </div>
    `;
  }).join('');
}

function changeCity(newCity) {
  currentCity = newCity;
  document.getElementById('nav-city-select').value = newCity;
  document.getElementById('footer-city-select').value = newCity;

  document.querySelectorAll('.city-name-inline').forEach(el => {
    el.textContent = newCity;
  });

  render5RGuide();

  if (currentResults.length > 0) {
    currentResults = getDemoItemsForCity(currentCity);
    renderResultsPanel(currentResults, new Date().toTimeString().split(' ')[0]);
  }

  showToast(`Updated local disposal rules for ${newCity}`);
}

// ─────────────────────────────────────────────
// 8. RENDER HISTORY DASHBOARD
// ─────────────────────────────────────────────
function renderHistoryDashboard() {
  const totalScans = scanHistory.length;
  let totalItems = 0;
  let totalCo2   = 0;

  scanHistory.forEach(entry => {
    (entry.results || []).forEach(it => {
      totalItems++;
      totalCo2 += (it.co2 || 0.15);
    });
  });

  document.getElementById('kpi-total-scans').textContent = totalScans;
  document.getElementById('kpi-total-items').textContent = totalItems;
  document.getElementById('kpi-total-co2').textContent   = totalCo2.toFixed(2);

  const list = document.getElementById('history-list');
  if (totalScans === 0) {
    list.innerHTML = `
      <div class="rounded-2xl bg-card border border-borderSubtle p-10 text-center">
        <p class="text-sm font-semibold text-gray-300">No Saved Scans Yet</p>
        <p class="text-xs text-gray-500 mt-1">Run a scan in the Live Scanner above and click <strong class="text-blue-400">Save to History</strong>.</p>
      </div>
    `;
    return;
  }

  list.innerHTML = '';
  [...scanHistory].reverse().forEach(entry => {
    const items = entry.results || [];
    const badgesHtml = items.map(it => {
      const st = CAT_STYLES[it.category] || CAT_STYLES.Recycle;
      return `<span class="px-2 py-0.5 rounded-full text-[10px] font-bold border ${st.badge}">${it.category}</span>`;
    }).join('');

    const rowsHtml = items.map(it => {
      const st = CAT_STYLES[it.category] || CAT_STYLES.Recycle;
      return `
        <div class="py-2.5 border-b border-borderSubtle last:border-none flex flex-col sm:flex-row sm:items-center justify-between gap-2">
          <div class="flex items-center gap-2.5">
            <span class="w-2.5 h-2.5 rounded-full shrink-0 ${st.dot}"></span>
            <div>
              <div class="text-xs font-semibold text-white">${it.item}</div>
              <div class="text-[11px] text-gray-400">${it.local_tip}</div>
            </div>
          </div>
          <span class="font-mono text-[10px] font-bold uppercase text-gray-400 shrink-0">${it.category}</span>
        </div>
      `;
    }).join('');

    const row = document.createElement('div');
    row.className = 'rounded-2xl bg-card border border-borderSubtle overflow-hidden';
    row.innerHTML = `
      <button onclick="toggleHistoryRow('${entry.id}')" class="w-full px-5 py-4 text-left flex flex-col sm:flex-row sm:items-center justify-between gap-3 hover:bg-cardHover transition cursor-pointer">
        <div class="flex flex-wrap items-center gap-3">
          <span class="font-mono text-xs font-bold text-emeraldAccent">${entry.timestamp}</span>
          <span class="px-2 py-0.5 rounded bg-obsidian border border-borderSubtle text-[11px] text-gray-300">${entry.source || 'Scanner'}</span>
          <span class="text-xs text-cyanAccent font-medium">${entry.city || 'Delhi'}</span>
        </div>
        <div class="flex items-center gap-3">
          <div class="flex flex-wrap gap-1.5">${badgesHtml}</div>
          <svg id="h-chev-${entry.id}" class="w-4 h-4 text-gray-400 transition-transform duration-200 shrink-0" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2">
            <polyline points="6 9 12 15 18 9"/>
          </svg>
        </div>
      </button>
      <div id="h-body-${entry.id}" class="hidden px-5 pb-4 pt-1 border-t border-borderSubtle bg-obsidian/50">
        ${rowsHtml}
      </div>
    `;
    list.appendChild(row);
  });
}

function toggleHistoryRow(id) {
  const body = document.getElementById('h-body-' + id);
  const chev = document.getElementById('h-chev-' + id);
  const isHidden = body.classList.contains('hidden');
  body.classList.toggle('hidden', !isHidden);
  chev.style.transform = isHidden ? 'rotate(180deg)' : 'rotate(0deg)';
}

function openClearConfirm() {
  if (!scanHistory.length) {
    showToast('History is already empty');
    return;
  }
  document.getElementById('clear-history-confirm').classList.remove('hidden');
}

function closeClearConfirm() {
  document.getElementById('clear-history-confirm').classList.add('hidden');
}

async function confirmClearHistory() {
  scanHistory = [];
  saveHistoryToStorage();
  closeClearConfirm();
  renderHistoryDashboard();
  try {
    await fetch('/api/history', { method: 'DELETE' });
  } catch {}
  showToast('All scan history cleared');
}

// ─────────────────────────────────────────────
// 9. TOAST HELPER
// ─────────────────────────────────────────────
let toastTimer = null;
function showToast(msg) {
  const t = document.getElementById('toast');
  document.getElementById('toast-msg').textContent = msg;
  t.classList.remove('opacity-0', 'translate-y-3');
  t.classList.add('opacity-100', 'translate-y-0');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    t.classList.add('opacity-0', 'translate-y-3');
    t.classList.remove('opacity-100', 'translate-y-0');
  }, 2200);
}