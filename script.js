// Atrust – Frontend ↔ Backend Integration

const API_BASE = "http://127.0.0.1:8000";

document.addEventListener("DOMContentLoaded", () => {
  const modal       = document.getElementById("uploadModal");
  const closeBtn    = document.getElementById("closeModal");
  const actionCards = document.querySelectorAll(".action-card");
  const fileInput   = document.getElementById("mediaFile");
  const fileSection = document.getElementById("fileSection");
  const textSection = document.getElementById("textSection");
  const textInput   = document.getElementById("textInput");
  const submitBtn   = document.getElementById("submitBtn");
  const modalTitle  = document.getElementById("modalTitle");
  const resultBox   = document.getElementById("resultBox");

  let currentMediaType = "";

  // ── Open modal ───────────────────────────────────────────────────
  actionCards.forEach(card => {
    card.addEventListener("click", () => {
      currentMediaType = card.getAttribute("data-media");
      modalTitle.textContent = `Check ${currentMediaType}`;
      resultBox.style.display = "none";
      resultBox.innerHTML = "";
      fileInput.value = "";
      textInput.value = "";

      if (currentMediaType === "Text") {
        fileSection.style.display = "none";
        textSection.style.display = "block";
        submitBtn.disabled = false;
      } else {
        fileSection.style.display = "block";
        textSection.style.display = "none";
        submitBtn.disabled = true;
        if (currentMediaType === "Video")      fileInput.accept = "video/*";
        else if (currentMediaType === "Audio") fileInput.accept = "audio/*";
        else if (currentMediaType === "Image") fileInput.accept = "image/*";
      }

      modal.removeAttribute("hidden");
    });
  });

  fileInput.addEventListener("change", () => {
    submitBtn.disabled = !fileInput.files.length;
  });

  closeBtn.addEventListener("click", () => modal.setAttribute("hidden", true));
  modal.addEventListener("click", (e) => {
    if (e.target === modal) modal.setAttribute("hidden", true);
  });

  // ── Submit ───────────────────────────────────────────────────────
  submitBtn.addEventListener("click", async (e) => {
    e.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = "Analyzing...";
    resultBox.style.display = "none";

    try {
      let data;

      if (currentMediaType === "Text") {
        const message = textInput.value.trim();
        if (!message) { showError("Please enter a message."); return; }
        const form = new FormData();
        form.append("text", message);
        const res = await fetch(`${API_BASE}/scan/text`, { method: "POST", body: form });
        if (!res.ok) throw new Error(res.status);
        data = await res.json();
      } else {
        const file = fileInput.files[0];
        if (!file) { showError("Please select a file."); return; }
        const form = new FormData();
        form.append("file", file);
        const endpoint = currentMediaType === "Video" ? "video" : currentMediaType === "Audio" ? "audio" : "image";
        const res = await fetch(`${API_BASE}/scan/${endpoint}`, { method: "POST", body: form });
        if (!res.ok) throw new Error(res.status);
        data = await res.json();
      }

      showResult(data);

    } catch (err) {
      showError("Could not connect to backend. Make sure the server is running.");
      console.error(err);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Start Verification";
    }
  });

  // ── Show result ──────────────────────────────────────────────────
  function showResult(data) {
    const riskType = data.risk_type || "critical";
    const isSafe   = riskType === "low" || riskType === "medium";
    const score    = Math.round(data.trust_score || 0);
    const color    = isSafe ? "#16a34a" : "#dc2626";
    const bgColor  = isSafe ? "#f0fdf4" : "#fef2f2";
    const label    = riskType.replace("_", " ").toUpperCase();

    // Circle parameters
    const radius = 54;
    const circumference = 2 * Math.PI * radius;
    const offset = circumference - (score / 100) * circumference;

    resultBox.style.cssText = `display:block;margin-top:20px;padding:20px;border-radius:12px;font-family:Inter,sans-serif;font-size:14px;background:${bgColor};border:1.5px solid ${color};text-align:center;`;
    resultBox.innerHTML = `
      <svg width="140" height="140" viewBox="0 0 140 140" style="display:block;margin:0 auto 12px;">
        <circle cx="70" cy="70" r="${radius}" fill="none" stroke="#e5e7eb" stroke-width="12"/>
        <circle cx="70" cy="70" r="${radius}" fill="none" stroke="${color}" stroke-width="12"
          stroke-dasharray="${circumference}" stroke-dashoffset="${offset}"
          stroke-linecap="round"
          transform="rotate(-90 70 70)"
          style="transition: stroke-dashoffset 0.8s ease;"/>
        <text x="70" y="65" text-anchor="middle" font-size="28" font-weight="700" fill="${color}" font-family="Inter,sans-serif">${score}</text>
        <text x="70" y="85" text-anchor="middle" font-size="12" fill="#6b7280" font-family="Inter,sans-serif">Trust Score</text>
      </svg>
      <div style="font-size:20px;font-weight:700;color:${color};margin-bottom:8px;">${label}</div>
      <div style="color:#374151;font-size:14px;">${data.recommended_action || ""}</div>
    `;
  }

  // ── Show error ───────────────────────────────────────────────────
  function showError(message) {
    resultBox.style.cssText = "display:block;margin-top:20px;padding:16px;border-radius:10px;background:#fef2f2;border:1.5px solid #dc2626;color:#dc2626;font-family:Inter,sans-serif;font-size:14px;";
    resultBox.innerHTML = `⚠️ ${message}`;
  }
});
