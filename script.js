// =============================================
// Atrust – Frontend ↔ Backend Integration
// =============================================

const API_BASE = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
  const modal       = document.getElementById("uploadModal");
  const closeBtn    = document.getElementById("closeModal");
  const actionCards = document.querySelectorAll(".action-card");
  const fileInput   = document.getElementById("mediaFile");
  const submitBtn   = document.querySelector(".submit-btn");
  const modalTitle  = document.querySelector(".modal-header h2");
  const uploadForm  = document.querySelector(".upload-form");

  let currentMediaType = ""; // tracks which card was clicked

  // ── Create result box inside modal ──────────────────────────────
  const resultBox = document.createElement("div");
  resultBox.id = "resultBox";
  resultBox.style.cssText = `
    margin-top: 20px;
    padding: 16px;
    border-radius: 10px;
    font-family: Inter, sans-serif;
    font-size: 14px;
    display: none;
  `;
  uploadForm.appendChild(resultBox);

  // ── Text input box (shown only for Text card) ────────────────────
  const textArea = document.createElement("textarea");
  textArea.id = "textInput";
  textArea.placeholder = "Paste your suspicious message here...";
  textArea.style.cssText = `
    width: 100%;
    height: 100px;
    margin-top: 10px;
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #ccc;
    font-family: Inter, sans-serif;
    font-size: 14px;
    resize: vertical;
    display: none;
    box-sizing: border-box;
  `;
  uploadForm.insertBefore(textArea, submitBtn);

  // ── Open modal when card is clicked ─────────────────────────────
  actionCards.forEach(card => {
    card.addEventListener("click", () => {
      currentMediaType = card.getAttribute("data-media"); // Video / Audio / Image / Text
      modalTitle.textContent = `Check ${currentMediaType}`;
      resultBox.style.display = "none";
      resultBox.innerHTML = "";
      fileInput.value = "";
      textArea.value = "";
      submitBtn.disabled = true;

      // Show text area for Text, file input for others
      if (currentMediaType === "Text") {
        fileInput.parentElement.style.display = "none";
        textArea.style.display = "block";
        submitBtn.disabled = false;
      } else {
        fileInput.parentElement.style.display = "block";
        textArea.style.display = "none";

        // Set accepted file types
        if (currentMediaType === "Video")      fileInput.accept = "video/*";
        else if (currentMediaType === "Audio") fileInput.accept = "audio/*";
        else if (currentMediaType === "Image") fileInput.accept = "image/*";
      }

      modal.removeAttribute("hidden");
    });
  });

  // ── Enable submit when file selected ────────────────────────────
  fileInput.addEventListener("change", () => {
    submitBtn.disabled = !fileInput.files.length;
  });

  // ── Close modal ──────────────────────────────────────────────────
  closeBtn.addEventListener("click", () => modal.setAttribute("hidden", true));
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.setAttribute("hidden", true);
  });

  // ── Submit — send to backend ─────────────────────────────────────
  submitBtn.addEventListener("click", async (e) => {
    e.preventDefault();

    // Show loading state
    submitBtn.disabled = true;
    submitBtn.textContent = "Analyzing...";
    resultBox.style.display = "none";
    resultBox.innerHTML = "";

    try {
      let data;

      if (currentMediaType === "Text") {
        // ── Text analysis ──────────────────────────────────────────
        const message = textArea.value.trim();
        if (!message) {
          showError("Please enter a message to analyze.");
          return;
        }
        const form = new FormData();
        form.append("text", message);
        const res = await fetch(`${API_BASE}/analyze/text`, {
          method: "POST",
          body: form,
        });
        data = await res.json();

      } else {
        // ── File analysis (Video / Audio / Image) ──────────────────
        const file = fileInput.files[0];
        if (!file) {
          showError("Please select a file.");
          return;
        }
        const form = new FormData();
        form.append("file", file);

        const endpoint =
          currentMediaType === "Video" ? "video" :
          currentMediaType === "Audio" ? "audio" : "image";

        const res = await fetch(`${API_BASE}/analyze/${endpoint}`, {
          method: "POST",
          body: form,
        });
        data = await res.json();
      }

      showResult(data);

    } catch (err) {
      showError("Could not connect to the backend. Make sure the server is running.");
      console.error(err);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Start Verification";
    }
  });

  // ── Display result ───────────────────────────────────────────────
  function showResult(data) {
    const isSafe   = data.status === "authentic" || data.status === "safe";
    const percent  = Math.round((data.confidence || 0) * 100);
    const color    = isSafe ? "#16a34a" : "#dc2626";
    const bgColor  = isSafe ? "#f0fdf4" : "#fef2f2";
    const emoji    = isSafe ? "✅" : "🚨";
    const label    = data.status?.replace("_", " ").toUpperCase();

    // Build details rows
    let detailsHTML = "";
    if (data.details) {
      const skip = ["detected_keywords"];
      Object.entries(data.details).forEach(([key, val]) => {
        if (skip.includes(key)) return;
        const label = key.replace(/_/g, " ");
        const pct   = Math.round(val * 100);
        detailsHTML += `
          <div style="margin-bottom:8px;">
            <div style="display:flex;justify-content:space-between;margin-bottom:3px;">
              <span style="text-transform:capitalize;">${label}</span>
              <span style="font-weight:600;">${pct}%</span>
            </div>
            <div style="background:#e5e7eb;border-radius:999px;height:6px;">
              <div style="background:${color};width:${pct}%;height:6px;border-radius:999px;"></div>
            </div>
          </div>`;
      });

      // Show detected keywords for text
      if (data.details.detected_keywords?.length) {
        const tags = data.details.detected_keywords
          .map(kw => `<span style="background:#fee2e2;color:#dc2626;padding:2px 8px;border-radius:999px;font-size:12px;margin:2px;display:inline-block;">${kw}</span>`)
          .join("");
        detailsHTML += `<div style="margin-top:10px;"><strong>Detected keywords:</strong><br/>${tags}</div>`;
      }
    }

    resultBox.style.cssText = `
      margin-top: 20px;
      padding: 16px;
      border-radius: 10px;
      font-family: Inter, sans-serif;
      font-size: 14px;
      background: ${bgColor};
      border: 1.5px solid ${color};
      display: block;
    `;

    resultBox.innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px;">
        <span style="font-size:24px;">${emoji}</span>
        <div>
          <div style="font-size:18px;font-weight:700;color:${color};">${label}</div>
          <div style="color:#6b7280;">Confidence: <strong>${percent}%</strong></div>
        </div>
      </div>
      <p style="color:#374151;margin-bottom:14px;">${data.summary}</p>
      ${detailsHTML}
    `;
  }

  // ── Display error ────────────────────────────────────────────────
  function showError(message) {
    resultBox.style.cssText = `
      margin-top: 20px;
      padding: 16px;
      border-radius: 10px;
      font-family: Inter, sans-serif;
      font-size: 14px;
      background: #fef2f2;
      border: 1.5px solid #dc2626;
      display: block;
      color: #dc2626;
    `;
    resultBox.innerHTML = `⚠️ ${message}`;
  }
});
