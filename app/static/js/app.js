/* ═══════════════════════════════════════════════════════════
   Mediathek NAS — UI
   ═══════════════════════════════════════════════════════════ */

/* ── i18n ───────────────────────────────────────────────── */

const STRINGS = {
  de: {
    "tab.find": "Suchen",
    "tab.queue": "Downloads",
    "tab.rules": "Abos",
    "tab.setup": "Einstellungen",
    "search.placeholder": "Sendung, Thema, Stichwort",
    "search.submit": "Suchen",
    "search.filters": "Filter",
    "search.idle": "Noch nichts gesucht",
    "search.running": "Suche läuft …",
    "search.hits": "{from}–{to} von {total}",
    "search.perPage": "pro Seite",
    "results.empty": "Suche etwas, um Treffer zu sehen.",
    "results.none": "Keine Treffer.",
    "field.channel": "Sender",
    "field.topic": "Thema",
    "field.query": "Suchbegriff",
    "field.from": "Von",
    "field.to": "Bis",
    "field.minMin": "Min. Minuten",
    "field.maxMin": "Max. Minuten",
    "field.quality": "Qualität",
    "field.root": "Download-Root",
    "field.rootDefault": "Vorgabe aus dem Container",
    "field.rootReset": "auf {path} zurücksetzen",
    "queue.delete": "Aus der Liste entfernen? Die Datei auf der Platte bleibt.",
    "queue.added": "In der Warteschlange",
    "field.parallel": "Gleichzeitig",
    "field.retries": "Auto-Retrys",
    "field.filename": "Dateiname",
    "field.subfolder": "Unterordner",
    "field.ruleLimit": "Abo-Limit",
    "field.tokens": "Platzhalter",
    "quality.best": "Beste verfügbare",
    "quality.high": "Bevorzugt HD",
    "quality.medium": "Normal",
    "quality.low": "Klein",
    "queue.title": "Warteschlange und Verlauf",
    "queue.empty": "Noch keine Downloads.",
    "rules.idle": "Noch kein Abo angelegt",
    "rules.empty": "Noch keine Abos vorhanden.",
    "rules.new": "Neues Abo anlegen",
    "rules.name": "Name",
    "rules.interval": "Intervall (Min.)",
    "rules.keepLatest": "Treffer merken",
    "rules.target": "Zielordner (optional)",
    "rules.auto": "Neue Treffer sofort laden",
    "rules.save": "Abo speichern",
    "rules.runAll": "Alle prüfen",
    "rules.runDue": "Fällige prüfen",
    "rules.saving": "Speichere Abo …",
    "rules.saved": "Abo gespeichert.",
    "rules.checking": "Prüfe {name} …",
    "rules.checkAll": "Prüfe alle Abos …",
    "rules.checkDue": "Führe fällige Abos aus …",
    "rules.result": "{matches} neue Treffer, {downloads} Downloads angestoßen.",
    "rules.every": "alle {n} Min.",
    "rules.autoOn": "Auto",
    "rules.autoOff": "Manuell",
    "rules.hits": "{n} Treffer",
    "rules.never": "Noch nie geprüft",
    "rules.last": "Zuletzt: {when}",
    "rules.active": "Aktiv",
    "rules.paused": "Pausiert",
    "rules.prefilled": "Abo aus dem Treffer vorbelegt — unten prüfen und speichern.",
    "setup.downloads": "Downloads",
    "setup.servers": "Medienserver",
    "setup.import": "Import und Dubletten",
    "setup.system": "System-Check",
    "setup.save": "Speichern",
    "setup.saving": "Speichere …",
    "setup.saved": "Gespeichert.",
    "setup.scan": "Jetzt aktualisieren",
    "setup.scanning": "Aktualisierung läuft …",
    "opt.skipDupes": "Dubletten global verhindern",
    "opt.scheduler": "Abos im Hintergrund ausführen",
    "opt.nfo": "NFO-Datei schreiben",
    "opt.json": "JSON-Metadaten schreiben",
    "opt.plex": "Plex-Integration",
    "opt.plexSection": "Plex Section-ID",
    "opt.plexScan": "Nach Download scannen",
    "opt.jellyfin": "Jellyfin-Integration",
    "opt.jellyfinLib": "Jellyfin Library-ID",
    "opt.jellyfinScan": "Nach Download aktualisieren",
    "opt.infuse": "Infuse-Links auf Apple-Geräten",
    "import.folder": "Ordner einlesen",
    "import.list": "Listendatei einlesen",
    "import.maxFiles": "Max. Dateien",
    "import.run": "Einlesen",
    "import.running": "Lese ein …",
    "import.done": "{imported} übernommen, {skipped} übersprungen.",
    "import.idle": "Noch kein Import ausgeführt.",
    "dupes.none": "Keine Dubletten erkannt.",
    "dupes.group": "{n} Einträge",
    "status.queued": "Wartet",
    "status.downloading": "Läuft",
    "status.completed": "Fertig",
    "status.failed": "Fehler",
    "status.canceled": "Abgebrochen",
    "flag.new": "neu",
    "flag.have": "vorhanden",
    "detail.download": "Auf NAS laden",
    "detail.makeRule": "Als Abo übernehmen",
    "detail.website": "Zur Mediathek",
    "detail.stream": "Vorschau",
    "detail.source": "Direkte Quelle",
    "detail.subtitles": "Untertitel",
    "detail.infusePlay": "In Infuse abspielen",
    "detail.infuseSave": "In Infuse merken",
    "detail.noDescription": "Keine Beschreibung vorhanden.",
    "detail.present": "Bereits vorhanden",
    "detail.hlsNote": "Inline-Vorschau nur für MP4. Andere Formate über den Stream-Link öffnen.",
    "activity.running": "{n} laufen",
    "activity.queued": "{n} warten",
    "dupe.exists": "Ist bereits vorhanden und wurde nicht erneut angelegt.",
    "error.download": "Download nicht möglich",
    "unit.min": "Min.",
    "unit.unknown": "?",
    "sys.containerChecks": "Container",
    "sys.manualChecks": "Manuell auf der Synology prüfen",
  },
  en: {
    "tab.find": "Search",
    "tab.queue": "Downloads",
    "tab.rules": "Subscriptions",
    "tab.setup": "Settings",
    "search.placeholder": "Show, topic, keyword",
    "search.submit": "Search",
    "search.filters": "Filters",
    "search.idle": "Nothing searched yet",
    "search.running": "Searching …",
    "search.hits": "{from}–{to} of {total}",
    "search.perPage": "per page",
    "results.empty": "Search for something to see results.",
    "results.none": "No results.",
    "field.channel": "Channel",
    "field.topic": "Topic",
    "field.query": "Keyword",
    "field.from": "From",
    "field.to": "To",
    "field.minMin": "Min. minutes",
    "field.maxMin": "Max. minutes",
    "field.quality": "Quality",
    "field.root": "Download root",
    "field.rootDefault": "Container default",
    "field.rootReset": "reset to {path}",
    "queue.delete": "Remove from the list? The file on disk is kept.",
    "queue.added": "Queued",
    "field.parallel": "Concurrent",
    "field.retries": "Auto retries",
    "field.filename": "Filename",
    "field.subfolder": "Subfolder",
    "field.ruleLimit": "Subscription limit",
    "field.tokens": "Placeholders",
    "quality.best": "Best available",
    "quality.high": "Prefer HD",
    "quality.medium": "Normal",
    "quality.low": "Small",
    "queue.title": "Queue and history",
    "queue.empty": "No downloads yet.",
    "rules.idle": "No subscription yet",
    "rules.empty": "No subscriptions yet.",
    "rules.new": "Add subscription",
    "rules.name": "Name",
    "rules.interval": "Interval (min)",
    "rules.keepLatest": "Keep matches",
    "rules.target": "Target folder (optional)",
    "rules.auto": "Download new matches immediately",
    "rules.save": "Save subscription",
    "rules.runAll": "Check all",
    "rules.runDue": "Check due",
    "rules.saving": "Saving subscription …",
    "rules.saved": "Subscription saved.",
    "rules.checking": "Checking {name} …",
    "rules.checkAll": "Checking all subscriptions …",
    "rules.checkDue": "Running due subscriptions …",
    "rules.result": "{matches} new matches, {downloads} downloads started.",
    "rules.every": "every {n} min",
    "rules.autoOn": "Auto",
    "rules.autoOff": "Manual",
    "rules.hits": "{n} matches",
    "rules.never": "Never checked",
    "rules.last": "Last: {when}",
    "rules.active": "Active",
    "rules.paused": "Paused",
    "rules.prefilled": "Subscription prefilled from this result — review and save below.",
    "setup.downloads": "Downloads",
    "setup.servers": "Media servers",
    "setup.import": "Import and duplicates",
    "setup.system": "System check",
    "setup.save": "Save",
    "setup.saving": "Saving …",
    "setup.saved": "Saved.",
    "setup.scan": "Refresh now",
    "setup.scanning": "Refreshing …",
    "opt.skipDupes": "Prevent duplicates globally",
    "opt.scheduler": "Run subscriptions in the background",
    "opt.nfo": "Write NFO file",
    "opt.json": "Write JSON metadata",
    "opt.plex": "Plex integration",
    "opt.plexSection": "Plex section ID",
    "opt.plexScan": "Scan after download",
    "opt.jellyfin": "Jellyfin integration",
    "opt.jellyfinLib": "Jellyfin library ID",
    "opt.jellyfinScan": "Refresh after download",
    "opt.infuse": "Infuse links on Apple devices",
    "import.folder": "Import folder",
    "import.list": "Import list file",
    "import.maxFiles": "Max. files",
    "import.run": "Import",
    "import.running": "Importing …",
    "import.done": "{imported} imported, {skipped} skipped.",
    "import.idle": "Nothing imported yet.",
    "dupes.none": "No duplicates found.",
    "dupes.group": "{n} entries",
    "status.queued": "Queued",
    "status.downloading": "Running",
    "status.completed": "Done",
    "status.failed": "Failed",
    "status.canceled": "Canceled",
    "flag.new": "new",
    "flag.have": "have it",
    "detail.download": "Download to NAS",
    "detail.makeRule": "Turn into subscription",
    "detail.website": "Open mediathek",
    "detail.stream": "Preview",
    "detail.source": "Direct source",
    "detail.subtitles": "Subtitles",
    "detail.infusePlay": "Play in Infuse",
    "detail.infuseSave": "Save to Infuse",
    "detail.noDescription": "No description available.",
    "detail.present": "Already in your library",
    "detail.hlsNote": "Inline preview works for MP4 only. Use the stream link for other formats.",
    "activity.running": "{n} running",
    "activity.queued": "{n} queued",
    "dupe.exists": "Already present — nothing was queued again.",
    "error.download": "Could not start download",
    "unit.min": "min",
    "unit.unknown": "?",
    "sys.containerChecks": "Container",
    "sys.manualChecks": "Check manually on the NAS",
  },
};

let lang = localStorage.getItem("mn.lang") || (navigator.language || "de").slice(0, 2);
if (!STRINGS[lang]) lang = "de";

function t(key, vars) {
  let value = (STRINGS[lang] && STRINGS[lang][key]) || STRINGS.de[key] || key;
  if (vars) {
    Object.entries(vars).forEach(([k, v]) => {
      value = value.replaceAll(`{${k}}`, String(v));
    });
  }
  return value;
}

function applyLanguage() {
  document.documentElement.lang = lang;
  document.querySelectorAll("[data-i18n]").forEach((node) => {
    node.textContent = t(node.dataset.i18n);
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((node) => {
    node.placeholder = t(node.dataset.i18nPlaceholder);
  });
  document.querySelectorAll(".lang-option").forEach((btn) => {
    btn.classList.toggle("is-active", btn.dataset.lang === lang);
  });
  renderResults(currentResults);
  renderDownloads(currentDownloads);
  renderRules(currentRules);
  if (activeDetail) showDetails(activeDetail);
}

/* ── Channels ───────────────────────────────────────────── */

// Fallback only. The real list comes from GET /api/channels, which samples the
// most recent entries upstream so vanished channels age out on their own.
const KNOWN_CHANNELS = [
  "3Sat", "ARD", "ARTE.DE", "ARTE.EN", "ARTE.ES", "ARTE.FR", "ARTE.IT", "ARTE.PL",
  "BR", "DW", "Funk.net", "HR", "KiKA", "MDR", "NDR", "ORF", "PHOENIX",
  "Radio Bremen TV", "RBB", "RBTV", "SR", "SRF", "SWR", "WDR",
  "ZDF", "ZDF-tivi", "ZDFinfo", "ZDFneo",
];

const channelListEl = document.getElementById("channelList");
const seenChannels = new Set(KNOWN_CHANNELS);

function renderChannelList() {
  channelListEl.innerHTML = [...seenChannels]
    .sort((a, b) => a.localeCompare(b, "de"))
    .map((name) => `<option value="${escapeAttribute(name)}"></option>`)
    .join("");
}

function learnChannels(items) {
  let added = false;
  items.forEach((item) => {
    if (item.channel && !seenChannels.has(item.channel)) {
      seenChannels.add(item.channel);
      added = true;
    }
  });
  if (added) renderChannelList();
}

async function refreshChannels() {
  try {
    const response = await fetchJson("/api/channels");
    const items = response.items || [];
    if (items.length >= 5) {
      seenChannels.clear();
      items.forEach((name) => seenChannels.add(name));
      renderChannelList();
    }
  } catch (error) {
    // The bundled fallback list stays in place; not worth bothering anyone about.
  }
}

/* ── Broadcaster colours ────────────────────────────────── */

const CHANNEL_COLORS = {
  ard: "#003c8f", "das erste": "#003c8f", "ard-alpha": "#7b2b8f", one: "#e2001a",
  tagesschau24: "#003c8f",
  zdf: "#fa7d19", "zdf-tivi": "#e5007d",
  zdfneo: "#8f1a5e", zdfinfo: "#0a5aa0", arte: "#ff4b00", "3sat": "#e5006d",
  kika: "#e5007d", phoenix: "#a50034", br: "#0b7ec8", hr: "#00457c",
  mdr: "#007dc5", ndr: "#0c2c57", rbb: "#004b93", sr: "#c8102e",
  swr: "#00a5dc", wdr: "#00519e", "dw": "#0f4c81", orf: "#c8102e",
  srf: "#e30613", funk: "#00d8a0", "radio bremen tv": "#009ee0",
};

function channelColor(name) {
  if (!name) return "#767c85";
  const key = String(name).trim().toLowerCase();
  if (CHANNEL_COLORS[key]) return CHANNEL_COLORS[key];
  // Longest prefix first, so "ard-alpha" is not swallowed by "ard".
  const base = Object.keys(CHANNEL_COLORS)
    .filter((k) => key.startsWith(k))
    .sort((a, b) => b.length - a.length)[0];
  if (base) return CHANNEL_COLORS[base];
  let hash = 0;
  for (let i = 0; i < key.length; i += 1) hash = (hash * 31 + key.charCodeAt(i)) % 360;
  return `hsl(${hash} 45% 42%)`;
}

/* ── Elements ───────────────────────────────────────────── */

const searchForm = document.getElementById("searchForm");
const settingsForm = document.getElementById("settingsForm");
const ruleForm = document.getElementById("ruleForm");
const filesystemImportForm = document.getElementById("filesystemImportForm");
const listImportForm = document.getElementById("listImportForm");

const resultsList = document.getElementById("resultsList");
const downloadList = document.getElementById("downloadList");
const rulesList = document.getElementById("rulesList");
const detailPanel = document.getElementById("detailPanel");
const detailSheet = document.getElementById("detailSheet");
const sheetBackdrop = document.getElementById("sheetBackdrop");
const sheetClose = document.getElementById("sheetClose");
const systemCheckPanel = document.getElementById("systemCheckPanel");
const duplicatesPanel = document.getElementById("duplicatesPanel");
const mediaServerPanel = document.getElementById("mediaServerPanel");

const searchStatus = document.getElementById("searchStatus");
const settingsStatus = document.getElementById("settingsStatus");
const ruleStatus = document.getElementById("ruleStatus");
const importStatus = document.getElementById("importStatus");
const mediaServerStatus = document.getElementById("mediaServerStatus");
const currentDownloadRoot = document.getElementById("currentDownloadRoot");
const searchRssLink = document.getElementById("searchRssLink");
const rootLockedNote = document.getElementById("rootLockedNote");
const rootResetButton = document.getElementById("rootResetButton");

rootResetButton.addEventListener("click", () => {
  settingsForm.elements.download_root.value = rootResetButton.dataset.path || "";
});

const activityBar = document.getElementById("activityBar");
const activityText = document.getElementById("activityText");
const activityPct = document.getElementById("activityPct");
const queueCount = document.getElementById("queueCount");

const resultTemplate = document.getElementById("resultTemplate");
const downloadTemplate = document.getElementById("downloadTemplate");
const ruleTemplate = document.getElementById("ruleTemplate");

let currentResults = [];
let currentDownloads = [];
let currentRules = [];
let currentTotal = 0;
let activeDetail = null;
let hasSearched = false;
let pageSize = Number(localStorage.getItem("mn.pageSize")) || 25;
let pageOffset = 0;

const pageSizeSelect = document.getElementById("pageSize");
const pagerFoot = document.getElementById("pagerFoot");
const pageRange = document.getElementById("pageRange");
const pagePrevButtons = [document.getElementById("pagePrev"), document.getElementById("pagePrevFoot")];
const pageNextButtons = [document.getElementById("pageNext"), document.getElementById("pageNextFoot")];

pageSizeSelect.value = String(pageSize);
pageSizeSelect.addEventListener("change", () => {
  pageSize = Number(pageSizeSelect.value) || 25;
  localStorage.setItem("mn.pageSize", String(pageSize));
  if (hasSearched) runSearch(0);
});

pagePrevButtons.forEach((btn) =>
  btn.addEventListener("click", () => runSearch(Math.max(0, pageOffset - pageSize))),
);
pageNextButtons.forEach((btn) => btn.addEventListener("click", () => runSearch(pageOffset + pageSize)));

/* ── Tabs ───────────────────────────────────────────────── */

function showTab(name) {
  document.querySelectorAll(".tab").forEach((btn) => btn.classList.toggle("is-active", btn.dataset.tab === name));
  document.querySelectorAll(".view").forEach((view) => view.classList.toggle("is-active", view.dataset.view === name));
  window.scrollTo({ top: 0 });
}

document.querySelectorAll(".tab").forEach((btn) => {
  btn.addEventListener("click", () => showTab(btn.dataset.tab));
});

document.querySelectorAll(".lang-option").forEach((btn) => {
  btn.addEventListener("click", () => {
    lang = btn.dataset.lang;
    localStorage.setItem("mn.lang", lang);
    applyLanguage();
  });
});

activityBar.addEventListener("click", () => showTab("queue"));

/* ── Detail sheet ───────────────────────────────────────── */

function openSheet() {
  detailSheet.hidden = false;
  sheetBackdrop.hidden = false;
}

function closeSheet() {
  detailSheet.hidden = true;
  sheetBackdrop.hidden = true;
  activeDetail = null;
}

sheetClose.addEventListener("click", closeSheet);
sheetBackdrop.addEventListener("click", closeSheet);
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !detailSheet.hidden) closeSheet();
});

/* ── Search ─────────────────────────────────────────────── */

searchForm.addEventListener("submit", (event) => {
  event.preventDefault();
  runSearch(0);
});

async function runSearch(offset) {
  pageOffset = Math.max(0, offset);
  hasSearched = true;
  searchStatus.textContent = t("search.running");
  try {
    const response = await fetchJson("/api/search", {
      method: "POST",
      body: JSON.stringify(searchPayloadFromForm()),
    });
    currentResults = response.results || [];
    currentTotal = response.total || 0;
    learnChannels(currentResults);
    renderResults(currentResults);
    updatePager();
    updateSearchRssLink();
    // Jump back to the first row so page 2 does not start mid-list.
    if (pageOffset > 0) resultsList.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    searchStatus.textContent = error.message;
    pagerFoot.hidden = true;
  }
}

function updatePager() {
  // Derive the range from the page window, not from how many rows came back:
  // date filtering happens after paging and can shorten a page.
  const from = currentTotal ? pageOffset + 1 : 0;
  const to = Math.min(pageOffset + pageSize, currentTotal);
  searchStatus.textContent = t("search.hits", { from, to, total: currentTotal });
  pageRange.textContent = searchStatus.textContent;

  const atStart = pageOffset === 0;
  const atEnd = pageOffset + pageSize >= currentTotal;
  pagePrevButtons.forEach((btn) => (btn.disabled = atStart));
  pageNextButtons.forEach((btn) => (btn.disabled = atEnd));
  pagerFoot.hidden = atStart && atEnd;
}

function searchPayloadFromForm() {
  const payload = Object.fromEntries(new FormData(searchForm).entries());
  payload.min_duration_minutes = numberOrNull(payload.min_duration_minutes);
  payload.max_duration_minutes = numberOrNull(payload.max_duration_minutes);
  payload.size = pageSize;
  payload.offset = pageOffset;
  return payload;
}

function renderResults(results) {
  if (!results.length) {
    resultsList.innerHTML = `<p class="empty">${escapeHtml(hasSearched ? t("results.none") : t("results.empty"))}</p>`;
    return;
  }
  resultsList.innerHTML = "";
  results.forEach((item) => {
    const node = resultTemplate.content.firstElementChild.cloneNode(true);
    const color = channelColor(item.channel);
    node.style.setProperty("--channel", color);
    node.querySelector(".row-channel").textContent = item.channel || "—";
    node.querySelector(".row-date").textContent = formatShortDate(item.air_date);
    node.querySelector(".row-dur").textContent = formatDuration(item.duration_seconds);
    const flag = node.querySelector(".row-flag");
    flag.textContent = item.already_present ? t("flag.have") : "";
    flag.classList.toggle("is-dupe", Boolean(item.already_present));
    node.querySelector(".row-title").textContent = item.title || "";
    node.querySelector(".row-topic").textContent = item.topic || "";
    node.querySelector(".row-open").addEventListener("click", () => showDetails(item));
    const act = node.querySelector(".row-act");
    act.addEventListener("click", async () => {
      act.disabled = true;
      await queueDownload(item);
      // A greyed-out arrow reads as "broken". A tick reads as "it is queued".
      act.classList.add("is-done");
      act.innerHTML =
        '<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M5 13l4 4L19 7" /></svg>';
      act.title = t("queue.added");
    });
    resultsList.appendChild(node);
  });
}

function showDetails(item) {
  activeDetail = item;
  const color = channelColor(item.channel);
  const link = (url, label) =>
    url ? `<a href="${escapeAttribute(url)}" target="_blank" rel="noreferrer">${escapeHtml(label)}</a>` : "";

  const preview =
    item.format_hint === "mp4" && item.source_url
      ? `<video class="preview-video" controls preload="metadata" src="${escapeAttribute(item.source_url)}"></video>`
      : `<p class="detail-note">${escapeHtml(t("detail.hlsNote"))}</p>`;

  detailPanel.innerHTML = `
    <p class="detail-meta">
      <span class="detail-channel" style="color:${color}">${escapeHtml(item.channel || "—")}</span>
      <span>${escapeHtml(formatShortDate(item.air_date))}</span>
      <span>${escapeHtml(formatDuration(item.duration_seconds))}</span>
      <span>${escapeHtml(item.quality || "")}</span>
    </p>
    <h2 class="detail-title">${escapeHtml(item.title || "")}</h2>
    ${item.topic ? `<p class="detail-meta"><span>${escapeHtml(item.topic)}</span></p>` : ""}
    <p class="detail-text">${escapeHtml(item.description || t("detail.noDescription"))}</p>
    ${item.already_present ? `<p class="detail-note">${escapeHtml(t("detail.present"))}${item.existing_final_path ? ` · ${escapeHtml(item.existing_final_path)}` : ""}</p>` : ""}
    <div class="detail-links">
      ${link(item.website_url, t("detail.website"))}
      ${link(item.preview_url, t("detail.stream"))}
      ${link(item.source_url, t("detail.source"))}
      ${link(item.subtitle_url, t("detail.subtitles"))}
      ${link(item.infuse_links?.play, t("detail.infusePlay"))}
      ${link(item.infuse_links?.save, t("detail.infuseSave"))}
    </div>
    ${preview}
    <div class="detail-actions">
      <button type="button" class="btn btn-primary" id="sheetDownload">${escapeHtml(t("detail.download"))}</button>
      <button type="button" class="btn btn-ghost" id="sheetRule">${escapeHtml(t("detail.makeRule"))}</button>
    </div>
  `;
  document.getElementById("sheetDownload").addEventListener("click", async () => {
    await queueDownload(item);
    closeSheet();
    showTab("queue");
  });
  document.getElementById("sheetRule").addEventListener("click", () => {
    prefillRuleForm(item);
    closeSheet();
    showTab("rules");
  });
  openSheet();
}

/* ── Downloads ──────────────────────────────────────────── */

async function queueDownload(item) {
  try {
    const response = await fetchJson("/api/downloads", { method: "POST", body: JSON.stringify(item) });
    if (response.duplicate_detected) window.alert(t("dupe.exists"));
    await refreshDownloads();
  } catch (error) {
    window.alert(`${t("error.download")}: ${error.message}`);
  }
}

function renderDownloads(items) {
  currentDownloads = items;
  updateActivity(items);

  if (!items.length) {
    downloadList.innerHTML = `<p class="empty">${escapeHtml(t("queue.empty"))}</p>`;
    return;
  }
  downloadList.innerHTML = "";
  items.forEach((item) => {
    const node = downloadTemplate.content.firstElementChild.cloneNode(true);
    const pct = Math.max(0, Math.min(100, Math.round(item.progress || 0)));
    node.style.setProperty("--channel", channelColor(item.channel));
    node.classList.toggle("is-live", item.status === "downloading");
    node.querySelector(".row-bar-fill").style.height = `${pct}%`;
    node.querySelector(".row-channel").textContent = item.channel || "—";
    node.querySelector(".dl-state").textContent = t(`status.${item.status}`);
    node.querySelector(".dl-pct").textContent = item.status === "completed" ? "" : `${pct}%`;
    node.querySelector(".row-title").textContent = item.title || "";
    node.querySelector(".dl-path").textContent = item.final_path || `${item.target_directory}/${item.filename}`;
    node.querySelector(".dl-error").textContent =
      item.error_message || (item.duplicate_of ? `#${item.duplicate_of.id}: ${item.duplicate_of.title}` : "");

    const retry = node.querySelector(".dl-retry");
    const cancel = node.querySelector(".dl-cancel");
    const del = node.querySelector(".dl-delete");
    retry.disabled = !["failed", "canceled"].includes(item.status);
    cancel.disabled = !["queued", "downloading"].includes(item.status);
    del.disabled = ["queued", "downloading"].includes(item.status);
    del.addEventListener("click", async () => {
      if (!window.confirm(t("queue.delete"))) return;
      await fetch(`/api/downloads/${item.id}`, { method: "DELETE" });
      await refreshDownloads();
    });
    retry.addEventListener("click", async () => {
      await fetchJson(`/api/downloads/${item.id}/retry`, { method: "POST" });
      await refreshDownloads();
    });
    cancel.addEventListener("click", async () => {
      await fetchJson(`/api/downloads/${item.id}/cancel`, { method: "POST" });
      await refreshDownloads();
    });
    node.querySelector(".row-open").addEventListener("click", () => {});
    downloadList.appendChild(node);
  });
}

function updateActivity(items) {
  const running = items.filter((i) => i.status === "downloading");
  const queued = items.filter((i) => i.status === "queued");
  const active = running.length + queued.length;

  queueCount.hidden = active === 0;
  queueCount.textContent = String(active);

  if (!running.length && !queued.length) {
    activityBar.hidden = true;
    return;
  }
  const avg = running.length
    ? Math.round(running.reduce((sum, i) => sum + (i.progress || 0), 0) / running.length)
    : 0;
  const parts = [];
  if (running.length) parts.push(t("activity.running", { n: running.length }));
  if (queued.length) parts.push(t("activity.queued", { n: queued.length }));
  activityText.textContent = `${parts.join(" · ")}${running.length ? ` — ${running[0].title}` : ""}`;
  activityPct.textContent = running.length ? `${avg}%` : "";
  activityBar.hidden = false;
}

/* ── Rules ──────────────────────────────────────────────── */

ruleForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  ruleStatus.textContent = t("rules.saving");
  const formData = new FormData(ruleForm);
  const payload = Object.fromEntries(formData.entries());
  payload.keep_latest = numberOrNull(payload.keep_latest);
  payload.interval_minutes = numberOrNull(payload.interval_minutes) || 180;
  payload.auto_download = formData.get("auto_download") === "on";
  try {
    await fetchJson("/api/rules", { method: "POST", body: JSON.stringify(payload) });
    ruleForm.reset();
    document.getElementById("ruleFormBox").open = false;
    ruleStatus.textContent = t("rules.saved");
    await refreshRules();
  } catch (error) {
    ruleStatus.textContent = error.message;
  }
});

function renderRules(items) {
  currentRules = items;
  if (!items.length) {
    rulesList.innerHTML = `<p class="empty">${escapeHtml(t("rules.empty"))}</p>`;
    return;
  }
  rulesList.innerHTML = "";
  items.forEach((item) => {
    const node = ruleTemplate.content.firstElementChild.cloneNode(true);
    node.style.setProperty("--channel", channelColor(item.channel));
    const state = node.querySelector(".rule-state");
    state.textContent = item.enabled ? t("rules.active") : t("rules.paused");
    state.classList.toggle("is-off", !item.enabled);
    node.querySelector(".rule-interval").textContent = t("rules.every", { n: item.interval_minutes });
    node.querySelector(".rule-hits").textContent = `${item.auto_download ? t("rules.autoOn") : t("rules.autoOff")} · ${t("rules.hits", { n: item.match_count || 0 })}`;
    node.querySelector(".rule-title").textContent = item.name;
    node.querySelector(".rule-query").textContent = [item.query, item.channel, item.topic].filter(Boolean).join(" · ");
    node.querySelector(".rule-history").textContent = item.last_run_at
      ? t("rules.last", { when: formatDateTime(item.last_run_at) }) + (item.last_error ? ` · ${item.last_error}` : "")
      : t("rules.never");
    node.querySelector(".rule-rss").href = `/api/rss/rules/${item.id}`;
    node.querySelector(".rule-run").addEventListener("click", async () => {
      ruleStatus.textContent = t("rules.checking", { name: item.name });
      const response = await fetchJson(`/api/rules/${item.id}/run`, {
        method: "POST",
        body: JSON.stringify({ limit: 15 }),
      });
      ruleStatus.textContent = t("rules.result", { matches: response.new_matches || 0, downloads: response.queued_downloads || 0 });
      await refreshRules();
      await refreshDownloads();
    });
    rulesList.appendChild(node);
  });
}

function prefillRuleForm(item) {
  ruleForm.elements.name.value = item.title || "";
  ruleForm.elements.query.value = item.topic || item.title || "";
  ruleForm.elements.channel.value = item.channel || "";
  ruleForm.elements.topic.value = item.topic || "";
  ruleForm.elements.quality.value = !item.quality || item.quality === "unknown" ? "best" : item.quality;
  ruleForm.elements.folder_template.value = "{channel}/{topic}";
  ruleForm.elements.filename_template.value = "{date}_{title}";
  ruleForm.elements.interval_minutes.value = 180;
  document.getElementById("ruleFormBox").open = true;
  ruleStatus.textContent = t("rules.prefilled");
}

document.getElementById("runAllRulesButton").addEventListener("click", () =>
  runRulesAction("/api/rules/run-all", t("rules.checkAll")),
);
document.getElementById("runDueRulesButton").addEventListener("click", () =>
  runRulesAction("/api/rules/run-due", t("rules.checkDue")),
);

async function runRulesAction(endpoint, pendingText) {
  ruleStatus.textContent = pendingText;
  try {
    const response = await fetchJson(endpoint, { method: "POST", body: JSON.stringify({ limit: 15 }) });
    const summary = (response.items || []).reduce(
      (acc, item) => {
        acc.matches += item.new_matches || 0;
        acc.downloads += item.queued_downloads || 0;
        return acc;
      },
      { matches: 0, downloads: 0 },
    );
    ruleStatus.textContent = t("rules.result", summary);
    await refreshRules();
    await refreshDownloads();
  } catch (error) {
    ruleStatus.textContent = error.message;
  }
}

/* ── Settings ───────────────────────────────────────────── */

settingsForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  settingsStatus.textContent = t("setup.saving");
  const f = new FormData(settingsForm);
  const on = (k) => f.get(k) === "on";
  const payload = {
    download_root: f.get("download_root"),
    concurrent_downloads: numberOrNull(f.get("concurrent_downloads")),
    max_retries: numberOrNull(f.get("max_retries")),
    rule_run_limit: numberOrNull(f.get("rule_run_limit")),
    filename_template: f.get("filename_template"),
    subfolder_template: f.get("subfolder_template"),
    skip_duplicates: on("skip_duplicates"),
    scheduler_enabled: on("scheduler_enabled"),
    create_nfo_sidecar: on("create_nfo_sidecar"),
    create_json_sidecar: on("create_json_sidecar"),
    plex_enabled: on("plex_enabled"),
    plex_base_url: f.get("plex_base_url"),
    plex_token: f.get("plex_token"),
    plex_library_section: f.get("plex_library_section"),
    plex_auto_scan: on("plex_auto_scan"),
    jellyfin_enabled: on("jellyfin_enabled"),
    jellyfin_base_url: f.get("jellyfin_base_url"),
    jellyfin_api_key: f.get("jellyfin_api_key"),
    jellyfin_library_id: f.get("jellyfin_library_id"),
    jellyfin_auto_scan: on("jellyfin_auto_scan"),
    infuse_enabled: on("infuse_enabled"),
  };
  try {
    applySettings(await fetchJson("/api/settings", { method: "PUT", body: JSON.stringify(payload) }));
    settingsStatus.textContent = t("setup.saved");
    await refreshMediaServers();
  } catch (error) {
    settingsStatus.textContent = error.message;
  }
});

function applySettings(settings) {
  const el = settingsForm.elements;
  currentDownloadRoot.textContent = settings.download_root;
  el.download_root.value = settings.download_root;
  el.concurrent_downloads.value = settings.concurrent_downloads;
  el.max_retries.value = settings.max_retries;
  el.rule_run_limit.value = settings.rule_run_limit;
  el.filename_template.value = settings.filename_template;
  el.subfolder_template.value = settings.subfolder_template;
  el.skip_duplicates.checked = Boolean(settings.skip_duplicates);
  el.scheduler_enabled.checked = Boolean(settings.scheduler_enabled);
  el.create_nfo_sidecar.checked = Boolean(settings.create_nfo_sidecar);
  el.create_json_sidecar.checked = Boolean(settings.create_json_sidecar);
  el.plex_enabled.checked = Boolean(settings.plex_enabled);
  el.plex_base_url.value = settings.plex_base_url || "";
  el.plex_token.value = settings.plex_token || "";
  el.plex_library_section.value = settings.plex_library_section || "";
  el.plex_auto_scan.checked = Boolean(settings.plex_auto_scan);
  el.jellyfin_enabled.checked = Boolean(settings.jellyfin_enabled);
  el.jellyfin_base_url.value = settings.jellyfin_base_url || "";
  el.jellyfin_api_key.value = settings.jellyfin_api_key || "";
  el.jellyfin_library_id.value = settings.jellyfin_library_id || "";
  el.jellyfin_auto_scan.checked = Boolean(settings.jellyfin_auto_scan);
  el.infuse_enabled.checked = Boolean(settings.infuse_enabled);

  // The container environment supplies the starting value; the user stays in
  // control and may point the app at any other writable mounted path.
  const containerRoot = (settings.container_defaults || {}).download_root;
  if (containerRoot && containerRoot !== settings.download_root) {
    rootResetButton.textContent = t("field.rootReset", { path: containerRoot });
    rootResetButton.dataset.path = containerRoot;
    rootLockedNote.hidden = false;
  } else {
    rootLockedNote.hidden = true;
  }
}

/* ── Imports ────────────────────────────────────────────── */

filesystemImportForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  importStatus.textContent = t("import.running");
  const f = new FormData(filesystemImportForm);
  try {
    const response = await fetchJson("/api/imports/filesystem", {
      method: "POST",
      body: JSON.stringify({ source_path: f.get("source_path"), max_files: numberOrNull(f.get("max_files")) || 500 }),
    });
    importStatus.textContent = t("import.done", { imported: response.imported, skipped: response.skipped });
    await refreshDownloads();
    await refreshDuplicates();
  } catch (error) {
    importStatus.textContent = error.message;
  }
});

listImportForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  importStatus.textContent = t("import.running");
  const f = new FormData(listImportForm);
  try {
    const response = await fetchJson("/api/imports/list", {
      method: "POST",
      body: JSON.stringify({ source_path: f.get("source_path") }),
    });
    importStatus.textContent = t("import.done", { imported: response.imported, skipped: response.skipped });
    await refreshDownloads();
    await refreshDuplicates();
  } catch (error) {
    importStatus.textContent = error.message;
  }
});

/* ── Media servers, checks, duplicates ──────────────────── */

document.getElementById("scanMediaServersButton").addEventListener("click", async () => {
  mediaServerStatus.textContent = t("setup.scanning");
  try {
    const response = await fetchJson("/api/media-servers/scan", { method: "POST" });
    mediaServerStatus.textContent = Object.entries(response)
      .map(([name, item]) => `${name}: ${item.label}`)
      .join(" · ");
    await refreshMediaServers();
  } catch (error) {
    mediaServerStatus.textContent = error.message;
  }
});

function renderMediaServers(payload) {
  const items = [
    { name: "Plex", ...payload.plex },
    { name: "Jellyfin", ...payload.jellyfin },
    { name: "Infuse", ...payload.infuse },
  ];
  mediaServerPanel.innerHTML = items
    .map(
      (item) => `<div class="check-row"><span class="check-dot ${escapeAttribute(item.status || "manual")}"></span>
        <span><strong>${escapeHtml(item.name)}</strong> · ${escapeHtml(item.label || "")}</span></div>`,
    )
    .join("");
}

function renderSystemCheck(payload) {
  const summary = payload.summary || {};
  const row = (item) =>
    `<div class="check-row"><span class="check-dot ${escapeAttribute(item.status || "manual")}"></span><span>${escapeHtml(item.label)}</span></div>`;
  const identity =
    summary.uid !== undefined
      ? `<p class="identity-line">user: "${summary.uid}:${summary.gid}"</p>`
      : "";
  systemCheckPanel.innerHTML = `
    <p class="checks-head">${escapeHtml(t("sys.containerChecks"))} — ${summary.ok_count || 0}/${summary.total_checks || 0} · ${escapeHtml(summary.architecture || "")}</p>
    ${identity}
    ${(payload.checks || []).map(row).join("")}
    <p class="checks-head">${escapeHtml(t("sys.manualChecks"))}</p>
    ${(payload.host_prerequisites || []).map(row).join("")}
  `;
}

function renderDuplicates(groups) {
  if (!groups.length) {
    duplicatesPanel.innerHTML = `<p class="inline-status">${escapeHtml(t("dupes.none"))}</p>`;
    return;
  }
  duplicatesPanel.innerHTML = groups
    .slice(0, 8)
    .map(
      (group) => `<p class="checks-head">${escapeHtml(t("dupes.group", { n: group.item_count }))}</p>` +
        group.items
          .map(
            (item) => `<div class="check-row"><span class="check-dot warning"></span>
              <span>${escapeHtml(item.title)} · ${escapeHtml(formatShortDate(item.air_date))}</span></div>`,
          )
          .join(""),
    )
    .join("");
}

/* ── Refreshers ─────────────────────────────────────────── */

async function refreshDownloads() {
  try {
    renderDownloads((await fetchJson("/api/downloads")).items || []);
  } catch (error) {
    downloadList.innerHTML = `<p class="empty">${escapeHtml(error.message)}</p>`;
  }
}

async function refreshRules() {
  try {
    renderRules((await fetchJson("/api/rules")).items || []);
  } catch (error) {
    rulesList.innerHTML = `<p class="empty">${escapeHtml(error.message)}</p>`;
  }
}

async function refreshSettings() {
  try {
    applySettings(await fetchJson("/api/settings"));
  } catch (error) {
    settingsStatus.textContent = error.message;
  }
}

async function refreshSystemCheck() {
  try {
    renderSystemCheck(await fetchJson("/api/system-check"));
  } catch (error) {
    systemCheckPanel.innerHTML = `<p class="inline-status">${escapeHtml(error.message)}</p>`;
  }
}

async function refreshDuplicates() {
  try {
    renderDuplicates((await fetchJson("/api/duplicates")).items || []);
  } catch (error) {
    duplicatesPanel.innerHTML = `<p class="inline-status">${escapeHtml(error.message)}</p>`;
  }
}

async function refreshMediaServers() {
  try {
    renderMediaServers(await fetchJson("/api/media-servers/status"));
  } catch (error) {
    mediaServerPanel.innerHTML = `<p class="inline-status">${escapeHtml(error.message)}</p>`;
  }
}

function updateSearchRssLink() {
  const params = new URLSearchParams();
  Object.entries(searchPayloadFromForm()).forEach(([key, value]) => {
    if (value !== null && value !== "" && !["size", "offset"].includes(key)) params.set(key, String(value));
  });
  searchRssLink.href = `/api/rss/search?${params.toString()}`;
}

/* ── Helpers ────────────────────────────────────────────── */

function formatDuration(seconds) {
  if (!seconds) return t("unit.unknown");
  return `${Math.round(seconds / 60)} ${t("unit.min")}`;
}

function formatShortDate(value) {
  if (!value) return "—";
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  return date.toLocaleDateString(lang === "en" ? "en-GB" : "de-DE", { day: "2-digit", month: "2-digit" });
}

function formatDateTime(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString(lang === "en" ? "en-GB" : "de-DE");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

const escapeAttribute = escapeHtml;

function numberOrNull(value) {
  if (value === "" || value === null || value === undefined) return null;
  const parsed = Number(value);
  return Number.isNaN(parsed) ? null : parsed;
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, { headers: { "Content-Type": "application/json" }, ...options });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(payload.detail || `HTTP ${response.status}`);
  return payload;
}

/* ── Boot ───────────────────────────────────────────────── */

applyLanguage();
renderChannelList();
refreshChannels();
refreshSettings();
refreshDownloads();
refreshRules();
refreshSystemCheck();
refreshDuplicates();
refreshMediaServers();
updateSearchRssLink();

setInterval(refreshDownloads, 4000);
setInterval(refreshRules, 20000);
setInterval(refreshSystemCheck, 60000);
setInterval(refreshDuplicates, 30000);
setInterval(refreshMediaServers, 60000);
