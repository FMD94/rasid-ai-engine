# RASID — AI Context-Aware Online Safety Engine

**Version:** 2.0 · 2026  
**Institution:** Almaarefa University · College of Engineering & Computer Science  
**Supervisor:** Dr Mohammed Algabri  
**Team:** Amina Atta · Faten Aldawood

---

## Overview

RASID is an AI-powered multilingual advertisement analysis system that detects unsafe, manipulative, and fraudulent digital advertising. It analyses text, image, and video content in both Arabic and English, and gives moderators full visibility into every AI decision.

**Detects:**
- Manipulative and fraudulent advertisements
- Emotionally exploitative content
- Misleading promotional tactics
- Unsafe digital advertising behaviour

**Supports:**
- Arabic and English advertisements
- Text, image, and video analysis
- Explainable AI (LIME)
- Human-in-the-loop moderation with dispute resolution
- Moderator dashboard and region policy review

---

## System Requirements

### Hardware

| Component | Minimum |
|-----------|---------|
| Processor | Intel i5 / AMD Ryzen 5 |
| RAM | 8 GB |
| Storage | 10 GB free space |
| GPU | NVIDIA GPU (optional) |
| Internet | Required for deployment and API testing |

### Software

| Software | Version |
|----------|---------|
| Python | 3.11+ |
| VS Code | Latest |
| Streamlit | Latest |
| FastAPI | Latest |
| SQLite | Built-in with Python |
| Git | Latest |

---

## Project Structure

```
rasid-ai-engine/
├── src/
│   ├── rasid/
│   ├── nlp/
│   └── vision/
├── archive/
├── data/
├── dashboard.py
├── requirements.txt
├── logs/
│   └── rasid.db
└── models/
```

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/FMD94/rasid-ai-engine.git

# 2. Open the folder in VS Code

# 3. Create a virtual environment
python -m venv .venv

# 4. Activate the environment (Windows)
.venv\Scripts\activate

# 5. Install dependencies
pip install -r requirements.txt
```

### Key Dependencies

`moviepy` · `opencv-python` · `pytesseract` · `scikit-learn` · `plotly` · `pandas` · `pillow` · `numpy` · `python-dotenv` · `pydantic` · `streamlit` · `fastapi`

---

## Running RASID

### Start the API Server

```bash
python -m uvicorn src.rasid.api:app --reload
```

| Page | URL |
|------|-----|
| API Base | http://127.0.0.1:8000 |
| Swagger Docs | http://127.0.0.1:8000/docs |

### Start the Dashboard

```bash
streamlit run dashboard.py
```

| Page | URL |
|------|-----|
| Dashboard | http://localhost:8501 |

### Shutdown

Press `CTRL + C` in each terminal window to stop services safely.

---

## Login

| Username | Password |
|----------|----------|
| admin | rasid123 |

> ⚠️ Change the default password immediately after first login.

---

## AI Stack

| Component | Model / Tool |
|-----------|-------------|
| Arabic NLP | AraBERT v2 |
| English NLP | BERT-base |
| OCR | pytesseract / EasyOCR |
| Video processing | MoviePy, OpenCV |
| Explainability | LIME |
| Deepfake detection | Prototype signal (deepfake_risk + deepfake_score) |
| Routing | Custom language router |
| Backend | FastAPI |
| Dashboard | Streamlit + Plotly |
| Database | SQLite |

---

## API Endpoints

### Text Analysis

- **Endpoint:** `POST /analyze/text/auto`
- **Languages:** Arabic and English (auto-detected)

**Example:**
```json
// Input
"Guaranteed profit within 24 hours"

// Output
{
  "decision": "blocked",
  "confidence": 0.91,
  "language": "en",
  "reasons": ["Rule matched blocked phrase: guaranteed profit"]
}
```

### Image Analysis

- **Endpoint:** `POST /analyze/image`
- **Formats:** JPG, PNG, WEBP
- **Pipeline:** OCR → Language detection → Transformer classification → LIME explanation → DB storage

### Video Analysis

- **Endpoint:** `POST /analyze/video`
- **Formats:** MP4, MOV, AVI
- **Pipeline:** Frame extraction → OCR per frame → Speech transcription → AI classification → Risk aggregation

---

## Risk Classification

| Category | Description |
|----------|-------------|
| Safe | Normal advertisement. No harmful elements detected. |
| Manipulative | Uses emotional or persuasive exploitation — dark patterns, false urgency, fear tactics. |
| Fraudulent | Dangerous, deceptive, or scam-like behaviour — phishing, impersonation, fake prizes. |

---

## Explainable AI (LIME)

RASID uses LIME to highlight exactly which words influenced the AI verdict.

```json
"lime_explanation": [
  { "word": "NOW", "weight": 0.0135 }
]
```

LIME explanations appear in the report view and the Logs tab of the dashboard.

---

## Dashboard Tabs

| Tab | Description |
|-----|-------------|
| 📊 Overview | Live summary: total scans, risk distribution, language breakdown, input type charts, latest analysis |
| 👤 Moderator Review | Review AI decisions, override classifications, add notes, save to audit log |
| 🌍 Region Policy Check | Apply region-specific rules (Saudi Arabia, GCC, EU, US, General) per policy area |
| 🗂 Logs | Full history: timestamps, language, confidence, deepfake risk/score, AI reasons, moderator reviews |
| ⚠️ Dispute Requests | Review and resolve user-submitted disputes against AI decisions |

---

## Human-in-the-Loop Moderation

RASID is not fully automated. Moderators can review and correct AI decisions, but corrections are **queued for senior admin approval** before entering the fine-tuning pipeline — protecting the model from incorrect or malicious feedback.

**Workflow:**
1. Moderator reviews an AI decision and submits a correction with a written reason
2. Correction enters a review queue
3. Senior admin approves or rejects the correction
4. Only approved corrections are promoted to fine-tuning data

Users can also submit **dispute requests** challenging an AI decision. Moderators review disputes and can override the outcome directly from the Dispute Requests tab.

---

## Database

RASID uses SQLite stored at `logs/rasid.db`.

| Table | Stores |
|-------|--------|
| `analysis_logs` | AI predictions, confidence scores, language, timestamps, LIME explanations, deepfake signals |
| `moderator_reviews` | Moderator decisions, override notes, review history, full audit trail |
| `dispute_requests` | User appeals, AI decision context, moderator resolution status |

---

## Troubleshooting

**API not running**
```bash
python -m uvicorn src.rasid.api:app --reload
# Check terminal for error messages
```

**Dashboard not updating**
- Confirm the API is running
- Confirm `logs/rasid.db` exists and SQLite is connected

**Browser extension not working**
- Check browser permissions
- Confirm API is accessible at localhost
- Verify `popup.js` is correctly configured

**Database errors**
```bash
# Reset the database (Windows)
del logs\rasid.db
# Then restart the API
```

---

## Planned Enhancements

- Full deepfake detection (image and video)
- SHAP explainability (alongside LIME)
- Real-time browser alerts
- Cloud deployment
- Multi-user moderation with role management
- Live social media monitoring
- Advanced multimodal content fusion
