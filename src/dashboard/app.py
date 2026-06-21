"""
Streamlit Dashboard for SentiMeter.
Interactive dashboard for visualizing and analyzing patient feedback.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from src.data.data_loader import DataLoader
from src.models.aspect_detector import AspectDetector
from src.models.service_line_classifier import ServiceLineClassifier
from src.models.aspect_sentiment_classifier import AspectSentimentClassifier
from src.engines.feedback_processor import FeedbackProcessor

PIPELINE_VERSION = "clause-routing-v3"

# Page configuration
st.set_page_config(
    page_title="SentiMeter Dashboard",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
        .metric-card {
            background-color: #f0f2f6;
            padding: 20px;
            border-radius: 10px;
            margin: 10px 0;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize components
@st.cache_resource
def initialize_components(pipeline_version: str):
    """Initialize all components once."""
    try:
        aspect_detector = AspectDetector()
        service_line_classifier = ServiceLineClassifier()
        aspect_sentiment_classifier = AspectSentimentClassifier()
        feedback_processor = FeedbackProcessor(
            aspect_detector,
            service_line_classifier,
            aspect_sentiment_classifier
        )
        data_loader = DataLoader()
        return feedback_processor, data_loader
    except Exception as e:
        st.error(f"Error initializing components: {e}")
        return None, None


# Load data
@st.cache_data(ttl=300)
def load_data():
    """Load processed feedback data."""
    _, data_loader = initialize_components(PIPELINE_VERSION)
    if data_loader is None:
        return pd.DataFrame()
    
    df = data_loader.load_feedback("processed_feedback.csv")
    if df.empty:
        # Try loading raw data
        df = data_loader.load_feedback("feedback.csv")
    
    return df


# Sidebar navigation
st.sidebar.title("🏥 SentiMeter")
st.sidebar.markdown("Patient Experience Intelligence Platform")
st.sidebar.markdown("---")

page = st.sidebar.radio(
    "Select Page",
    [
        "📊 Dashboard Overview",
        "🔍 Feedback Analyzer",
        "📋 Complaint Queue",
        "📈 Department Trends",
        "🎯 Aspect Analytics",
        "⚠️ Escalation Center",
        "🌟 Emerging Themes",
        "👥 Staff Analytics"
    ]
)

# ============================================================================
# PAGE 1: DASHBOARD OVERVIEW
# ============================================================================
if page == "📊 Dashboard Overview":
    st.title("Dashboard Overview")
    
    df = load_data()
    
    if df.empty:
        st.warning("No data loaded. Please generate or upload feedback data first.")
        st.stop()
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Total Feedbacks",
            value=len(df),
            delta=len(df) if len(df) > 0 else 0
        )
    
    with col2:
        escalations = df["requires_escalation"].sum() if "requires_escalation" in df.columns else 0
        st.metric(
            label="Escalations",
            value=int(escalations),
            delta="critical issues"
        )
    
    with col3:
        if "overall_sentiment" in df.columns:
            positive = (df["overall_sentiment"] == "positive").sum()
            st.metric(
                label="Positive Feedback",
                value=int(positive),
                delta=f"{(positive/len(df)*100):.1f}%"
            )
    
    with col4:
        if "overall_sentiment" in df.columns:
            negative = (df["overall_sentiment"] == "negative").sum()
            st.metric(
                label="Negative Feedback",
                value=int(negative),
                delta=f"{(negative/len(df)*100):.1f}%"
            )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sentiment Distribution")
        if "overall_sentiment" in df.columns:
            sentiment_counts = df["overall_sentiment"].value_counts()
            fig = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                color_discrete_map={"positive": "#2ecc71", "neutral": "#95a5a6", "negative": "#e74c3c"}
            )
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("Severity Distribution")
        if "severity" in df.columns:
            severity_counts = df["severity"].value_counts()
            color_map = {"CRITICAL": "#e74c3c", "HIGH": "#e67e22", "MEDIUM": "#f39c12", "LOW": "#2ecc71"}
            fig = px.pie(
                values=severity_counts.values,
                names=severity_counts.index,
                color_discrete_map=color_map
            )
            st.plotly_chart(fig, width='stretch')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Department Distribution")
        if "routing_department" in df.columns:
            dept_counts = df["routing_department"].value_counts().head(10)
            fig = px.bar(
                x=dept_counts.values,
                y=dept_counts.index,
                orientation='h',
                color=dept_counts.values,
                color_continuous_scale='Blues'
            )
            fig.update_layout(showlegend=False, xaxis_title="Count", yaxis_title="Department")
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("Service Line Distribution")
        if "service_line" in df.columns:
            service_counts = df["service_line"].value_counts()
            fig = px.bar(
                x=service_counts.index,
                y=service_counts.values,
                color=service_counts.values,
                color_continuous_scale='Greens'
            )
            fig.update_layout(showlegend=False, xaxis_title="Service Line", yaxis_title="Count")
            st.plotly_chart(fig, width='stretch')


# ============================================================================
# PAGE 2: FEEDBACK ANALYZER
# ============================================================================
elif page == "🔍 Feedback Analyzer":
    st.title("Real-time Feedback Analyzer")
    
    feedback_processor, _ = initialize_components(PIPELINE_VERSION)
    
    if feedback_processor is None:
        st.error("Components not initialized")
        st.stop()
    
    # Input area
    st.subheader("Analyze Single Feedback")
    feedback_text = st.text_area(
        "Enter feedback text:",
        height=150,
        placeholder="Paste patient feedback here..."
    )
    
    if st.button("🔍 Analyze Feedback", width='stretch'):
        if feedback_text.strip():
            with st.spinner("Analyzing feedback..."):
                result = feedback_processor.process_single(feedback_text)

            # Clause Analysis
            st.subheader("Clause Analysis")

            if result.get("clause_analysis"):
                rows = [
                    {
                        "Clause": item["clause"],
                        "Staff": item["staff_category"],
                        "Aspects": ", ".join(item["aspects"]),
                        "Sentiment": item["overall_sentiment"]
                    }
                    for item in result["clause_analysis"]
                ]

                clause_df = pd.DataFrame(rows)
                st.dataframe(clause_df, width='stretch')
            else:
                st.info("No clauses were detected in this feedback.")

            # Display results
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Service Line", result["service_line"])
            
            with col2:
                st.metric("Severity", result["severity"])
            
            with col3:
                st.metric("Staff Category", result["staff_category"])
            
            st.markdown("---")
            
            # Aspects and sentiments
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Detected Aspects")
                for aspect in result["aspects"]:
                    st.write(f"• {aspect}")
            
            with col2:
                st.subheader("Aspect Sentiments")
                for aspect, sentiment in result["aspect_sentiments"].items():
                    emoji = "😊" if sentiment == "positive" else "😐" if sentiment == "neutral" else "😞"
                    st.write(f"• {aspect}: {emoji} {sentiment}")
            
            st.markdown("---")
            
            # Routing information
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("Routing Information")
                st.write(f"**Department:** {result['routing_department']}")
                st.write(f"**Overall Sentiment:** {result['overall_sentiment']}")
            
            with col2:
                st.subheader("Escalation Status")
                if result["requires_escalation"]:
                    st.error(f"⚠️ **ESCALATED**: {result['escalation_reason']}")
                else:
                    st.success("✓ No escalation required")
        else:
            st.warning("Please enter feedback text")


# ============================================================================
# PAGE 3: COMPLAINT QUEUE
# ============================================================================
elif page == "📋 Complaint Queue":
    st.title("Complaint Queue")
    
    df = load_data()
    
    if df.empty:
        st.warning("No data available")
        st.stop()
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        severity_filter = st.multiselect(
            "Filter by Severity",
            options=["CRITICAL", "HIGH", "MEDIUM", "LOW"],
            default=["CRITICAL", "HIGH"]
        )
    
    with col2:
        if "overall_sentiment" in df.columns:
            sentiment_filter = st.multiselect(
                "Filter by Sentiment",
                options=df["overall_sentiment"].unique(),
                default=None
            )
        else:
            sentiment_filter = None
    
    with col3:
        if "routing_department" in df.columns:
            dept_filter = st.multiselect(
                "Filter by Department",
                options=df["routing_department"].unique(),
                default=None
            )
        else:
            dept_filter = None
    
    # Apply filters
    filtered_df = df.copy()
    
    if "severity" in filtered_df.columns and severity_filter:
        filtered_df = filtered_df[filtered_df["severity"].isin(severity_filter)]
    
    if sentiment_filter and "overall_sentiment" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["overall_sentiment"].isin(sentiment_filter)]
    
    if dept_filter and "routing_department" in filtered_df.columns:
        filtered_df = filtered_df[filtered_df["routing_department"].isin(dept_filter)]
    
    # Display queue
    st.subheader(f"Queue ({len(filtered_df)} complaints)")
    
    # Display as table
    display_cols = ["feedback_id", "feedback_text", "severity", "overall_sentiment", "routing_department"]
    display_cols = [col for col in display_cols if col in filtered_df.columns]
    
    st.dataframe(
        filtered_df[display_cols].head(20),
        width='stretch',
        height=500
    )


# ============================================================================
# PAGE 4: DEPARTMENT TRENDS
# ============================================================================
elif page == "📈 Department Trends":
    st.title("Department Trends")
    
    df = load_data()
    
    if df.empty or "routing_department" not in df.columns:
        st.warning("No data available")
        st.stop()
    
    # Department selection
    departments = df["routing_department"].unique()
    selected_dept = st.selectbox("Select Department", departments)
    
    dept_df = df[df["routing_department"] == selected_dept]
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Complaints", len(dept_df))
    
    with col2:
        if "severity" in dept_df.columns:
            st.metric("Critical Issues", (dept_df["severity"] == "CRITICAL").sum())
    
    with col3:
        if "requires_escalation" in dept_df.columns:
            st.metric("Escalations", dept_df["requires_escalation"].sum())
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Sentiment Distribution")
        if "overall_sentiment" in dept_df.columns:
            sentiment_counts = dept_df["overall_sentiment"].value_counts()
            fig = px.pie(
                values=sentiment_counts.values,
                names=sentiment_counts.index,
                color_discrete_map={"positive": "#2ecc71", "neutral": "#95a5a6", "negative": "#e74c3c"}
            )
            st.plotly_chart(fig, width='stretch')
    
    with col2:
        st.subheader("Severity Distribution")
        if "severity" in dept_df.columns:
            severity_counts = dept_df["severity"].value_counts()
            fig = px.bar(
                x=severity_counts.index,
                y=severity_counts.values,
                color=severity_counts.index,
                color_discrete_map={"CRITICAL": "#e74c3c", "HIGH": "#e67e22", "MEDIUM": "#f39c12", "LOW": "#2ecc71"}
            )
            st.plotly_chart(fig, width='stretch')


# ============================================================================
# PAGE 5: ASPECT ANALYTICS
# ============================================================================
elif page == "🎯 Aspect Analytics":
    st.title("Aspect Analytics")
    
    df = load_data()
    
    if df.empty or "aspects" not in df.columns:
        st.warning("No data available")
        st.stop()
    
    # Expand aspects
    all_aspects = []
    for aspects_str in df["aspects"]:
        if isinstance(aspects_str, str):
            aspects = aspects_str.split("|")
            all_aspects.extend(aspects)
    
    # Count aspects
    from collections import Counter
    aspect_counts = Counter(all_aspects)
    
    # Display aspect distribution
    st.subheader("Aspect Frequency")
    aspect_df = pd.DataFrame(
        list(aspect_counts.items()),
        columns=["Aspect", "Count"]
    ).sort_values("Count", ascending=False)
    
    fig = px.bar(
        aspect_df,
        x="Aspect",
        y="Count",
        color="Count",
        color_continuous_scale="Viridis"
    )
    st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Aspect-wise sentiment analysis
    st.subheader("Sentiment by Aspect")
    
    if "aspect_sentiments" in df.columns:
        # Parse aspect sentiments
        aspect_sentiment_data = []
        
        for _, row in df.iterrows():
            aspects_str = row.get("aspects", "")
            sentiments_str = row.get("aspect_sentiments", "")
            
            if isinstance(aspects_str, str) and isinstance(sentiments_str, str):
                aspects = aspects_str.split("|")
                for aspect in aspects:
                    aspect_sentiment_data.append({"aspect": aspect})
        
        if aspect_sentiment_data:
            sentiment_df = pd.DataFrame(aspect_sentiment_data)
            fig = px.histogram(
                sentiment_df,
                x="aspect",
                color="aspect",
                barmode="group"
            )
            st.plotly_chart(fig, width='stretch')


# ============================================================================
# PAGE 6: ESCALATION CENTER
# ============================================================================
elif page == "⚠️ Escalation Center":
    st.title("Escalation Center")
    
    df = load_data()
    
    if df.empty or "requires_escalation" not in df.columns:
        st.warning("No data available")
        st.stop()
    
    escalations = df[df["requires_escalation"] == True]
    
    # Metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Escalations", len(escalations))
    
    with col2:
        if "severity" in escalations.columns:
            critical = (escalations["severity"] == "CRITICAL").sum()
            st.metric("Critical Issues", int(critical))
    
    with col3:
        if len(df) > 0:
            escalation_rate = (len(escalations) / len(df)) * 100
            st.metric("Escalation Rate", f"{escalation_rate:.1f}%")
    
    st.markdown("---")
    
    # Display escalations
    st.subheader("Escalated Complaints")
    
    if not escalations.empty:
        display_cols = [col for col in ["feedback_id", "feedback_text", "severity", "escalation_reason", "routing_department"] if col in escalations.columns]
        st.dataframe(
            escalations[display_cols].head(20),
            width='stretch',
            height=500
        )
    else:
        st.success("✓ No escalations!")


# ============================================================================
# PAGE 7: EMERGING THEMES
# ============================================================================
elif page == "🌟 Emerging Themes":
    st.title("Emerging Themes")
    
    st.info("Emerging themes are detected using semantic clustering of feedback texts.")
    
    st.markdown("""
    This feature uses:
    - **SentenceTransformer** for semantic embeddings
    - **HDBSCAN** for clustering unknown themes
    """)
    
    st.subheader("Detected Themes")
    st.info("Emerging theme detection requires sufficient data. Analyze more feedback to discover patterns.")


# ============================================================================
# PAGE 8: STAFF ANALYTICS
# ============================================================================
elif page == "👥 Staff Analytics":
    st.title("Staff Analytics")
    
    df = load_data()
    
    if df.empty or "staff_category" not in df.columns:
        st.warning("No data available")
        st.stop()
    
    # Staff category distribution
    st.subheader("Feedback by Staff Category")
    staff_counts = df["staff_category"].value_counts()
    
    fig = px.bar(
        x=staff_counts.index,
        y=staff_counts.values,
        color=staff_counts.values,
        color_continuous_scale="Plasma",
        labels={"x": "Staff Category", "y": "Number of Feedbacks"}
    )
    st.plotly_chart(fig, width='stretch')
    
    st.markdown("---")
    
    # Staff-wise sentiment analysis
    st.subheader("Sentiment by Staff Category")
    
    if "overall_sentiment" in df.columns:
        # Create cross-tabulation
        staff_sentiment = pd.crosstab(
            df["staff_category"],
            df["overall_sentiment"]
        )
        
        fig = px.bar(
            staff_sentiment,
            barmode="group",
            color_discrete_map={"positive": "#2ecc71", "neutral": "#95a5a6", "negative": "#e74c3c"}
        )
        fig.update_layout(
            xaxis_title="Staff Category",
            yaxis_title="Count"
        )
        st.plotly_chart(fig, width='stretch')


# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #888;">
    <small>SentiMeter v1.0 • Patient Experience Intelligence Platform</small>
</div>
""", unsafe_allow_html=True)
