// ---------------------------------------------------------------------
// main.js - frontend logic for the Conversational EDA Workspace
// ---------------------------------------------------------------------

const $ = (sel) => document.querySelector(sel);

// ---- Tab navigation ----------------------------------------------------
document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    document.querySelectorAll(".tab-btn").forEach((b) => b.classList.remove("active"));
    document.querySelectorAll(".tab-pane").forEach((p) => p.classList.remove("active"));
    btn.classList.add("active");
    $(`#tab-${btn.dataset.tab}`).classList.add("active");
  });
});

// ---- Upload / Dropzone --------------------------------------------------
const dropzone = $("#dropzone");
const fileInput = $("#fileInput");
const uploadMessage = $("#uploadMessage");
const datasetStatus = $("#datasetStatus");
const cleanControls = $("#cleanControls");

dropzone.addEventListener("click", () => fileInput.click());
dropzone.addEventListener("dragover", (e) => { e.preventDefault(); dropzone.classList.add("dragover"); });
dropzone.addEventListener("dragleave", () => dropzone.classList.remove("dragover"));
dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.classList.remove("dragover");
  if (e.dataTransfer.files.length) uploadFile(e.dataTransfer.files[0]);
});
fileInput.addEventListener("change", () => {
  if (fileInput.files.length) uploadFile(fileInput.files[0]);
});

async function uploadFile(file) {
  setUploadMessage("Uploading and parsing file...", "");
  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/api/upload", { method: "POST", body: formData });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Upload failed.");

    setUploadMessage(
      `✓ Loaded "${data.meta.original_filename}" — ${data.meta.n_rows} rows × ${data.meta.n_cols} columns.`,
      "success"
    );
    datasetStatus.textContent = `${data.meta.original_filename} (${data.meta.n_rows}×${data.meta.n_cols})`;
    cleanControls.style.display = "block";
    loadPreview();
  } catch (err) {
    setUploadMessage(`✗ ${err.message}`, "error");
  }
}

function setUploadMessage(text, cls) {
  uploadMessage.textContent = text;
  uploadMessage.className = "message-box" + (cls ? ` ${cls}` : "");
}

// ---- Preview table -------------------------------------------------------
async function loadPreview() {
  const container = $("#previewContainer");
  container.innerHTML = "<p class='muted'>Loading preview...</p>";
  try {
    const res = await fetch("/api/preview");
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Could not load preview.");
    renderPreviewTable(data.preview, container);
  } catch (err) {
    container.innerHTML = `<p class="message-box error">${err.message}</p>`;
  }
}

function renderPreviewTable(preview, container) {
  const { columns, rows, shape } = preview;
  let html = `<p class="muted">Showing first ${rows.length} of ${shape[0]} rows</p>`;
  html += "<table class='preview-table'><thead><tr>";
  columns.forEach((c) => (html += `<th>${escapeHtml(c)}</th>`));
  html += "</tr></thead><tbody>";
  rows.forEach((row) => {
    html += "<tr>" + row.map((v) => `<td>${v === null ? "<em>NaN</em>" : escapeHtml(String(v))}</td>`).join("") + "</tr>";
  });
  html += "</tbody></table>";
  container.innerHTML = html;
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}

// ---- Quick Clean ----------------------------------------------------------
$("#applyCleanBtn").addEventListener("click", async () => {
  const drop_duplicates = $("#dropDupes").checked;
  const fillna_strategy = $("#fillStrategy").value;
  try {
    const res = await fetch("/api/clean", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ drop_duplicates, fillna_strategy }),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Cleaning failed.");
    setUploadMessage(
      `✓ Cleaned: ${data.result.rows_before} → ${data.result.rows_after} rows.`, "success"
    );
    loadPreview();
  } catch (err) {
    setUploadMessage(`✗ ${err.message}`, "error");
  }
});

// ---- Profiling report -------------------------------------------------------
$("#generateProfileBtn").addEventListener("click", async () => {
  const status = $("#profileStatus");
  const btn = $("#generateProfileBtn");
  btn.disabled = true;
  status.textContent = "Generating report... this can take a moment for larger datasets.";
  try {
    const res = await fetch("/api/profile", { method: "POST" });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || "Profiling failed.");
    $("#profileFrame").src = data.report_url;
    status.textContent = data.minimal
      ? "Report generated (minimal mode used for large dataset)."
      : "Report generated successfully.";
  } catch (err) {
    status.textContent = `Error: ${err.message}`;
  } finally {
    btn.disabled = false;
  }
});

// ---- Chat -------------------------------------------------------------------
const chatWindow = $("#chatWindow");
const chatForm = $("#chatForm");
const chatInput = $("#chatInput");

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  const message = chatInput.value.trim();
  if (!message) return;
  appendUserMessage(message);
  chatInput.value = "";
  const typingEl = appendTypingIndicator();

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message }),
    });
    const data = await res.json();
    typingEl.remove();
    if (!res.ok) {
      appendAgentMessage(data.error || "Something went wrong.", { error: true });
      return;
    }
    appendAgentMessage(data.response.content, { chartUrl: data.response.chart_url });
  } catch (err) {
    typingEl.remove();
    appendAgentMessage(`Network error: ${err.message}`, { error: true });
  }
});

function appendUserMessage(text) {
  const div = document.createElement("div");
  div.className = "chat-msg user";
  div.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
  chatWindow.appendChild(div);
  scrollChatToBottom();
}

function appendAgentMessage(text, { chartUrl, error } = {}) {
  const div = document.createElement("div");
  div.className = "chat-msg agent";
  const bubble = document.createElement("div");
  bubble.className = "bubble" + (error ? " error" : "");
  bubble.innerHTML = escapeHtml(text).replace(/\n/g, "<br>");
  if (chartUrl) {
    const img = document.createElement("img");
    img.src = chartUrl + `?t=${Date.now()}`; // cache-bust
    img.alt = "Generated chart";
    bubble.appendChild(img);
  }
  div.appendChild(bubble);
  chatWindow.appendChild(div);
  scrollChatToBottom();
}

function appendTypingIndicator() {
  const div = document.createElement("div");
  div.className = "chat-msg agent";
  div.innerHTML = `<div class="bubble"><span class="typing"><span></span><span></span><span></span></span></div>`;
  chatWindow.appendChild(div);
  scrollChatToBottom();
  return div;
}

function scrollChatToBottom() {
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ---- Reset session -------------------------------------------------------
$("#resetBtn").addEventListener("click", async () => {
  if (!confirm("Reset session? This clears your uploaded dataset and chat history.")) return;
  await fetch("/api/reset", { method: "POST" });
  window.location.reload();
});
