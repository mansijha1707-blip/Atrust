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
        
        const res = await fetch(`${API_BASE}/scan/text`, {
          method: "POST",
          body: form,
        });
        if (!res.ok) throw new Error(`Request failed: ${res.status}`);
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

        
        const res = await fetch(`${API_BASE}/scan/${endpoint}`, {
          method: "POST",
          body: form,
        });
        if (!res.ok) throw new Error(`Request failed: ${res.status}`);
        data = await res.json();
      }

      
      showResult(data, currentMediaType);

    } catch (err) {
      showError("Could not connect to the backend. Make sure the server is running.");
      console.error(err);
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = "Start Verification";
    }
  });

  // ── Display result ───────────────────────────────────────────────
  
  function showResult(data, mediaType) {
    const riskType = data.risk_type || "critical";
    const isSafe = riskType === "low" || riskType === "medium";
    const percent = Math.round(data.trust_score || 0);
    const color    = isSafe ? "#16a34a" : "#dc2626";
    const bgColor  = isSafe ? "#f0fdf4" : "#fef2f2";
    const emoji    = isSafe ? "✅" : "🚨";
    const label = riskType.replace("_", " ").toUpperCase();

    // Build details rows
    let detailsHTML = "";
    
    const key = (mediaType || "").toLowerCase();
    const details = data.raw?.[key]?.summary || {};
    if (details && typeof details === "object") {
      Object.entries(details).forEach(([key, val]) => {
        if (typeof val !== "number") return;
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
          <div style="color:#6b7280;">Trust Score: <strong>${percent}%</strong></div>
        </div>
      </div>
      <p style="color:#374151;margin-bottom:14px;">${data.recommended_action || "No recommendation available."}</p>
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
