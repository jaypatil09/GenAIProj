# Quick Start Guide for SentiMeter

## 🚀 Get Running in 5 Minutes

### Step 1: Install Dependencies (2 minutes)

```bash
# Navigate to project directory
cd SentiMeter

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### Step 2: Generate Sample Data (2 minutes)

```bash
python generate_dataset.py
```

This creates `data/feedback.csv` with 10,000 realistic hospital feedback records.

### Step 3: Choose Your Interface (1 minute)

#### Option A: Web Dashboard (Recommended for First-Time Users)

```bash
streamlit run src/dashboard/app.py
```

Open browser → `http://localhost:8501`

**Features:**
- 📊 Real-time feedback analysis
- 📋 View complaint queue
- 📈 Department trends
- 🎯 Aspect analytics
- ⚠️ Escalation monitoring
- 👥 Staff performance metrics

#### Option B: REST API (For Integration)

```bash
python -m uvicorn src.api.main:app --reload
```

Open browser → `http://localhost:8000/docs` (Swagger UI)

**Example Request:**
```bash
curl -X POST "http://localhost:8000/analyze-feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "feedback_text": "The doctor was helpful but the wait was too long"
  }' | jq .
```

---

## 📊 What the System Does

Input: Patient feedback text
```
"The nurse was rude and we waited 3 hours for the doctor"
```

Output: Complete analysis
```json
{
  "service_line": "Emergency Department",
  "aspects": ["politeness", "wait_time"],
  "aspect_sentiments": {
    "politeness": "negative",
    "wait_time": "negative"
  },
  "overall_sentiment": "negative",
  "staff_category": "nursing_staff",
  "severity": "HIGH",
  "routing_department": "Nursing Supervisor",
  "requires_escalation": true,
  "escalation_reason": "HIGH severity complaint"
}
```

---

## 📁 Key Files

### Core Pipeline
- `src/engines/feedback_processor.py` - Main orchestrator
- `src/models/aspect_detector.py` - Aspect detection (9 types)
- `src/models/service_line_classifier.py` - Hospital department classification
- `src/models/aspect_sentiment_classifier.py` - Sentiment scoring
- `src/engines/severity_engine.py` - Severity assessment
- `src/engines/routing_engine.py` - Complaint routing

### User Interfaces
- `src/dashboard/app.py` - Streamlit dashboard (8 pages)
- `src/api/main.py` - FastAPI REST endpoints (6 endpoints)

### Data Management
- `src/data/text_cleaning.py` - Text preprocessing
- `src/data/data_loader.py` - CSV file handling
- `generate_dataset.py` - Synthetic data generator

### Documentation
- `README.md` - Comprehensive documentation
- `architecture.md` - Detailed system design

---

## 🎯 Common Tasks

### Analyze Single Feedback via Dashboard
1. Go to 📊 → 🔍 Feedback Analyzer
2. Paste feedback text
3. Click "🔍 Analyze Feedback"
4. View complete analysis

### View Escalations
1. Click ⚠️ Escalation Center
2. See critical and high severity complaints
3. Review routing decisions

### Upload CSV File
1. Use API: `POST /bulk-upload`
2. Select `data/feedback.csv` file
3. Wait for processing
4. Results saved to `data/processed_feedback.csv`

### Train Custom Models
```python
from src.models.aspect_detector import AspectDetector

detector = AspectDetector()
texts = [...]  # Your training texts
labels = [...]  # Multi-hot encoded labels
detector.train(texts, labels)
```

---

## 📊 System Outputs

### What Gets Detected

**Aspects (9 types):**
- wait_time, politeness, cleanliness
- billing, diagnostics, discharge_process
- doctor_explanation, nursing_care, lab_services

**Service Lines (7 types):**
- Outpatient Department, Emergency Department, Inpatient Ward
- Surgery, Diagnostic Services, Billing Department, Administration

**Staff Categories (7 types):**
- doctor, nursing_staff, reception_staff
- billing_staff, diagnostics_staff, housekeeping, security

**Severity Levels (4 types):**
- CRITICAL (medication errors, patient falls)
- HIGH (serious errors, long delays >2 hours)
- MEDIUM (rude staff, moderate delays)
- LOW (positive feedback, minor issues)

**Sentiments (3 types):**
- positive, neutral, negative

---

## 🔧 Customization

### Add Custom Aspect Keywords

Edit `src/models/aspect_detector.py`:

```python
ASPECT_KEYWORDS = {
    "your_aspect": ["keyword1", "keyword2", "keyword3"],
    # ... more aspects
}
```

### Change Routing Rules

Edit `src/engines/routing_engine.py`:

```python
ASPECT_ROUTING = {
    "your_aspect": "Your Department",
    # ... more mappings
}
```

### Adjust Severity Rules

Edit `src/engines/severity_engine.py`:

```python
SEVERITY_KEYWORDS = {
    "CRITICAL": ["keyword1", "keyword2"],
    # ... more rules
}
```

---

## 📈 Dashboard Pages Explained

| Page | Purpose |
|------|---------|
| 📊 Overview | Key metrics and distribution charts |
| 🔍 Analyzer | Real-time feedback analysis |
| 📋 Queue | View and filter complaints |
| 📈 Trends | Department-specific analytics |
| 🎯 Aspects | Aspect frequency and sentiment |
| ⚠️ Escalations | Critical complaint management |
| 🌟 Themes | Emerging complaint patterns |
| 👥 Staff | Staff category analytics |

---

## 🐛 Troubleshooting

**Models not loading?**
```bash
# Rebuild models on startup
rm models/*.pkl
python -c "from src.models import *; print('Ready')"
```

**No data showing?**
```bash
# Generate sample data
python generate_dataset.py

# Check file exists
ls data/feedback.csv
```

**Streamlit slow?**
```bash
# Clear cache
streamlit cache clear

# Restart
streamlit run src/dashboard/app.py --logger.level=error
```

**API not responding?**
```bash
# Check server is running
curl http://localhost:8000/health

# View logs for errors
python -m uvicorn src.api.main:app --log-level debug
```

---

## 💡 Pro Tips

1. **Start with Dashboard** - Better for understanding the system
2. **Use API for Integration** - REST endpoints for other apps
3. **Batch Upload** - Process CSV files with `/bulk-upload`
4. **Custom Models** - Train on your hospital's feedback for better accuracy
5. **Monitor Escalations** - Check escalation center regularly
6. **Export Data** - All data in CSV format for external tools

---

## 📞 Support

For detailed information:
- See `README.md` for comprehensive docs
- See `architecture.md` for technical design
- Check docstrings in Python files for code help

For questions about components:
- Text cleaning: See `src/data/text_cleaning.py`
- Models: See `src/models/`
- Engines: See `src/engines/`
- API: See `src/api/`

---

## ✅ Verification Checklist

After setup, verify everything works:

- [ ] `python generate_dataset.py` creates 10K records
- [ ] Dashboard loads at `http://localhost:8501`
- [ ] API responds at `http://localhost:8000/health`
- [ ] Sample feedback analyzes correctly
- [ ] CSV upload works
- [ ] Metrics endpoint returns data
- [ ] All 8 dashboard pages load

---

**You're ready! Start with the Streamlit dashboard for the best user experience.** 🎉

Next: `streamlit run src/dashboard/app.py`
