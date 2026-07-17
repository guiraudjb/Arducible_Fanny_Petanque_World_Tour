const RANKS = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"];
const SUITS = ["hearts", "diamonds", "clubs", "spades"];
const SUIT_LABELS = { hearts: "Cœur", diamonds: "Carreau", clubs: "Trèfle", spades: "Pique" };
const STORAGE_KEY = "fanny-card-studio-v2";

let assets = [];          // [{id, label, source}]
let assetById = {};        // id -> asset
let sizePresets = {};      // name -> [w, h] mm
let assignment = {};       // slotKey -> assetId
let selectedSlot = null;   // slotKey
let jokerCount = 2;
let activeTab = "fanny";
let searchTerm = "";

const $ = (sel) => document.querySelector(sel);
const el = (tag, cls, text) => {
  const e = document.createElement(tag);
  if (cls) e.className = cls;
  if (text !== undefined) e.textContent = text;
  return e;
};

function slotKey(rank, suit) { return `${rank}-${suit}`; }

function currentSlotList() {
  const slots = [];
  for (const suit of SUITS) for (const rank of RANKS) slots.push([rank, suit]);
  for (let i = 0; i < jokerCount; i++) slots.push(["JOKER", i % 2 === 0 ? "red" : "black"]);
  return slots;
}

function thumbUrl(assetId) {
  return `/thumbs/${assetId.replace(":", "_")}.jpg`;
}

// ---------- réglages carte (taille / coins / nom) ----------

function currentSizePayload() {
  const preset = $("#sizePreset").value;
  if (preset === "custom") {
    return { trim_mm: [parseFloat($("#customW").value) || 63, parseFloat($("#customH").value) || 88] };
  }
  return { size_preset: preset };
}

function currentCardOptions() {
  return {
    ...currentSizePayload(),
    corner_style: $("#cornerStyle").value,
    show_label: $("#showLabel").checked,
  };
}

// ---------- état persistant ----------

function saveState() {
  const s = {
    assignment, jokerCount,
    sizePreset: $("#sizePreset").value,
    customW: $("#customW").value, customH: $("#customH").value,
    cornerStyle: $("#cornerStyle").value,
    showLabel: $("#showLabel").checked,
  };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(s));
}

function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return;
    const s = JSON.parse(raw);
    assignment = s.assignment || {};
    jokerCount = s.jokerCount ?? 2;
    if (s.sizePreset) $("#sizePreset").value = s.sizePreset;
    if (s.customW) $("#customW").value = s.customW;
    if (s.customH) $("#customH").value = s.customH;
    if (s.cornerStyle) $("#cornerStyle").value = s.cornerStyle;
    if (typeof s.showLabel === "boolean") $("#showLabel").checked = s.showLabel;
  } catch (e) { /* état corrompu, on ignore */ }
}

function showToast(msg, isError) {
  const t = $("#toast");
  t.textContent = msg;
  t.classList.remove("hidden");
  t.classList.toggle("error", !!isError);
  clearTimeout(showToast._t);
  showToast._t = setTimeout(() => t.classList.add("hidden"), 4000);
}

async function fetchJSON(url, opts) {
  const res = await fetch(url, opts);
  if (!res.ok) {
    let msg = res.statusText;
    try { msg = (await res.json()).error || msg; } catch (e) { /* pas du json */ }
    throw new Error(msg);
  }
  return res;
}

// ---------- plan de jeu ----------

function buildGrid() {
  const container = $("#suitGrids");
  container.innerHTML = "";
  for (const suit of SUITS) {
    const row = el("div", "suit-row");
    row.appendChild(el("div", "suit-label", SUIT_LABELS[suit]));
    const cells = el("div", "suit-cells");
    for (const rank of RANKS) cells.appendChild(makeSlotEl(rank, suit));
    row.appendChild(cells);
    container.appendChild(row);
  }
  buildJokerGrid();
  refreshGridVisuals();
}

function buildJokerGrid() {
  const jokerGrid = $("#jokerGrid");
  jokerGrid.innerHTML = "";
  if (jokerCount === 0) return;
  jokerGrid.appendChild(el("div", "suit-label", "Jokers"));
  const cells = el("div", "suit-cells");
  for (let i = 0; i < jokerCount; i++) cells.appendChild(makeSlotEl("JOKER", i % 2 === 0 ? "red" : "black"));
  jokerGrid.appendChild(cells);
}

function makeSlotEl(rank, suit) {
  const key = slotKey(rank, suit);
  const div = el("div", "slot empty");
  div.dataset.key = key;
  const tag = el("span", "rank-tag", rank === "JOKER" ? "JK" : rank);
  div.appendChild(tag);
  div.addEventListener("click", () => selectSlot(key));
  return div;
}

function refreshGridVisuals() {
  const slots = currentSlotList();
  document.querySelectorAll(".slot[data-key]").forEach((slotEl) => {
    const key = slotEl.dataset.key;
    const assetId = assignment[key];
    slotEl.classList.toggle("selected", key === selectedSlot);
    slotEl.querySelectorAll("img, .country-tag").forEach((n) => n.remove());
    if (assetId && assetById[assetId]) {
      slotEl.classList.remove("empty");
      slotEl.classList.add("filled");
      const img = el("img");
      img.src = thumbUrl(assetId);
      slotEl.appendChild(img);
      slotEl.appendChild(el("span", "country-tag", assetById[assetId].label || "(sans nom)"));
    } else {
      slotEl.classList.add("empty");
      slotEl.classList.remove("filled");
    }
  });
  const total = slots.length;
  const done = slots.filter(([r, s]) => assignment[slotKey(r, s)] !== undefined).length;
  $("#progress").textContent = `${done} / ${total}`;
}

function selectSlot(key) {
  selectedSlot = key;
  refreshGridVisuals();
  updateAssetGridHighlight();
  updatePreview();
}

// ---------- panneau des images (Fanny + imports) ----------

function switchTab(tab) {
  activeTab = tab;
  document.querySelectorAll(".tab-btn").forEach((b) => b.classList.toggle("active", b.dataset.tab === tab));
  $("#tabFanny").classList.toggle("active", tab === "fanny");
  $("#tabCustom").classList.toggle("active", tab === "custom");
  buildAssetGrid();
}

function buildAssetGrid() {
  const grid = $("#assetGrid");
  grid.innerHTML = "";
  const term = searchTerm.trim().toLowerCase();
  const usedIds = new Set(Object.values(assignment));
  assets
    .filter((a) => a.source === activeTab)
    .filter((a) => !term || a.label.toLowerCase().includes(term))
    .forEach((a) => {
      const card = el("div", "country-card");
      card.dataset.id = a.id;
      if (usedIds.has(a.id)) card.classList.add("used");
      const img = el("img");
      img.src = thumbUrl(a.id);
      img.loading = "lazy";
      card.appendChild(img);
      card.appendChild(el("div", "name", a.label || "(sans nom)"));
      card.addEventListener("click", () => assignAssetToSelectedSlot(a.id));
      grid.appendChild(card);
    });
  if (activeTab === "custom" && assets.filter((a) => a.source === "custom").length === 0) {
    grid.appendChild(el("div", "hint", "Aucune image importée pour l'instant."));
  }
}

function updateAssetGridHighlight() {
  document.querySelectorAll(".country-card").forEach((c) => c.classList.remove("active"));
  if (selectedSlot === null) return;
  const assetId = assignment[selectedSlot];
  if (!assetId) return;
  const card = document.querySelector(`.country-card[data-id="${assetId}"]`);
  if (card) card.classList.add("active");
}

function nextEmptySlot(afterKey) {
  const slots = currentSlotList().map(([r, s]) => slotKey(r, s));
  const startIdx = afterKey ? slots.indexOf(afterKey) + 1 : 0;
  for (let i = 0; i < slots.length; i++) {
    const key = slots[(startIdx + i) % slots.length];
    if (assignment[key] === undefined) return key;
  }
  return null;
}

function assignAssetToSelectedSlot(assetId) {
  if (selectedSlot === null) {
    showToast("Clique d'abord une case du plan de jeu.");
    return;
  }
  assignment[selectedSlot] = assetId;
  saveState();
  const nextKey = nextEmptySlot(selectedSlot);
  refreshGridVisuals();
  buildAssetGrid();
  if (nextKey) selectSlot(nextKey);
  else { updatePreview(); updateAssetGridHighlight(); }
}

// ---------- import d'images ----------

function fileToBase64(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = () => resolve(reader.result.split(",", 2)[1]);
    reader.onerror = reject;
    reader.readAsDataURL(file);
  });
}

async function handleUpload(fileList) {
  const files = Array.from(fileList);
  if (!files.length) return;
  showToast(`Import de ${files.length} image(s)…`);
  try {
    const payloadFiles = await Promise.all(
      files.map(async (f) => ({ name: f.name, data: await fileToBase64(f) }))
    );
    const res = await fetchJSON("/api/upload", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ files: payloadFiles }),
    });
    const data = await res.json();
    for (const a of data.assets) { assets.push(a); assetById[a.id] = a; }
    showToast(`${data.assets.length} image(s) importée(s).`);
    switchTab("custom");
  } catch (e) {
    showToast("Échec de l'import : " + e.message, true);
  }
}

// ---------- aperçu ----------

function parseSlotKey(key) {
  const i = key.lastIndexOf("-");
  return [key.slice(0, i), key.slice(i + 1)];
}

async function updatePreview() {
  const box = $("#previewBox");
  if (selectedSlot === null) {
    box.innerHTML = '<div class="preview-placeholder">Sélectionne une case</div>';
    return;
  }
  const assetId = assignment[selectedSlot];
  if (!assetId) {
    box.innerHTML = '<div class="preview-placeholder">Case vide — choisis une image à droite</div>';
    return;
  }
  const [rank, suit] = parseSlotKey(selectedSlot);
  const target = $("#previewProfile").value;
  box.innerHTML = '<div class="preview-placeholder">Rendu…</div>';
  try {
    const res = await fetchJSON("/api/preview", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target, asset_id: assetId, rank, suit, ...currentCardOptions() }),
    });
    const blob = await res.blob();
    const img = el("img");
    img.src = URL.createObjectURL(blob);
    box.innerHTML = "";
    box.appendChild(img);
  } catch (e) {
    box.innerHTML = `<div class="preview-placeholder">Erreur : ${e.message}</div>`;
  }
}

// ---------- exports ----------

async function doExport(target, filenameFallback) {
  const missing = currentSlotList().filter(([r, s]) => assignment[slotKey(r, s)] === undefined);
  if (missing.length) {
    showToast(`${missing.length} case(s) encore vide(s) — remplis tout le jeu avant d'exporter.`, true);
    return;
  }
  showToast("Génération en cours… (peut prendre une minute)");
  try {
    const res = await fetchJSON("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ target, assignment, joker_count: jokerCount, ...currentCardOptions() }),
    });
    const blob = await res.blob();
    const disposition = res.headers.get("Content-Disposition") || "";
    const match = disposition.match(/filename="([^"]+)"/);
    const filename = match ? match[1] : filenameFallback;
    const url = URL.createObjectURL(blob);
    const a = el("a");
    a.href = url; a.download = filename;
    document.body.appendChild(a); a.click(); a.remove();
    showToast("Export terminé : " + filename);
  } catch (e) {
    showToast("Échec de l'export : " + e.message, true);
  }
}

// ---------- init ----------

function wireControls() {
  $("#jokerCount").value = String(jokerCount);
  $("#jokerCount").addEventListener("change", (e) => {
    jokerCount = parseInt(e.target.value, 10);
    saveState();
    buildJokerGrid();
    refreshGridVisuals();
  });
  $("#sizePreset").addEventListener("change", (e) => {
    $("#customSizeInputs").classList.toggle("hidden", e.target.value !== "custom");
    saveState();
    updatePreview();
  });
  $("#customSizeInputs").classList.toggle("hidden", $("#sizePreset").value !== "custom");
  $("#customW").addEventListener("change", () => { saveState(); updatePreview(); });
  $("#customH").addEventListener("change", () => { saveState(); updatePreview(); });
  $("#cornerStyle").addEventListener("change", () => { saveState(); updatePreview(); });
  $("#showLabel").addEventListener("change", () => { saveState(); updatePreview(); });
  $("#previewProfile").addEventListener("change", updatePreview);
  $("#search").addEventListener("input", (e) => { searchTerm = e.target.value; buildAssetGrid(); updateAssetGridHighlight(); });
  $("#uploadInput").addEventListener("change", (e) => { handleUpload(e.target.files); e.target.value = ""; });
  document.querySelectorAll(".tab-btn").forEach((b) => b.addEventListener("click", () => switchTab(b.dataset.tab)));

  $("#clearSlot").addEventListener("click", () => {
    if (selectedSlot === null) return;
    delete assignment[selectedSlot];
    saveState();
    refreshGridVisuals();
    buildAssetGrid();
    updatePreview();
  });
  $("#clearAll").addEventListener("click", () => {
    if (!confirm("Vider toutes les cases du plan de jeu ?")) return;
    assignment = {};
    saveState();
    refreshGridVisuals();
    buildAssetGrid();
    updatePreview();
  });
  $("#exportSprite").addEventListener("click", () => doExport("sprite", "fanny_card_studio_sprites.zip"));
  $("#exportMpc").addEventListener("click", () => doExport("mpc", "fanny_card_studio_mpc.zip"));
  $("#exportPrintEurope").addEventListener("click", () => doExport("printeurope", "fanny_card_studio_printeurope.pdf"));
}

async function init() {
  wireControls();
  loadState();
  $("#customSizeInputs").classList.toggle("hidden", $("#sizePreset").value !== "custom");

  const res = await fetchJSON("/api/assets");
  const data = await res.json();
  assets = data.assets;
  sizePresets = data.sizes;
  assetById = Object.fromEntries(assets.map((a) => [a.id, a]));

  buildGrid();
  buildAssetGrid();
  updatePreview();
}

init();
