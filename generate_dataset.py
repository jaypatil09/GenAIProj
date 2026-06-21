"""
Generate synthetic hospital patient feedback data for training and testing.
Creates 10,000 realistic feedback records with all required fields.
"""

import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

# Feedback templates and keywords
POSITIVE_TEMPLATES = [
    "The {staff} was very helpful and explained everything clearly.",
    "Great experience at {service_line}. The staff was polite and attentive.",
    "Very satisfied with the {aspect} provided. Highly recommend.",
    "The {staff} took care of me promptly and professionally.",
    "Excellent service and clean facilities. Very impressed.",
    "The team was courteous and the process was smooth.",
    "Couldn't ask for better care. Staff was very responsive.",
    "Very happy with the treatment and explanation provided.",
]

NEGATIVE_TEMPLATES = [
    "Had to wait for {wait_time} hours at {service_line}. Very frustrated.",
    "The {staff} was rude and dismissive. Poor experience.",
    "The facilities were dirty and smelly. Unacceptable.",
    "Billing was confusing and the {staff} was unhelpful.",
    "Waited too long and no one explained the {aspect} properly.",
    "The {staff} shouted at me without any reason.",
    "Got the {aspect} report with a 3-day delay.",
    "Very disappointed with the {aspect} provided. Staff was arrogant.",
]

NEUTRAL_TEMPLATES = [
    "The experience at {service_line} was average. Nothing special.",
    "Process took time but eventually got {aspect} done.",
    "The staff was neither particularly helpful nor rude.",
    "Facilities were okay but could be cleaner.",
    "The {aspect} was handled routinely without issues.",
    "Experience was satisfactory but with minor delays.",
    "Everything was as expected for {service_line}.",
]

SERVICE_LINES = [
    "Outpatient Department",
    "Emergency Department",
    "Inpatient Ward",
    "Surgery",
    "Diagnostic Services",
    "Billing Department",
    "Administration"
]

STAFF_TYPES = [
    "doctor",
    "nurse",
    "receptionist",
    "billing staff",
    "lab technician",
    "radiologist",
    "housekeeping staff",
    "security guard"
]

ASPECTS = [
    "wait_time",
    "politeness",
    "cleanliness",
    "billing",
    "diagnostics",
    "discharge_process",
    "doctor_explanation",
    "nursing_care",
    "lab_services"
]

SOURCES = ["web_form", "mobile_app", "email", "phone", "in_person"]

SENTIMENT_MAP = {
    "positive": ["positive", "satisfied", "great", "excellent", "helpful", "polite", "responsive", "courteous"],
    "negative": ["negative", "disappointed", "frustrated", "rude", "arrogant", "dirty", "delayed", "unhelpful"],
    "neutral": ["average", "okay", "satisfactory", "routine", "normal", "adequate"]
}

STAFF_KEYWORDS = {
    "doctor": ["doctor", "physician", "consultant", "specialist"],
    "nursing_staff": ["nurse", "nursing", "ward nurse", "icu nurse"],
    "reception_staff": ["receptionist", "reception", "front desk", "check-in"],
    "billing_staff": ["billing", "finance", "accounts", "payment"],
    "diagnostics_staff": ["lab", "technician", "radiologist", "pathologist", "phlebotomist"],
    "housekeeping": ["housekeeping", "cleaning", "janitor", "staff", "cleaner"],
    "security": ["security", "guard"]
}

ASPECT_KEYWORDS = {
    "wait_time": ["wait", "delay", "queue", "late", "long time", "took hours"],
    "politeness": ["rude", "arrogant", "shouted", "polite", "courteous", "respectful"],
    "cleanliness": ["dirty", "smell", "unclean", "clean", "hygiene", "facilities"],
    "billing": ["bill", "insurance", "charges", "payment", "expensive", "affordable"],
    "diagnostics": ["report", "result", "scan", "lab", "test"],
    "discharge_process": ["discharge", "summary", "clearance", "checkout"],
    "doctor_explanation": ["explain", "understand", "told", "informed", "communication"],
    "nursing_care": ["nurse", "care", "attentive", "responsive", "support"],
    "lab_services": ["lab", "test", "blood", "sample", "results"]
}

SEVERITY_RULES = {
    "CRITICAL": ["safety", "medication error", "patient fall", "allergy", "infection", "heart attack", "critical"],
    "HIGH": ["wrong", "error", "major issue", "serious", "harm", "3 hours", "4 hours"],
    "MEDIUM": ["rude", "delayed", "2 hours", "inconvenience", "confusion"],
    "LOW": ["positive", "good", "satisfied", "excellent", "happy", "great"]
}

DEPARTMENTS = [
    "OPD Operations",
    "ED Operations",
    "Nursing Supervisor",
    "Medical Services",
    "Surgical Services",
    "Diagnostics Department",
    "Billing Department",
    "Housekeeping",
    "Front Desk",
    "Management"
]


def get_random_date(days_back=90):
    """Generate a random date within the last N days."""
    end = datetime.now()
    start = end - timedelta(days=days_back)
    random_date = start + timedelta(
        seconds=random.randint(0, int((end - start).total_seconds()))
    )
    return random_date.strftime("%Y-%m-%d %H:%M:%S")


def extract_staff_category(text):
    """Extract staff category from feedback text using rules."""
    text_lower = text.lower()
    for category, keywords in STAFF_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            return category
    return "general_staff"


def extract_aspects(text):
    """Extract aspects mentioned in the text."""
    text_lower = text.lower()
    detected_aspects = []
    
    for aspect, keywords in ASPECT_KEYWORDS.items():
        if any(keyword in text_lower for keyword in keywords):
            detected_aspects.append(aspect)
    
    # Ensure at least one aspect is detected
    if not detected_aspects:
        detected_aspects = [random.choice(ASPECTS)]
    
    return detected_aspects[:3]  # Max 3 aspects per feedback


def determine_sentiment_for_aspect(text, aspect):
    """Determine sentiment for a specific aspect."""
    text_lower = text.lower()
    
    # Check for positive indicators
    positive_found = any(word in text_lower for word in SENTIMENT_MAP["positive"])
    # Check for negative indicators
    negative_found = any(word in text_lower for word in SENTIMENT_MAP["negative"])
    
    if positive_found and not negative_found:
        return "positive"
    elif negative_found and not positive_found:
        return "negative"
    elif positive_found and negative_found:
        # Mixed sentiment - randomly pick or lean negative for complaints
        return random.choice(["negative", "neutral", "negative"])
    else:
        return "neutral"


def determine_severity(text, sentiment):
    """Determine severity based on content and sentiment."""
    text_lower = text.lower()
    
    # Check for critical keywords
    for keyword in SEVERITY_RULES["CRITICAL"]:
        if keyword in text_lower:
            return "CRITICAL"
    
    # Check for high severity keywords
    for keyword in SEVERITY_RULES["HIGH"]:
        if keyword in text_lower:
            return "HIGH"
    
    # Check for medium severity keywords
    for keyword in SEVERITY_RULES["MEDIUM"]:
        if keyword in text_lower:
            return "MEDIUM"
    
    # Default based on sentiment
    if sentiment == "positive":
        return "LOW"
    elif sentiment == "negative":
        return random.choice(["MEDIUM", "HIGH"])
    else:
        return "MEDIUM"


def generate_feedback_text(sentiment_type, service_line, aspect, staff_type):
    """Generate realistic feedback text."""
    if sentiment_type == "positive":
        template = random.choice(POSITIVE_TEMPLATES)
    elif sentiment_type == "negative":
        template = random.choice(NEGATIVE_TEMPLATES)
    else:
        template = random.choice(NEUTRAL_TEMPLATES)
    
    # Replace placeholders
    text = template.replace("{staff}", staff_type)
    text = text.replace("{service_line}", service_line)
    text = text.replace("{aspect}", aspect)
    text = text.replace("{wait_time}", str(random.randint(1, 5)))
    
    return text


def generate_dataset(num_records=10000):
    """Generate synthetic feedback dataset."""
    
    print(f"Generating {num_records} synthetic feedback records...")
    
    records = []
    
    sentiment_distribution = ["positive", "negative", "neutral", "mixed"]
    
    for i in range(num_records):
        if (i + 1) % 1000 == 0:
            print(f"  Generated {i + 1}/{num_records} records...")
        
        # Choose sentiment type
        sentiment_type = random.choices(
            sentiment_distribution,
            weights=[0.40, 0.35, 0.15, 0.10]
        )[0]
        
        # Choose base sentiment
        if sentiment_type == "mixed":
            overall_sentiment = random.choice(["positive", "negative", "neutral"])
            sentiment_type = random.choice(["positive", "negative"])
        else:
            overall_sentiment = sentiment_type
        
        # Choose service line and staff
        service_line = random.choice(SERVICE_LINES)
        staff_category = random.choice(STAFF_TYPES)
        
        # Choose aspect
        aspect = random.choice(ASPECTS)
        
        # Generate feedback text
        feedback_text = generate_feedback_text(
            sentiment_type, service_line, aspect, staff_category
        )
        
        # Extract aspects from text (may find multiple)
        detected_aspects = extract_aspects(feedback_text)
        
        # Generate aspect sentiments
        aspect_sentiments = {}
        for asp in detected_aspects:
            aspect_sentiments[asp] = determine_sentiment_for_aspect(
                feedback_text, asp
            )
        
        # Determine severity
        severity = determine_severity(feedback_text, overall_sentiment)
        
        # Determine if escalation needed
        requires_escalation = severity in ["CRITICAL", "HIGH"]
        escalation_reason = None
        if requires_escalation:
            escalation_reason = f"{severity} severity complaint"
        
        # Route to department
        if "wait_time" in detected_aspects:
            routing_department = "OPD Operations"
        elif "politeness" in detected_aspects:
            routing_department = "Front Desk"
        elif "doctor_explanation" in detected_aspects:
            routing_department = "Medical Services"
        elif "billing" in detected_aspects:
            routing_department = "Billing Department"
        elif "cleanliness" in detected_aspects:
            routing_department = "Housekeeping"
        elif "nursing_care" in detected_aspects:
            routing_department = "Nursing Supervisor"
        elif "diagnostics" in detected_aspects:
            routing_department = "Diagnostics Department"
        else:
            routing_department = random.choice(DEPARTMENTS)
        
        # Add escalation for critical/high severity
        if requires_escalation:
            routing_department = "Management"
        
        record = {
            "feedback_id": f"FBK{i+1:06d}",
            "timestamp": get_random_date(),
            "source": random.choice(SOURCES),
            "feedback_text": feedback_text,
            "service_line": service_line,
            "aspects": "|".join(detected_aspects),
            "aspect_sentiments": "|".join([f"{asp}:{sent}" for asp, sent in aspect_sentiments.items()]),
            "overall_sentiment": overall_sentiment,
            "staff_category": extract_staff_category(feedback_text),
            "severity": severity,
            "routing_department": routing_department,
            "requires_escalation": requires_escalation,
            "escalation_reason": escalation_reason or ""
        }
        
        records.append(record)
    
    # Create DataFrame
    df = pd.DataFrame(records)
    
    # Create data directory if it doesn't exist
    data_dir = os.path.join(os.path.dirname(__file__), "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Save to CSV
    output_path = os.path.join(data_dir, "feedback.csv")
    df.to_csv(output_path, index=False)
    
    print(f"\n✓ Dataset generated successfully!")
    print(f"  Total records: {len(df)}")
    print(f"  Output file: {output_path}")
    print(f"\nDataset summary:")
    print(f"  Sentiment distribution:\n{df['overall_sentiment'].value_counts()}")
    print(f"\n  Service line distribution:\n{df['service_line'].value_counts()}")
    print(f"\n  Severity distribution:\n{df['severity'].value_counts()}")
    print(f"\n  Source distribution:\n{df['source'].value_counts()}")
    
    return df


if __name__ == "__main__":
    generate_dataset(num_records=10000)
