# Patient Experience Intelligence & Smart Complaint Routing Platform

## Project Overview
This is an intelligent feedback analysis and complaint routing system designed for hospitals. It processes patient feedback, extracts insights, and automatically routes complaints to appropriate departments with severity assessment.

## System Architecture

### Data Flow
```
Feedback
  ↓
Text Cleaning & Preprocessing
  ↓
Service Line Classification (TF-IDF + Logistic Regression)
  ↓
Aspect Extraction (Rule-Based + Multi-label Classification)
  ↓
Aspect Sentiment Analysis (TF-IDF + Logistic Regression)
  ↓
Staff Category Detection (Rule-Based)
  ↓
Severity Scoring (Rule-Based Engine)
  ↓
Routing Engine (Department Assignment)
  ↓
Emerging Theme Discovery (Sentence Transformer + HDBSCAN)
  ↓
Dashboard & Reporting
```

## Key Components

### 1. Text Cleaning Module (`src/data/text_cleaning.py`)
- Lowercase conversion
- Punctuation removal
- Stop word removal
- Tokenization
- Lemmatization

### 2. Service Line Classifier (`src/models/service_line_classifier.py`)
**Input:** Feedback text
**Output:** Service line category
**Model:** TF-IDF Vectorizer + Logistic Regression
**Categories:**
- Outpatient Department (OPD)
- Emergency Department (ED)
- Inpatient Ward (IP)
- Surgery
- Diagnostic Services
- Billing
- Administration

### 3. Aspect Extraction (`src/models/aspect_detector.py`)
**Approach:** Rule-Based + Multi-label Classification
**Aspects Detected:**
- `wait_time`: Keywords (wait, delay, queue, late)
- `politeness`: Keywords (rude, arrogant, shouted, polite)
- `cleanliness`: Keywords (dirty, smell, unclean)
- `billing`: Keywords (bill, insurance, charges)
- `diagnostics`: Keywords (report, result, scan, lab)
- `discharge_process`: Keywords (discharge, summary, clearance)
- `doctor_explanation`: Keywords (explain, understand, told, informed)
- `nursing_care`: Keywords (nurse, care, attentive, responsive)
- `lab_services`: Keywords (test, lab, blood, sample)

### 4. Aspect Sentiment Analysis (`src/models/aspect_sentiment_classifier.py`)
**Input:** Aspect + Feedback text
**Output:** Sentiment (positive, neutral, negative)
**Model:** TF-IDF Vectorizer + Logistic Regression
**Approach:** Per-aspect sentiment scoring

### 5. Staff Category Detection (`src/engines/staff_detector.py`)
**Method:** Rule-based keyword matching
**Categories:**
- `doctor`: Keywords (doctor, physician, consultant)
- `nursing_staff`: Keywords (nurse, nursing)
- `reception_staff`: Keywords (reception, receptionist, front desk)
- `billing_staff`: Keywords (billing, finance, accounts)
- `diagnostics_staff`: Keywords (lab, technician, radiologist, pathologist)
- `housekeeping`: Keywords (housekeeping, cleaning, janitor)
- `security`: Keywords (security, guard)

### 6. Severity Engine (`src/engines/severity_engine.py`)
**Rule-Based Classification:**
- **CRITICAL:** Safety concerns, wrong medication, patient falls, critical procedures
- **HIGH:** Long delays (>2 hours), serious medical errors, patient harm risk
- **MEDIUM:** Staff rudeness, significant delays (30 min - 2 hours), process failures
- **LOW:** Minor delays, general praise, routine complaints

### 7. Routing Engine (`src/engines/routing_engine.py`)
**Rules-Based Routing:**
- `wait_time` → OPD Operations
- `politeness` → Front Desk
- `doctor_explanation` → Medical Services
- `billing` → Billing Department
- `cleanliness` → Housekeeping
- `nursing_care` → Nursing Supervisor
- `diagnostics` → Diagnostics Department
- **Escalation:** CRITICAL and HIGH severity routed to Management

### 8. Emerging Theme Discovery (`src/models/theme_discovery.py`)
**Method:** Unsupervised clustering on semantic embeddings
**Pipeline:**
1. Generate embeddings using SentenceTransformer (all-MiniLM-L6-v2)
2. Apply HDBSCAN clustering
3. Extract theme labels from cluster centroids
4. Track emerging themes over time

### 9. FastAPI Backend (`src/api/main.py`)
**Endpoints:**
- `POST /analyze-feedback`: Analyze single feedback item
- `POST /bulk-upload`: Bulk upload CSV file
- `GET /metrics`: System-wide metrics
- `GET /department-summary`: Department-wise summary
- `GET /emerging-themes`: Recent emerging themes
- `GET /escalations`: Escalated complaints

### 10. Streamlit Dashboard (`src/dashboard/app.py`)
**Pages:**
1. **Feedback Analyzer:** Real-time feedback analysis
2. **Complaint Queue:** View and manage complaints
3. **Department Trends:** Trend analysis by department
4. **Aspect Analytics:** Aspect-wise sentiment distribution
5. **Escalation Center:** Manage escalated cases
6. **Emerging Themes:** Discover new complaint patterns
7. **Staff Analytics:** Performance metrics by staff
8. **Service Line Analytics:** Service-wise statistics

## Data Storage
- **CSV Format:** All data stored in CSV files for easy access and portability
- **Locations:**
  - `data/feedback.csv`: Raw feedback records
  - `data/processed_feedback.csv`: Analyzed feedback
  - `data/themes.csv`: Emerging themes
  - `data/escalations.csv`: Escalated complaints
  - `models/`: Trained model artifacts (joblib)

## Feedback Record Schema

```json
{
  "feedback_id": "FBK001",
  "timestamp": "2024-01-01 10:30:00",
  "source": "web_form|app|email|phone",
  "feedback_text": "The doctor was very helpful and explained everything",
  "service_line": "OPD",
  "aspects": ["doctor_explanation", "nursing_care"],
  "aspect_sentiments": {"doctor_explanation": "positive", "nursing_care": "positive"},
  "overall_sentiment": "positive",
  "staff_category": "doctor",
  "severity": "LOW",
  "routing_department": "Medical Services",
  "requires_escalation": false,
  "escalation_reason": null,
  "themes": ["staff_communication", "patient_education"]
}
```

## Technology Stack
- **Framework:** FastAPI for REST API
- **Frontend:** Streamlit for interactive dashboard
- **ML Libraries:** scikit-learn, XGBoost
- **NLP:** Sentence Transformers, HDBSCAN
- **Data Processing:** Pandas, NumPy
- **Serialization:** Joblib for model persistence
- **Data Storage:** CSV files

## File Structure
```
SentiMeter/
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── text_cleaning.py
│   │   └── data_loader.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── service_line_classifier.py
│   │   ├── aspect_detector.py
│   │   ├── aspect_sentiment_classifier.py
│   │   └── theme_discovery.py
│   ├── engines/
│   │   ├── __init__.py
│   │   ├── staff_detector.py
│   │   ├── severity_engine.py
│   │   ├── routing_engine.py
│   │   └── feedback_processor.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   └── schemas.py
│   └── dashboard/
│       ├── __init__.py
│       └── app.py
├── data/
│   ├── feedback.csv
│   ├── processed_feedback.csv
│   └── themes.csv
├── models/
│   ├── service_line_model.pkl
│   ├── aspect_model.pkl
│   ├── sentiment_model.pkl
│   └── embeddings/
├── notebooks/
│   └── exploration.ipynb
├── requirements.txt
├── architecture.md
├── generate_dataset.py
└── README.md
```

## Processing Pipeline

1. **Ingestion:** Feedback received via API, form, or bulk upload
2. **Cleaning:** Text preprocessing and normalization
3. **Classification:** Service line and aspect detection
4. **Sentiment:** Aspect-level sentiment analysis
5. **Detection:** Staff category and severity determination
6. **Routing:** Automatic department assignment
7. **Discovery:** Emerging theme identification
8. **Storage:** Results saved to CSV
9. **Visualization:** Dashboard updates in real-time

## Performance Metrics
- **Accuracy Targets:**
  - Service Line Classification: >90%
  - Aspect Detection: >85%
  - Sentiment Analysis: >85%
  - Severity Classification: >95% (rule-based)
  - Routing Accuracy: >95% (rule-based)

- **Processing:**
  - Single feedback: <1 second
  - Bulk upload (10K records): <5 minutes

## Future Enhancements
- Time-series analysis for trend forecasting
- Anomaly detection for unusual complaints
- Multi-language support
- Real-time alerts for critical feedback
- Advanced NLP for implicit aspect detection
- Feedback loop for model improvement
