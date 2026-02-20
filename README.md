# 🛡️ Atrust — Multi-Modal Digital Trust Verification System

> Detect deepfakes, AI-generated images, voice clones, and phishing scams in real time.

---

## 📌 What is Atrust?

Atrust is a web-based cyber integrity platform that helps users verify the authenticity of digital media and messages. It uses AI-powered analysis across four modalities:

| Modality | What it detects |
|----------|----------------|
| 🎬 Video | Deepfake manipulation, facial inconsistencies, lip-sync mismatch |
| 🖼️ Image | AI-generated images, GAN fingerprints, face swaps |
| 🎧 Audio | Voice cloning, spectral anomalies, synthetic speech |
| 📝 Text  | Phishing, UPI/OTP scams, impersonation, legal threats |

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10 or higher → [Download here](https://www.python.org/downloads/)
- Git → [Download here](https://git-scm.com/downloads)

### Installation

**Step 1 — Clone the repository**
```bash
git clone https://github.com/mansijha1707-blip/Atrust.git
cd Atrust
```

**Step 2 — Install dependencies**
```bash
pip install -r requirements.txt
```

**Step 3 — Start the backend server**

Option A — Double click `start.bat` (Windows, easiest)

Option B — Run manually:
```bash
uvicorn main:app --reload
```

**Step 4 — Open the frontend**

Open `index.html` in your browser. That's it!

---

## 🔗 API Endpoints

Base URL: `http://127.0.0.1:8000`

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check |
| GET | `/health` | Server status |
| POST | `/scan/video` | Analyse video for deepfakes |
| POST | `/scan/image` | Detect AI-generated images |
| POST | `/scan/audio` | Detect voice cloning |
| POST | `/scan/text` | Detect phishing/scam messages |
| POST | `/scan/unified` | Analyse all modalities at once |

Interactive API docs: **http://127.0.0.1:8000/docs**

---

## 📡 Example API Response

```json
{
  "trust_score": 32,
  "risk_type": "critical",
  "flags": ["text:otp_mentioned", "text:upi_mentioned", "text:urgent_language"],
  "recommended_action": "Treat as malicious. Do not send money/OTP/UPI or sensitive info.",
  "evidence": [
    {
      "pipeline": "text",
      "type": "scam_intent_rules",
      "severity": 4,
      "details": {
        "matches": [
          { "flag": "text:otp_mentioned", "severity": 5 },
          { "flag": "text:upi_mentioned", "severity": 5 },
          { "flag": "text:urgent_language", "severity": 3 }
        ]
      }
    }
  ]
}
```
<img width="1919" height="869" alt="image" src="https://github.com/user-attachments/assets/40867dcc-bb5f-4328-b765-c295dea5f71b" />

<img width="833" height="756" alt="image" src="https://github.com/user-attachments/assets/543a4ab7-401b-4279-a43b-033dcc2afcd9" />


---

## 📁 Project Structure

```
Atrust/
├── index.html        ← Frontend dashboard
├── about.html        ← About page
├── styles.css        ← Styling
├── script.js         ← Frontend logic (connects to backend)
│
├── main.py           ← FastAPI server entry point
├── video.py          ← Video deepfake detection
├── image.py          ← AI image detection
├── audio.py          ← Voice clone detection
├── text.py           ← Phishing/scam text detection
├── files.py          ← File upload handling
├── report.py         ← Trust report builder
├── schemas.py        ← Pydantic data models
├── requirements.txt  ← Python dependencies
├── start.bat         ← One-click server startup (Windows)
└── uploads/          ← Temporary file storage (auto-cleaned)
```

---

## 🧠 Trust Score Explained

Every scan returns a **Trust Score** from 0–100:

| Score | Risk Level | Meaning |
|-------|-----------|---------|
| 85–100 | 🟢 Low | Safe to proceed |
| 65–84 | 🟡 Medium | Proceed with caution |
| 40–64 | 🟠 High | Seek verification |
| 0–39 | 🔴 Critical | Treat as malicious |

---

## 🔮 Future Improvements

- [ ] Integrate real deepfake detection model (FaceForensics++)
- [ ] Integrate real voice clone detection (RawNet2 / AASIST)
- [ ] Integrate real image detection (CNNDetection / DIRE)
- [ ] Upgrade text detection with fine-tuned BERT model
- [ ] Add user authentication
- [ ] Deploy to cloud (AWS / Render / Railway)

---

## 👥 Contributors

- [mansijha1707-blip](https://github.com/mansijha1707-blip)

---

## 🏆 Built For

**Hackathon Project** — Multi-Modal Digital Trust Verification  
*Fighting deepfakes and digital fraud with AI.*
