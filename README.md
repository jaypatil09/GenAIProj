# SentiMeter: Patient Experience Intelligence & Smart Complaint Routing Platform

A comprehensive AI-powered system for analyzing hospital patient feedback, detecting service issues, and automatically routing complaints to appropriate departments with severity assessment.

## 🎯 Project Overview

SentiMeter processes patient feedback through an intelligent pipeline that:

- **Analyzes feedback** using rule-based and machine learning approaches
- **Detects service aspects** (wait times, staff politeness, cleanliness, billing, etc.)
- **Determines sentiment** at both overall and aspect-specific levels
- **Assesses severity** using rule-based engines
- **Routes complaints** to appropriate departments
- **Discovers emerging themes** using semantic clustering
- **Provides visualizations** through interactive dashboards and APIs

### Key Features

✅ **No External LLMs** - Pure ML using scikit-learn, XGBoost, and Sentence Transformers  
✅ **No Cloud Dependencies** - Runs completely locally  
✅ **CSV-Based Storage** - All data stored in simple CSV files  
✅ **Real-time Analysis** - Process feedback instantly via API or dashboard  
✅ **Automated Routing** - Intelligent routing based on multiple factors  
✅ **Theme Discovery** - Detect unknown complaint patterns using HDBSCAN  
✅ **Interactive Dashboard** - Streamlit-based visualization and analysis  
✅ **REST API** - FastAPI endpoints for integration

## 📋 System Architecture

```
Patient Feedback
        ↓
    [Text Cleaning]
        ↓
    [Service Line Classification] → TF-IDF + Logistic Regression
        ↓
    [Aspect Extraction] → Rule-Based + Multi-label Classification
        ↓
    [Aspect Sentiment Analysis] → TF-IDF + Logistic Regression
        ↓
    [Staff Detection] → Rule-Based Keyword Matching
        ↓
    [Severity Scoring] → Rule-Based Engine
        ↓
    [Routing Engine] → Department Assignment
        ↓
    [Theme Discovery] → SentenceTransformer + HDBSCAN
        ↓
    [Dashboard & API] → Visualization & Integration
```

## 🏗️ Project Structure

```
SentiMeter/
├── src/
│   ├── data/                          # Data processing
│   │   ├── __init__.py
│   │   ├── text_cleaning.py          # Text preprocessing
│   │   └── data_loader.py            # CSV data management
│   ├── models/                        # ML models
│   │   ├── __init__.py
│   │   ├── aspect_detector.py        # Aspect detection
│   │   ├── service_line_classifier.py # Service line classification
│   │   ├── aspect_sentiment_classifier.py # Sentiment analysis
│   │   └── theme_discovery.py        # Emerging theme discovery
│   ├── engines/                       # Processing engines
│   │   ├── __init__.py
│   │   ├── staff_detector.py         # Staff category detection
│   │   ├── severity_engine.py        # Severity scoring
│   │   ├── routing_engine.py         # Department routing
│   │   └── feedback_processor.py     # Main pipeline orchestrator
│   ├── api/                          # REST API
│   │   ├── __init__.py
│   │   ├── main.py                   # FastAPI application
│   │   └── schemas.py                # Request/response models
│   └── dashboard/                    # Streamlit dashboard
│       ├── __init__.py
│       └── app.py                    # Dashboard application
├── data/                             # Data directory
│   ├── feedback.csv                  # Raw feedback data
│   ├── processed_feedback.csv        # Analyzed feedback
│   ├── themes.csv                    # Emerging themes
│   └── escalations.csv               # Escalated complaints
├── models/                           # Saved ML models (joblib)
│   ├── service_line_model.pkl
│   ├── aspect_vectorizer.pkl
│   ├── aspect_model.pkl
│   ├── aspect_sentiment_model_*.pkl
│   └── themes_metadata.pkl
├── notebooks/                        # Jupyter notebooks
│   └── exploration.ipynb
├── requirements.txt                  # Python dependencies
├── generate_dataset.py               # Synthetic data generation
├── architecture.md                   # Detailed architecture
└── README.md                         # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- pip or conda
- 2GB RAM minimum
- ~500MB disk space

### Installation

1. **Clone or navigate to the project**

```bash
cd SentiMeter
```

2. **Create a virtual environment (recommended)**

```bash
# Using venv
python -m venv venv
venv\Scripts\activate

```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Generate sample data**

```bash
python generate_dataset.py
```

This generates 10,000 synthetic feedback records in `data/feedback.csv`

## 💻 Usage

### Option 1: Run the FastAPI Server

```bash
python -m uvicorn src.api.main:app --reload --host 0.0.0.0 --port 8000
```

Access the API at: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

**Example API Call:**

```bash
curl -X POST "http://localhost:8000/analyze-feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "feedback_text": "The doctor was very helpful but the wait time was too long",
    "feedback_id": "FBK001"
  }'
```

### Option 2: Run the Streamlit Dashboard

```bash
streamlit run src/dashboard/app.py
```

Access the dashboard at: `http://localhost:8501`

The dashboard includes:
- 📊 Dashboard Overview
- 🔍 Real-time Feedback Analyzer
- 📋 Complaint Queue Management
- 📈 Department Trends
- 🎯 Aspect Analytics
- ⚠️ Escalation Center
- 🌟 Emerging Themes
- 👥 Staff Analytics

### Option 3: Programmatic Usage

```python
from src.models.aspect_detector import AspectDetector
from src.models.service_line_classifier import ServiceLineClassifier
from src.models.aspect_sentiment_classifier import AspectSentimentClassifier
from src.engines.feedback_processor import FeedbackProcessor

# Initialize components
aspect_detector = AspectDetector()
service_line_classifier = ServiceLineClassifier()
aspect_sentiment_classifier = AspectSentimentClassifier()

# Create processor
processor = FeedbackProcessor(
    aspect_detector,
    service_line_classifier,
    aspect_sentiment_classifier
)

# Process feedback
feedback_text = "The doctor explained everything clearly and was very polite"
result = processor.process_single(feedback_text)

print(result)
# Output:
# {
#   'feedback_id': 'FBK...',
#   'service_line': 'Outpatient Department',
#   'aspects': ['doctor_explanation', 'politeness'],
#   'aspect_sentiments': {'doctor_explanation': 'positive', 'politeness': 'positive'},
#   'overall_sentiment': 'positive',
#   'staff_category': 'doctor',
#   'severity': 'LOW',
#   'routing_department': 'Medical Services',
#   'requires_escalation': False,
#   'escalation_reason': None
# }
```

## 📊 API Endpoints

### Analyze Single Feedback
```
POST /analyze-feedback
Content-Type: application/json

{
  "feedback_text": "string",
  "feedback_id": "string (optional)",
  "source": "string (optional)"
}
```

### Bulk Upload CSV
```
POST /bulk-upload
Content-Type: multipart/form-data

[CSV file with feedback_text column]
```

### Get System Metrics
```
GET /metrics
```

Returns sentiment, severity, and department distributions.

### Get Department Summary
```
GET /department-summary
```

Returns per-department analytics.

### Get Emerging Themes
```
GET /emerging-themes
```

Returns discovered themes from feedback clustering.

### Get Escalations
```
GET /escalations
```

Returns list of escalated complaints.

### Health Check
```
GET /health
GET /
```

## 🎯 Detected Aspects

The system detects 9 key aspects of patient feedback:

| Aspect | Keywords |
|--------|----------|
| **wait_time** | wait, delay, queue, late, long time |
| **politeness** | rude, arrogant, shouted, polite, courteous |
| **cleanliness** | dirty, smell, unclean, clean, hygiene |
| **billing** | bill, insurance, charges, payment, cost |
| **diagnostics** | report, result, scan, lab, test |
| **discharge_process** | discharge, summary, clearance, checkout |
| **doctor_explanation** | explain, understand, told, informed |
| **nursing_care** | nurse, care, attentive, responsive |
| **lab_services** | lab, test, blood, sample, results |

## 📈 Service Lines

The system classifies feedback into hospital service lines:

- Outpatient Department (OPD)
- Emergency Department (ED)
- Inpatient Ward (IP)
- Surgery
- Diagnostic Services
- Billing Department
- Administration

## 🎓 Staff Categories

Staff detected in feedback:

- doctor
- nursing_staff
- reception_staff
- billing_staff
- diagnostics_staff
- housekeeping
- security

## ⚠️ Severity Levels

Feedback is classified into 4 severity levels:

| Level | Triggers | Examples |
|-------|----------|----------|
| **CRITICAL** | Safety concerns, medication errors, patient falls | "Wrong medication given", "Patient fell from bed" |
| **HIGH** | Serious errors, significant delays >2 hours | "Wrong diagnosis", "Waited 3 hours" |
| **MEDIUM** | Staff rudeness, moderate delays 30 min-2 hours | "Rude doctor", "Waited 1.5 hours" |
| **LOW** | Praise, minor issues | "Excellent service", "Quick appointment" |

## 🛣️ Routing Rules

Feedback is routed based on primary aspect:

| Aspect | Department |
|--------|-----------|
| wait_time | OPD Operations |
| politeness | Front Desk |
| doctor_explanation | Medical Services |
| billing | Billing Department |
| cleanliness | Housekeeping |
| nursing_care | Nursing Supervisor |
| diagnostics | Diagnostics Department |

**Critical/High severity** → Management

## 🌟 Emerging Theme Discovery

Uses semantic embeddings and clustering:

1. **Embedding**: SentenceTransformer (all-MiniLM-L6-v2)
2. **Clustering**: HDBSCAN for unsupervised grouping
3. **Discovery**: Identifies new complaint patterns automatically

## 📦 Dependencies

Core dependencies:

- **FastAPI**: REST API framework
- **Streamlit**: Interactive dashboard
- **Pandas**: Data processing
- **NumPy**: Numerical computing
- **scikit-learn**: ML algorithms (TF-IDF, Logistic Regression)
- **XGBoost**: Gradient boosting (for potential future use)
- **sentence-transformers**: Semantic embeddings
- **HDBSCAN**: Clustering algorithm
- **Plotly**: Interactive visualizations
- **Joblib**: Model serialization

See `requirements.txt` for exact versions.

## 🔧 Configuration

### Text Cleaning Options

```python
from src.data.text_cleaning import TextCleaner

cleaner = TextCleaner(
    remove_stopwords=True,
    lowercase=True
)
```

### Aspect Detection Options

```python
from src.models.aspect_detector import AspectDetector

detector = AspectDetector(
    use_ml=True,  # Use ML model if available
    model_path="models"
)
```

### Theme Discovery Options

```python
from src.models.theme_discovery import ThemeDiscovery

discoverer = ThemeDiscovery(
    model_name="all-MiniLM-L6-v2",
    model_path="models"
)

themes = discoverer.discover_themes(
    texts=feedback_texts,
    min_cluster_size=10,
    min_samples=5
)
```

## 📚 Example Workflows

### Workflow 1: Analyze Raw Feedback File

```python
from src.data.data_loader import DataLoader
from src.engines.feedback_processor import FeedbackProcessor
import pandas as pd

# Load raw feedback
loader = DataLoader()
df = loader.load_feedback("feedback.csv")

# Process all records
processor = FeedbackProcessor(...)
results = processor.process_dataframe(df, text_column="feedback_text")

# Save processed results
loader.save_processed_feedback(results)
```

### Workflow 2: Real-time API Monitoring

```bash
# Terminal 1: Start API server
python -m uvicorn src.api.main:app --reload

# Terminal 2: Monitor escalations
curl http://localhost:8000/escalations | jq .

# Terminal 3: Submit feedback
curl -X POST "http://localhost:8000/analyze-feedback" \
  -H "Content-Type: application/json" \
  -d '{"feedback_text": "..."}'
```

### Workflow 3: Dashboard Monitoring

```bash
# Start dashboard
streamlit run src/dashboard/app.py

# Access at http://localhost:8501
# View real-time analytics and submit feedback
```

## 🔍 Data Format

### Input: Raw Feedback

```csv
feedback_id,source,feedback_text
FBK001,web_form,"The doctor was helpful but we waited too long"
FBK002,app,"Billing process was confusing"
```

### Output: Processed Feedback

```csv
feedback_id,timestamp,original_text,service_line,aspects,aspect_sentiments,overall_sentiment,staff_category,severity,routing_department,requires_escalation,escalation_reason
FBK001,2024-01-01T10:30:00,The doctor was helpful...,Outpatient Department,doctor_explanation|wait_time,doctor_explanation:positive|wait_time:negative,neutral,doctor,MEDIUM,Medical Services,false,
FBK002,2024-01-01T11:00:00,Billing process was...,Billing Department,billing,billing:negative,negative,billing_staff,MEDIUM,Billing Department,false,
```

## 🧪 Testing

Run a quick test:

```bash
# Generate sample data
python generate_dataset.py

# Test API
python -m uvicorn src.api.main:app --reload

# In another terminal
curl http://localhost:8000/health
curl http://localhost:8000/metrics
```

## 📊 Performance

Expected performance on a modern machine:

- **Single feedback**: <1 second
- **Batch (100 records)**: <10 seconds
- **Bulk upload (10K records)**: <5 minutes
- **Theme discovery**: Depends on data size, typically 1-2 minutes

## 🚫 Limitations & Future Enhancements

### Current Limitations

- Rule-based components may need tuning for specific hospitals
- Theme discovery requires minimum feedback volume (~1000 records)
- No multi-language support currently
- Limited historical trend analysis

### Planned Enhancements

- [ ] Time-series forecasting for trend prediction
- [ ] Anomaly detection for unusual complaints
- [ ] Multi-language support
- [ ] Real-time alert system
- [ ] Advanced NLP for implicit aspect detection
- [ ] Feedback loop for model improvement
- [ ] Database integration (PostgreSQL, MongoDB)
- [ ] Advanced visualizations (3D clustering)
- [ ] Staff performance scoring
- [ ] Department KPI tracking

## 🤝 Contributing

To contribute improvements:

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit with documentation

## 📝 License

This project is provided as-is for healthcare feedback analysis.

## 📧 Support

For issues or questions:

1. Check the `architecture.md` for detailed system information
2. Review example code in docstrings
3. Check data formats in the CSV files

## 🎓 Learning Resources

Key concepts used in this project:

- **TF-IDF**: Text feature extraction for ML
- **Logistic Regression**: Linear classification model
- **Sentence Transformers**: Semantic text embeddings
- **HDBSCAN**: Density-based clustering
- **Rule-based systems**: Domain-specific logic
- **Pipeline orchestration**: Multi-stage processing

## 📄 Citation

If you use SentiMeter in your work, please reference:

```
SentiMeter: Patient Experience Intelligence & Smart Complaint Routing Platform
Version 1.0
2024
```

## ✨ Acknowledgments

Built with:
- scikit-learn for ML foundations
- Sentence Transformers for embeddings
- HDBSCAN for clustering
- FastAPI for REST APIs
- Streamlit for dashboards
- Plotly for visualizations

---

**Ready to get started? Run `python generate_dataset.py` to create sample data, then start the API or dashboard!** 🚀
