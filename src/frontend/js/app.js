/**
 * EcoLens Frontend Controller
 * Handles floating navbar sliding indicator, scroll-spy, webcam/upload modes,
 * and live communication with the Flask backend.
 */

const navItems = document.querySelectorAll(".nav-item");
const navIndicator = document.getElementById("nav-indicator");
const sections = document.querySelectorAll("main .section");

let currentMode = "live"; // "live" | "upload"
let selectedFile = null;

// ─────────────────────────────────────────────
//  FLOATING NAVBAR SLIDING INDICATOR & SCROLL-SPY
// ─────────────────────────────────────────────
function moveIndicator(activeEl) {
  if (!activeEl || !navIndicator) return;
  navIndicator.style.width = `${activeEl.offsetWidth}px`;
  navIndicator.style.transform = `translateX(${activeEl.offsetLeft}px)`;
}

function setActiveNav(sectionId) {
  navItems.forEach((item) => {
    const isMatch = item.dataset.section === sectionId;
    item.classList.toggle("active", isMatch);
    if (isMatch) moveIndicator(item);
  });
}

navItems.forEach((item) => {
  item.addEventListener("click", () => setActiveNav(item.dataset.section));
});

window.addEventListener("resize", () => {
  const active = document.querySelector(".nav-item.active");
  moveIndicator(active);
});

// Sync indicator while scrolling
const observer = new IntersectionObserver(
  (entries) => {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        setActiveNav(entry.target.id);
      }
    });
  },
  { rootMargin: "-40% 0px -50% 0px" }
);
sections.forEach((sec) => observer.observe(sec));

// Initialize indicator on load
window.addEventListener("DOMContentLoaded", () => {
  moveIndicator(document.querySelector(".nav-item.active"));
  loadHistory();
});

// ─────────────────────────────────────────────
//  MODE SWITCHING (LIVE WEBCAM vs UPLOAD)
// ─────────────────────────────────────────────
const btnModeLive = document.getElementById("btn-mode-live");
const btnModeUpload = document.getElementById("btn-mode-upload");
const liveViewport = document.getElementById("live-viewport");
const uploadViewport = document.getElementById("upload-viewport");
const fileInput = document.getElementById("file-input");
const uploadPreview = document.getElementById("upload-preview");
const uploadPlaceholder = document.getElementById("upload-placeholder");

btnModeLive.addEventListener("click", () => {
  currentMode = "live";
  btnModeLive.classList.add("active");
  btnModeUpload.classList.remove("active");
  liveViewport.classList.remove("hidden");
  uploadViewport.classList.add("hidden");
});

btnModeUpload.addEventListener("click", () => {
  currentMode = "upload";
  btnModeUpload.classList.add("active");
  btnModeLive.classList.remove("active");
  uploadViewport.classList.remove("hidden");
  liveViewport.classList.add("hidden");
});

uploadViewport.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", (e) => {
  const file = e.target.files[0];
  if (!file) return;
  selectedFile = file;
  uploadPreview.src = URL.createObjectURL(file);
  uploadPreview.classList.remove("hidden");
  uploadPlaceholder.classList.add("hidden");
});

// ─────────────────────────────────────────────
//  API ACTIONS (SCAN / SAVE / CLEAR)
// ─────────────────────────────────────────────
document.getElementById("btn-scan").addEventListener("click", async () => {
  const city = document.getElementById("city-select").value;
  document.getElementById("status-text").textContent = "Sending to Gemini 2.5 Flash...";

  if (currentMode === "upload" && selectedFile) {
    const formData = new FormData();
    formData.append("image", selectedFile);
    formData.append("city", city);
    await fetch("/api/scan", { method: "POST", body: formData });
  } else {
    await fetch("/api/scan", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ city }),
    });
  }
});

document.getElementById("btn-save").addEventListener("click", async () => {
  const res = await fetch("/api/save", { method: "POST" });
  const data = await res.json();
  document.getElementById("status-text").textContent = data.status;
  loadHistory();
});

document.getElementById("btn-clear").addEventListener("click", async () => {
  await fetch("/api/clear", { method: "POST" });
  renderResults([]);
  document.getElementById("scan-time").textContent = "--:--:--";
  document.getElementById("status-text").textContent = "Cleared";
});

document.getElementById("btn-clear-history").addEventListener("click", async () => {
  if (!confirm("Delete all saved scan history?")) return;
  await fetch("/api/history", { method: "DELETE" });
  loadHistory();
});

// ─────────────────────────────────────────────
//  POLLING RESULTS & VOICE STATUS
// ─────────────────────────────────────────────
function renderResults(items) {
  const container = document.getElementById("results-container");
  if (!items || items.length === 0) {
    container.innerHTML = `<div class="empty-state">No items scanned yet. Click <strong>Scan Waste</strong> or say <code>"scan"</code>.</div>`;
    return;
  }

  container.innerHTML = items
    .map(
      (item) => `
      <div class="item-card cat-${item.category}">
        <span class="badge">${item.category}</span>
        <h3>${item.item}</h3>
        <p>${item.reason}</p>
        <ul>${(item.reuse_ideas || []).map((idea) => `<li>${idea}</li>`).join("")}</ul>
        <div class="tip">Local tip: ${item.local_tip || ""}</div>
      </div>`
    )
    .join("");
}

async function pollState() {
  try {
    const [resData, voiceData] = await Promise.all([
      fetch("/api/results").then((r) => r.json()),
      fetch("/api/voice_status").then((r) => r.json()),
    ]);

    document.getElementById("status-text").textContent = resData.status;
    if (resData.scan_time) {
      document.getElementById("scan-time").textContent = resData.scan_time;
    }
    if (resData.results && resData.results.length > 0) {
      renderResults(resData.results);
    }

    const voiceEl = document.getElementById("voice-status");
    if (!voiceData.listening) {
      voiceEl.textContent = "Mic: off";
    } else if (voiceData.last_heard) {
      voiceEl.textContent = `Heard "${voiceData.last_heard}" (${voiceData.last_status})`;
    } else {
      voiceEl.textContent = "Mic: listening";
    }
  } catch {
    // Ignore transient network errors
  }
}

async function loadHistory() {
  try {
    const res = await fetch("/api/history");
    const data = await res.json();
    const entries = data.history || [];

    let totalItems = 0;
    let recyclable = 0;
    entries.forEach((e) => {
      (e.results || []).forEach((i) => {
        totalItems++;
        if (i.category === "Recycle") recyclable++;
      });
    });

    document.getElementById("stat-scans").textContent = entries.length;
    document.getElementById("stat-items").textContent = totalItems;
    document.getElementById("stat-recyclable").textContent = recyclable;

    const list = document.getElementById("history-list");
    if (entries.length === 0) {
      list.innerHTML = `<div class="empty-state">No saved scans yet.</div>`;
      return;
    }

    list.innerHTML = [...entries]
      .reverse()
      .map(
        (e) => `
        <div class="history-entry">
          <strong>${e.timestamp}</strong> — ${e.city || "Delhi"} (${(e.results || []).length} items)
          <div style="margin-top:6px; color:#94a3b8; font-size:0.88rem;">
            ${(e.results || []).map((i) => `[${i.category}] ${i.item}`).join(" • ")}
          </div>
        </div>`
      )
      .join("");
  } catch {
    // Ignore errors on initial load
  }
}

setInterval(pollState, 1500);