const searchForm = document.getElementById("searchForm");
const settingsForm = document.getElementById("settingsForm");
const ruleForm = document.getElementById("ruleForm");
const filesystemImportForm = document.getElementById("filesystemImportForm");
const listImportForm = document.getElementById("listImportForm");
const resultsList = document.getElementById("resultsList");
const downloadList = document.getElementById("downloadList");
const rulesList = document.getElementById("rulesList");
const detailPanel = document.getElementById("detailPanel");
const systemCheckPanel = document.getElementById("systemCheckPanel");
const duplicatesPanel = document.getElementById("duplicatesPanel");
const mediaServerPanel = document.getElementById("mediaServerPanel");
const resultCount = document.getElementById("resultCount");
const searchStatus = document.getElementById("searchStatus");
const settingsStatus = document.getElementById("settingsStatus");
const ruleStatus = document.getElementById("ruleStatus");
const importStatus = document.getElementById("importStatus");
const mediaServerStatus = document.getElementById("mediaServerStatus");
const currentDownloadRoot = document.getElementById("currentDownloadRoot");
const runAllRulesButton = document.getElementById("runAllRulesButton");
const runDueRulesButton = document.getElementById("runDueRulesButton");
const scanMediaServersButton = document.getElementById("scanMediaServersButton");
const searchRssLink = document.getElementById("searchRssLink");

const resultTemplate = document.getElementById("resultTemplate");
const downloadTemplate = document.getElementById("downloadTemplate");
const ruleTemplate = document.getElementById("ruleTemplate");

let currentResults = [];

searchForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  searchStatus.textContent = "Suche laeuft ...";
  const payload = searchPayloadFromForm();

  try {
    const response = await fetchJson("/api/search", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    currentResults = response.results || [];
    renderResults(currentResults);
    resultCount.textContent = `${response.total || 0} Treffer`;
    searchStatus.textContent = `${currentResults.length} Eintraege geladen.`;
    updateSearchRssLink();
    if (currentResults.length) {
      showDetails(currentResults[0]);
    }
  } catch (error) {
    searchStatus.textContent = error.message;
  }
});

settingsForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  settingsStatus.textContent = "Speichere ...";
  const formData = new FormData(settingsForm);
  const payload = {
    download_root: formData.get("download_root"),
    concurrent_downloads: numberOrNull(formData.get("concurrent_downloads")),
    max_retries: numberOrNull(formData.get("max_retries")),
    skip_duplicates: formData.get("skip_duplicates") === "on",
    scheduler_enabled: formData.get("scheduler_enabled") === "on",
    filename_template: formData.get("filename_template"),
    subfolder_template: formData.get("subfolder_template"),
    create_nfo_sidecar: formData.get("create_nfo_sidecar") === "on",
    create_json_sidecar: formData.get("create_json_sidecar") === "on",
    rule_run_limit: numberOrNull(formData.get("rule_run_limit")),
    plex_enabled: formData.get("plex_enabled") === "on",
    plex_base_url: formData.get("plex_base_url"),
    plex_token: formData.get("plex_token"),
    plex_library_section: formData.get("plex_library_section"),
    plex_auto_scan: formData.get("plex_auto_scan") === "on",
    jellyfin_enabled: formData.get("jellyfin_enabled") === "on",
    jellyfin_base_url: formData.get("jellyfin_base_url"),
    jellyfin_api_key: formData.get("jellyfin_api_key"),
    jellyfin_library_id: formData.get("jellyfin_library_id"),
    jellyfin_auto_scan: formData.get("jellyfin_auto_scan") === "on",
    infuse_enabled: formData.get("infuse_enabled") === "on",
  };

  try {
    const response = await fetchJson("/api/settings", {
      method: "PUT",
      body: JSON.stringify(payload),
    });
    applySettings(response);
    settingsStatus.textContent = "Einstellungen gespeichert.";
    await refreshMediaServers();
  } catch (error) {
    settingsStatus.textContent = error.message;
  }
});

ruleForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  ruleStatus.textContent = "Speichere Regel ...";
  const formData = new FormData(ruleForm);
  const payload = Object.fromEntries(formData.entries());
  payload.keep_latest = numberOrNull(payload.keep_latest);
  payload.interval_minutes = numberOrNull(payload.interval_minutes) || 180;
  payload.auto_download = formData.get("auto_download") === "on";

  try {
    await fetchJson("/api/rules", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    ruleForm.reset();
    ruleStatus.textContent = "Regel gespeichert.";
    await refreshRules();
  } catch (error) {
    ruleStatus.textContent = error.message;
  }
});

filesystemImportForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  importStatus.textContent = "Lese vorhandene Dateien ein ...";
  const formData = new FormData(filesystemImportForm);
  try {
    const response = await fetchJson("/api/imports/filesystem", {
      method: "POST",
      body: JSON.stringify({
        source_path: formData.get("source_path"),
        max_files: numberOrNull(formData.get("max_files")) || 500,
      }),
    });
    importStatus.textContent = `${response.imported} Dateien importiert, ${response.skipped} uebersprungen.`;
    await refreshDownloads();
    await refreshDuplicates();
  } catch (error) {
    importStatus.textContent = error.message;
  }
});

listImportForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  importStatus.textContent = "Importiere Liste ...";
  const formData = new FormData(listImportForm);
  try {
    const response = await fetchJson("/api/imports/list", {
      method: "POST",
      body: JSON.stringify({ source_path: formData.get("source_path") }),
    });
    importStatus.textContent = `${response.imported} Eintraege importiert, ${response.skipped} uebersprungen.`;
    await refreshDownloads();
    await refreshDuplicates();
  } catch (error) {
    importStatus.textContent = error.message;
  }
});

runAllRulesButton.addEventListener("click", async () => {
  await runRulesAction("/api/rules/run-all", "Pruefe alle Regeln ...");
});

runDueRulesButton.addEventListener("click", async () => {
  await runRulesAction("/api/rules/run-due", "Fuehre faellige Regeln aus ...");
});

scanMediaServersButton.addEventListener("click", async () => {
  mediaServerStatus.textContent = "Stosse Aktualisierung an ...";
  try {
    const response = await fetchJson("/api/media-servers/scan", { method: "POST" });
    mediaServerStatus.textContent = summarizeMediaServerScan(response);
    await refreshMediaServers();
  } catch (error) {
    mediaServerStatus.textContent = error.message;
  }
});

function searchPayloadFromForm() {
  const formData = new FormData(searchForm);
  const payload = Object.fromEntries(formData.entries());
  payload.min_duration_minutes = numberOrNull(payload.min_duration_minutes);
  payload.max_duration_minutes = numberOrNull(payload.max_duration_minutes);
  payload.size = 25;
  payload.offset = 0;
  return payload;
}

function renderResults(results) {
  if (!results.length) {
    resultsList.className = "results-list empty-state";
    resultsList.textContent = "Keine Treffer gefunden.";
    return;
  }

  resultsList.className = "results-list";
  resultsList.innerHTML = "";

  results.forEach((item) => {
    const node = resultTemplate.content.firstElementChild.cloneNode(true);
    node.querySelector(".result-channel").textContent = item.channel || "Unbekannt";
    node.querySelector(".result-date").textContent = item.air_date || "Ohne Datum";
    node.querySelector(".result-quality").textContent = item.quality || "n/a";
    node.querySelector(".result-title").textContent = item.title;
    node.querySelector(".result-topic").textContent = item.topic || "";
    node.querySelector(".result-description").textContent = item.description || "Keine Kurzbeschreibung";
    node.querySelector(".result-duration").textContent = formatDuration(item.duration_seconds);
    node.querySelector(".result-presence").textContent = item.already_present
      ? `Schon vorhanden · ${translateStatus(item.existing_status || "completed")}`
      : "Neu";
    node.querySelector(".details-button").addEventListener("click", () => showDetails(item));
    node.querySelector(".download-button").addEventListener("click", () => queueDownload(item));
    node.querySelector(".rule-button").addEventListener("click", () => prefillRuleForm(item));
    resultsList.appendChild(node);
  });
}

function showDetails(item) {
  const websiteAction = item.website_url
    ? `<a class="action-link" href="${escapeAttribute(item.website_url)}" target="_blank" rel="noreferrer">Zur Mediathek</a>`
    : "";
  const previewAction = item.preview_url
    ? `<a class="action-link" href="${escapeAttribute(item.preview_url)}" target="_blank" rel="noreferrer">Stream / Vorschau</a>`
    : "";
  const sourceAction = item.source_url
    ? `<a class="action-link" href="${escapeAttribute(item.source_url)}" target="_blank" rel="noreferrer">Direkte Quelle</a>`
    : "";
  const subtitleAction = item.subtitle_url
    ? `<a class="action-link" href="${escapeAttribute(item.subtitle_url)}" target="_blank" rel="noreferrer">Untertitel</a>`
    : "";
  const infusePlayAction = item.infuse_links?.play
    ? `<a class="action-link" href="${escapeAttribute(item.infuse_links.play)}">In Infuse abspielen</a>`
    : "";
  const infuseSaveAction = item.infuse_links?.save
    ? `<a class="action-link" href="${escapeAttribute(item.infuse_links.save)}">In Infuse merken</a>`
    : "";
  const duplicateNote = item.already_present
    ? `<p class="detail-meta">Bereits vorhanden${item.existing_final_path ? ` · ${escapeHtml(item.existing_final_path)}` : ""}</p>`
    : "";
  const videoPreview =
    item.format_hint === "mp4"
      ? `<video class="preview-video" controls preload="metadata" src="${escapeAttribute(item.source_url)}"></video>`
      : `<div class="preview-note">Direktes Inline-Preview ist vor allem fuer MP4 sinnvoll. HLS und andere Formate oeffnen wir ueber den Stream-Link.</div>`;

  detailPanel.className = "detail-card";
  detailPanel.innerHTML = `
    <div class="detail-topline">
      <span class="badge">${escapeHtml(item.channel || "Unbekannt")}</span>
      <span class="badge">${escapeHtml(item.air_date || "Ohne Datum")}</span>
      <span class="badge">${escapeHtml(item.quality || "n/a")}</span>
    </div>
    <h3 class="detail-title">${escapeHtml(item.title)}</h3>
    <p class="detail-description">${escapeHtml(item.description || "Keine Beschreibung vorhanden.")}</p>
    <p class="detail-meta">${escapeHtml(item.topic || "Ohne Thema")} · ${escapeHtml(formatDuration(item.duration_seconds))} · Format: ${escapeHtml(item.format_hint || "unbekannt")}</p>
    ${duplicateNote}
    <div class="detail-actions">
      ${websiteAction}
      ${previewAction}
      ${sourceAction}
      ${subtitleAction}
      ${infusePlayAction}
      ${infuseSaveAction}
    </div>
    ${videoPreview}
    <div class="detail-actions">
      <button id="detailDownloadButton" type="button">Auf NAS laden</button>
      <button id="detailRuleButton" type="button" class="button-secondary">Als Regel uebernehmen</button>
    </div>
  `;
  document.getElementById("detailDownloadButton").addEventListener("click", () => queueDownload(item));
  document.getElementById("detailRuleButton").addEventListener("click", () => prefillRuleForm(item));
}

function prefillRuleForm(item) {
  ruleForm.elements.name.value = item.title;
  ruleForm.elements.query.value = item.title;
  ruleForm.elements.channel.value = item.channel || "";
  ruleForm.elements.topic.value = item.topic || "";
  ruleForm.elements.quality.value = item.quality === "unknown" ? "best" : item.quality;
  ruleForm.elements.folder_template.value = "{channel}/{topic}";
  ruleForm.elements.filename_template.value = "{date}_{title}";
  ruleForm.elements.interval_minutes.value = 180;
  ruleStatus.textContent = "Regel aus dem Treffer vorbelegt. Du kannst sie jetzt speichern.";
  ruleForm.scrollIntoView({ behavior: "smooth", block: "center" });
}

async function queueDownload(item) {
  try {
    const response = await fetchJson("/api/downloads", {
      method: "POST",
      body: JSON.stringify(item),
    });
    if (response.duplicate_detected) {
      window.alert("Der Eintrag ist bereits vorhanden und wurde nicht erneut angelegt.");
    }
    await refreshDownloads();
    await refreshDuplicates();
  } catch (error) {
    window.alert(`Download konnte nicht angelegt werden: ${error.message}`);
  }
}

async function refreshDownloads() {
  try {
    const response = await fetchJson("/api/downloads");
    renderDownloads(response.items || []);
  } catch (error) {
    downloadList.className = "download-list empty-state";
    downloadList.textContent = error.message;
  }
}

async function refreshRules() {
  try {
    const response = await fetchJson("/api/rules");
    renderRules(response.items || []);
  } catch (error) {
    rulesList.className = "rules-list empty-state";
    rulesList.textContent = error.message;
  }
}

async function refreshSettings() {
  try {
    const response = await fetchJson("/api/settings");
    applySettings(response);
  } catch (error) {
    settingsStatus.textContent = error.message;
  }
}

async function refreshSystemCheck() {
  try {
    const response = await fetchJson("/api/system-check");
    renderSystemCheck(response);
  } catch (error) {
    systemCheckPanel.className = "empty-state";
    systemCheckPanel.textContent = error.message;
  }
}

async function refreshDuplicates() {
  try {
    const response = await fetchJson("/api/duplicates");
    renderDuplicates(response.items || []);
  } catch (error) {
    duplicatesPanel.className = "empty-state";
    duplicatesPanel.textContent = error.message;
  }
}

async function refreshMediaServers() {
  try {
    const response = await fetchJson("/api/media-servers/status");
    renderMediaServers(response);
  } catch (error) {
    mediaServerPanel.className = "empty-state";
    mediaServerPanel.textContent = error.message;
  }
}

function applySettings(settings) {
  currentDownloadRoot.textContent = settings.download_root;
  settingsForm.elements.download_root.value = settings.download_root;
  settingsForm.elements.concurrent_downloads.value = settings.concurrent_downloads;
  settingsForm.elements.max_retries.value = settings.max_retries;
  settingsForm.elements.skip_duplicates.checked = Boolean(settings.skip_duplicates);
  settingsForm.elements.filename_template.value = settings.filename_template;
  settingsForm.elements.subfolder_template.value = settings.subfolder_template;
  settingsForm.elements.rule_run_limit.value = settings.rule_run_limit;
  settingsForm.elements.scheduler_enabled.checked = Boolean(settings.scheduler_enabled);
  settingsForm.elements.create_nfo_sidecar.checked = Boolean(settings.create_nfo_sidecar);
  settingsForm.elements.create_json_sidecar.checked = Boolean(settings.create_json_sidecar);
  settingsForm.elements.plex_enabled.checked = Boolean(settings.plex_enabled);
  settingsForm.elements.plex_base_url.value = settings.plex_base_url || "";
  settingsForm.elements.plex_token.value = settings.plex_token || "";
  settingsForm.elements.plex_library_section.value = settings.plex_library_section || "";
  settingsForm.elements.plex_auto_scan.checked = Boolean(settings.plex_auto_scan);
  settingsForm.elements.jellyfin_enabled.checked = Boolean(settings.jellyfin_enabled);
  settingsForm.elements.jellyfin_base_url.value = settings.jellyfin_base_url || "";
  settingsForm.elements.jellyfin_api_key.value = settings.jellyfin_api_key || "";
  settingsForm.elements.jellyfin_library_id.value = settings.jellyfin_library_id || "";
  settingsForm.elements.jellyfin_auto_scan.checked = Boolean(settings.jellyfin_auto_scan);
  settingsForm.elements.infuse_enabled.checked = Boolean(settings.infuse_enabled);
}

function renderDownloads(items) {
  if (!items.length) {
    downloadList.className = "download-list empty-state";
    downloadList.textContent = "Noch keine Downloads vorhanden.";
    return;
  }

  downloadList.className = "download-list";
  downloadList.innerHTML = "";

  items.forEach((item) => {
    const node = downloadTemplate.content.firstElementChild.cloneNode(true);
    node.querySelector(".download-title").textContent = item.title;
    node.querySelector(".download-status").textContent = translateStatus(item.status);
    node.querySelector(".download-path").textContent = item.final_path || `${item.target_directory}/${item.filename}`;
    node.querySelector(".download-meta").textContent = [
      item.channel || "Ohne Sender",
      `${Math.round(item.progress || 0)}%`,
      `Retry ${item.retry_count || 0}/${item.max_retries || 0}`,
      item.imported ? "Import" : "",
      item.is_duplicate ? "Duplikat" : "",
    ]
      .filter(Boolean)
      .join(" · ");
    node.querySelector(".download-error").textContent =
      item.error_message || (item.duplicate_of ? `Vorhanden als #${item.duplicate_of.id}: ${item.duplicate_of.title}` : "");
    node.querySelector(".progress-bar").style.width = `${Math.max(0, Math.min(100, item.progress || 0))}%`;
    const retryButton = node.querySelector(".retry-button");
    const cancelButton = node.querySelector(".cancel-button");
    retryButton.disabled = !["failed", "canceled"].includes(item.status);
    cancelButton.disabled = !["queued", "downloading"].includes(item.status);
    retryButton.addEventListener("click", async () => {
      await fetchJson(`/api/downloads/${item.id}/retry`, { method: "POST" });
      await refreshDownloads();
    });
    cancelButton.addEventListener("click", async () => {
      await fetchJson(`/api/downloads/${item.id}/cancel`, { method: "POST" });
      await refreshDownloads();
    });
    downloadList.appendChild(node);
  });
}

function renderRules(items) {
  if (!items.length) {
    rulesList.className = "rules-list empty-state";
    rulesList.textContent = "Noch keine Regeln vorhanden.";
    return;
  }

  rulesList.className = "rules-list";
  rulesList.innerHTML = "";

  items.forEach((item) => {
    const node = ruleTemplate.content.firstElementChild.cloneNode(true);
    node.querySelector(".rule-title").textContent = item.name;
    node.querySelector(".rule-query").textContent =
      [item.query, item.channel && `Sender: ${item.channel}`, item.topic && `Thema: ${item.topic}`]
        .filter(Boolean)
        .join(" · ");
    node.querySelector(".rule-state").textContent = item.enabled ? "Aktiv" : "Pausiert";
    node.querySelector(".rule-meta").textContent =
      `Alle ${item.interval_minutes} Min. · Auto-Download: ${item.auto_download ? "an" : "aus"} · Treffer: ${item.match_count || 0}`;
    node.querySelector(".rule-history").textContent =
      item.last_run_at
        ? `Zuletzt geprueft: ${formatDateTime(item.last_run_at)}${item.last_error ? ` · Fehler: ${item.last_error}` : ""}`
        : "Noch nie ausgefuehrt.";
    node.querySelector(".rule-rss-link").href = `/api/rss/rules/${item.id}`;

    node.querySelector(".run-rule-button").addEventListener("click", async () => {
      ruleStatus.textContent = `Pruefe Regel ${item.name} ...`;
      const response = await fetchJson(`/api/rules/${item.id}/run`, {
        method: "POST",
        body: JSON.stringify({ limit: 15 }),
      });
      ruleStatus.textContent = `${response.new_matches} neue Treffer fuer ${item.name}.`;
      await refreshRules();
      await refreshDownloads();
      await refreshDuplicates();
    });

    const matchesBox = node.querySelector(".rule-matches");
    node.querySelector(".show-matches-button").addEventListener("click", async () => {
      const response = await fetchJson(`/api/rules/${item.id}/matches`);
      renderRuleMatches(matchesBox, response.items || []);
    });

    rulesList.appendChild(node);
  });
}

function renderRuleMatches(container, items) {
  container.hidden = false;
  if (!items.length) {
    container.className = "rule-matches empty-state";
    container.textContent = "Noch keine Treffer gespeichert.";
    return;
  }

  container.className = "rule-matches";
  container.innerHTML = items
    .map((item) => {
      const suffix = item.download_id ? " · Download angelegt" : "";
      return `<div class="match-item">${escapeHtml(item.air_date || "Ohne Datum")} · ${escapeHtml(item.title)}${suffix}</div>`;
    })
    .join("");
}

function renderSystemCheck(payload) {
  const summary = payload.summary || {};
  const checks = payload.checks || [];
  const prereqs = payload.host_prerequisites || [];
  systemCheckPanel.className = "system-check";
  systemCheckPanel.innerHTML = `
    <div class="system-summary">
      <strong>${summary.ok_count || 0}/${summary.total_checks || 0} Container-Checks ok</strong>
      <span>${escapeHtml(summary.platform || "")}</span>
      <span>${escapeHtml(summary.architecture || "")}</span>
    </div>
    <div class="system-grid">
      ${checks
        .map(
          (item) => `
            <div class="check-row">
              <span class="check-dot ${item.status}"></span>
              <span>${escapeHtml(item.label)}</span>
            </div>`,
        )
        .join("")}
    </div>
    <div class="system-manual">
      <h3>Manuell auf der Synology pruefen</h3>
      ${prereqs
        .map(
          (item) => `
            <div class="check-row manual">
              <span class="check-dot manual"></span>
              <span>${escapeHtml(item.label)}</span>
            </div>`,
        )
        .join("")}
    </div>
  `;
}

function renderDuplicates(groups) {
  if (!groups.length) {
    duplicatesPanel.className = "empty-state";
    duplicatesPanel.textContent = "Noch keine Dubletten erkannt.";
    return;
  }
  duplicatesPanel.className = "system-check";
  duplicatesPanel.innerHTML = groups
    .slice(0, 8)
    .map(
      (group) => `
        <div class="duplicate-group">
          <strong>${group.item_count} Eintraege</strong>
          <div class="system-grid">
            ${group.items
              .map(
                (item) => `
                  <div class="check-row">
                    <span class="check-dot warning"></span>
                    <span>${escapeHtml(item.title)} · ${escapeHtml(item.air_date || "ohne Datum")} · ${escapeHtml(
                      translateStatus(item.status),
                    )}</span>
                  </div>`,
              )
              .join("")}
          </div>
        </div>`,
    )
    .join("");
}

function renderMediaServers(payload) {
  const items = [
    { name: "Plex", ...payload.plex },
    { name: "Jellyfin", ...payload.jellyfin },
    { name: "Infuse", ...payload.infuse },
  ];
  mediaServerPanel.className = "system-check";
  mediaServerPanel.innerHTML = items
    .map(
      (item) => `
        <div class="check-row">
          <span class="check-dot ${item.status || "manual"}"></span>
          <span><strong>${escapeHtml(item.name)}</strong> · ${escapeHtml(item.label || "")}</span>
        </div>`,
    )
    .join("");
}

function summarizeMediaServerScan(payload) {
  return Object.entries(payload)
    .map(([name, item]) => `${name}: ${item.label}`)
    .join(" · ");
}

async function runRulesAction(endpoint, pendingText) {
  ruleStatus.textContent = pendingText;
  try {
    const response = await fetchJson(endpoint, {
      method: "POST",
      body: JSON.stringify({ limit: 15 }),
    });
    const items = response.items || [];
    const summary = items.reduce(
      (acc, item) => {
        acc.matches += item.new_matches || 0;
        acc.downloads += item.queued_downloads || 0;
        return acc;
      },
      { matches: 0, downloads: 0 },
    );
    ruleStatus.textContent = `${summary.matches} neue Treffer, ${summary.downloads} Downloads angestossen.`;
    await refreshRules();
    await refreshDownloads();
    await refreshDuplicates();
  } catch (error) {
    ruleStatus.textContent = error.message;
  }
}

function updateSearchRssLink() {
  const params = new URLSearchParams();
  const payload = searchPayloadFromForm();
  Object.entries(payload).forEach(([key, value]) => {
    if (value !== null && value !== "" && !["size", "offset"].includes(key)) {
      params.set(key, String(value));
    }
  });
  searchRssLink.href = `/api/rss/search?${params.toString()}`;
}

function formatDuration(seconds) {
  if (!seconds) {
    return "Dauer unbekannt";
  }
  const minutes = Math.round(seconds / 60);
  return `${minutes} Min.`;
}

function translateStatus(status) {
  const labels = {
    queued: "In Warteschlange",
    downloading: "Laeuft",
    completed: "Abgeschlossen",
    failed: "Fehlgeschlagen",
    canceled: "Abgebrochen",
  };
  return labels[status] || status;
}

function formatDateTime(value) {
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString("de-DE");
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}

function escapeAttribute(value) {
  return escapeHtml(value);
}

function numberOrNull(value) {
  if (value === "" || value === null || value === undefined) {
    return null;
  }
  const parsed = Number(value);
  return Number.isNaN(parsed) ? null : parsed;
}

async function fetchJson(url, options = {}) {
  const response = await fetch(url, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(payload.detail || "Unbekannter Fehler");
  }
  return payload;
}

refreshSettings();
refreshDownloads();
refreshRules();
refreshSystemCheck();
refreshDuplicates();
refreshMediaServers();
updateSearchRssLink();
setInterval(refreshDownloads, 4000);
setInterval(refreshRules, 12000);
setInterval(refreshSystemCheck, 30000);
setInterval(refreshDuplicates, 20000);
setInterval(refreshMediaServers, 30000);
