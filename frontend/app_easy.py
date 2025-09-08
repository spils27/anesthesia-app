import streamlit as st
import requests
from datetime import datetime, timedelta
import time
import pandas as pd
import json
from typing import Optional
import os

# API configuration
API_URL = "http://localhost:8000/api"

# Page config
st.set_page_config(
    page_title="Anesthesia Record System - EASy",
    page_icon="💉",
    layout="wide"
)

# Custom CSS for EASy styling
st.markdown("""
<style>
    /* Set white background for main containers */
    .main {
        background-color: white;
        color: #2d3748;
    }
    .stApp {
        background-color: white;
        color: #2d3748;
    }
    [data-testid="stAppViewContainer"] {
        background-color: white;
        color: #2d3748;
    }
    [data-testid="stHeader"] {
        background-color: white;
        color: #2d3748;
    }
    
    /* Professional text colors with good contrast */
    .stMarkdown, .stText, p, span, div, label {
        color: #2d3748 !important;  /* Dark gray-blue for body text */
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1a365d !important;  /* Dark blue for headings */
    }
    
    /* Bold text slightly darker */
    strong, b {
        color: #1a202c !important;  /* Very dark gray */
    }
    
    /* Fix black text in specific elements */
    .stMarkdown p, .stMarkdown span {
        color: #2d3748 !important;
    }
    
    /* Ensure all text in columns has proper color */
    div[data-testid="column"] p,
    div[data-testid="column"] span,
    div[data-testid="column"] label {
        color: #2d3748 !important;
    }
    
    /* Override inline styles that might be setting black color */
    div[style*="color: black"] {
        color: #2d3748 !important;
    }
    
    /* Specific fixes for form labels */
    .stTextInput label p,
    .stNumberInput label p,
    .stSelectbox label p,
    .stDateInput label p,
    .stTextArea label p {
        color: #2d3748 !important;
    }
    
    /* Tab styling */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
        background-color: white;
    }
    .stTabs [data-baseweb="tab"] {
        padding: 8px 16px;
        background-color: #e0e0e0;
        color: black;
    }
    .stTabs [aria-selected="true"] {
        background-color: #4CAF50;
        color: white;
    }
    div[data-testid="column"] {
        padding: 5px;
    }
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        background-color: white;
        color: black;
    }
    
    /* Ensure all sections have white background */
    section[data-testid="stSidebar"] {
        background-color: #f0f0f0;
        color: black;
    }
    .element-container {
        background-color: white;
        color: black;
    }
    
    /* Professional Medical Form Color Scheme */
    /* Input fields - Light blue-gray background with dark blue text for better readability */
    .stTextInput > div > div > input {
        color: #1a365d !important;  /* Dark blue text */
        background-color: #f7fafc !important;  /* Very light blue-gray */
        border: 1px solid #cbd5e0 !important;  /* Soft gray-blue border */
    }
    .stNumberInput > div > div > input {
        color: #1a365d !important;
        background-color: #f7fafc !important;
        border: 1px solid #cbd5e0 !important;
    }
    .stSelectbox > div > div > div {
        color: #1a365d !important;
        background-color: #f7fafc !important;
    }
    .stTextArea > div > div > textarea {
        color: #1a365d !important;
        background-color: #f7fafc !important;
        border: 1px solid #cbd5e0 !important;
    }
    .stDateInput > div > div > input {
        color: #1a365d !important;
        background-color: #f7fafc !important;
        border: 1px solid #cbd5e0 !important;
    }
    
    /* Fix for date input containers and other black elements */
    div[data-baseweb="input"] {
        background-color: #f7fafc !important;
    }
    
    /* Fix black background on date inputs specifically */
    .stDateInput > div > div {
        background-color: transparent !important;
    }
    
    /* Fix for any element with black background */
    div[style*="background-color: black"],
    div[style*="background: black"],
    div[style*="background-color: rgb(0, 0, 0)"] {
        background-color: #f7fafc !important;
    }
    
    /* Specific fix for number input spinners */
    .stNumberInput > div > div > div {
        background-color: #f7fafc !important;
    }
    
    /* Fix for all baseui inputs */
    [data-baseweb="base-input"] {
        background-color: #f7fafc !important;
    }
    
    /* Override any inline black styles */
    *[style*="background-color: black"] {
        background-color: #f7fafc !important;
    }
    
    /* Radio buttons and checkboxes - Professional medical blue */
    .stRadio > div > label {
        color: #2c5282 !important;  /* Medium blue */
    }
    .stCheckbox > label {
        color: #2c5282 !important;
    }
    
    /* Radio/checkbox selected state */
    .stRadio > div > label > div[data-checked="true"] {
        background-color: #2b6cb0 !important;
    }
    
    /* Buttons - Medical green for primary actions */
    .stButton > button {
        background-color: #48bb78;  /* Medical green */
        color: white !important;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        background-color: #38a169;  /* Darker green on hover */
        transform: translateY(-1px);
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Primary button styling */
    .stButton > button[kind="primary"] {
        background-color: #3182ce !important;  /* Medical blue */
        color: white !important;
    }
    
    .stButton > button[kind="primary"]:hover {
        background-color: #2c5282 !important;
    }
    
    /* Secondary button styling */
    .stButton > button[kind="secondary"] {
        background-color: #718096 !important;  /* Gray */
        color: white !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background-color: #4a5568 !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'record_id' not in st.session_state:
    st.session_state.record_id = None
if 'patient_id' not in st.session_state:
    st.session_state.patient_id = st.query_params.get('patient_id', '11')
if 'location_id' not in st.session_state:
    st.session_state.location_id = 1
if 'last_save' not in st.session_state:
    st.session_state.last_save = datetime.now()
if 'medications_given' not in st.session_state:
    st.session_state.medications_given = []
if 'vital_signs' not in st.session_state:
    st.session_state.vital_signs = []

# Helper functions
def api_get(endpoint):
    try:
        response = requests.get(f"{API_URL}{endpoint}")
        response.raise_for_status()
        return response.json()
    except:
        return None

def api_post(endpoint, data):
    try:
        response = requests.post(f"{API_URL}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        return None

def api_put(endpoint, data):
    try:
        response = requests.put(f"{API_URL}{endpoint}", json=data)
        response.raise_for_status()
        return response.json()
    except:
        return None

def load_patient():
    if st.session_state.patient_id:
        patient = api_get(f"/patients/{st.session_state.patient_id}")
        if not patient:
            # Create dummy patient for demo
            patient_data = {
                "open_dental_id": st.session_state.patient_id,
                "first_name": "Allen",
                "last_name": "Allowed",
                "date_of_birth": "1980-05-06T00:00:00",
                "medical_record_number": "11"
            }
            patient = api_post("/patients/", patient_data)
        return patient
    return None

def create_or_load_record():
    if not st.session_state.record_id and st.session_state.patient_id:
        patient = load_patient()
        if patient:
            record_data = {
                "patient_id": patient["id"],
                "location_id": st.session_state.location_id
            }
            record = api_post("/records/", record_data)
            if record:
                st.session_state.record_id = record["id"]
                return record
    elif st.session_state.record_id:
        return api_get(f"/records/{st.session_state.record_id}")
    return None

def save_record():
    if st.session_state.record_id:
        # Implementation remains same
        return True
    return False

# Main app
def main():
    # Create or load record
    record = create_or_load_record()
    patient = load_patient()
    
    # Tabs - Preop Checklist first
    tab1, tab2, tab3, tab4 = st.tabs(["Preop Checklist", "Anesthetic Record", "Post Anesthesia Score", "Inventory"])
    
    with tab1:
        render_preop_checklist_tab()
    
    with tab2:
        render_anesthetic_record_tab()
    
    with tab3:
        render_post_anesthesia_score_tab()
        
    with tab4:
        render_inventory_tab()

def render_preop_checklist_tab():
    patient = load_patient()
    
    # Custom CSS for bordered sections with different colors
    st.markdown("""
    <style>
    .header-section { 
        background-color: #e6f2ff;  /* Light blue like PDF */
        border: 2px solid #000;  /* Black borders like PDF */
        padding: 0px; 
        margin-bottom: 0px;
    }
    .sedation-section { 
        background-color: #f0f8ff;  /* Very light blue */
        border: 2px solid #000; 
        border-top: none;
        padding: 0px; 
        margin-bottom: 0px;
    }
    .vitals-section { 
        background-color: #f0fdf4;  /* Soft green */
        border: 2px solid #000; 
        border-top: none;
        padding: 0px; 
        margin-bottom: 0px;
    }
    .equipment-section { 
        background-color: #fffacd;  /* Light yellow like PDF */
        border: 2px solid #000; 
        border-top: none;
        padding: 0px; 
        margin-bottom: 0px;
    }
    .medical-review-section { 
        background-color: #f5e6ff;  /* Light purple like PDF */
        border: 2px solid #000; 
        border-top: none;
        padding: 0px; 
        margin-bottom: 0px;
    }
    .special-section { 
        background-color: #fef2f2;  /* Light pink like PDF */
        border: 2px solid #000; 
        border-top: none;
        padding: 0px; 
        margin-bottom: 0px;
    }
    
    /* Table-like cell borders */
    .form-row {
        border-bottom: 2px solid #000;
        padding: 0;
        margin: 0;
    }
    
    .form-row:last-child {
        border-bottom: none;
    }
    
    .form-cell {
        border-right: 2px solid #000;
        padding: 8px;
        min-height: 40px;
        display: flex;
        align-items: center;
    }
    
    .form-cell:last-child {
        border-right: none;
    }
    
    /* Section headers with dark background */
    .section-header {
        background-color: #4a5568;
        color: white;
        padding: 6px 12px;
        font-weight: bold;
        text-align: center;
        border-bottom: 2px solid #000;
        margin: 0;
    }
    
    /* Compact form elements */
    .stCheckbox {
        margin-bottom: 0 !important;
        padding: 2px 0 !important;
    }
    
    .stRadio {
        margin-bottom: 0 !important;
        padding: 2px 0 !important;
    }
    
    .stTextInput > div {
        margin-bottom: 0 !important;
    }
    
    .stNumberInput > div {
        margin-bottom: 0 !important;
    }
    
    .stSelectbox > div {
        margin-bottom: 0 !important;
    }
    
    .stTextArea > div {
        margin-bottom: 0 !important;
    }
    
    /* Reduce padding in sections */
    .header-section .stColumns,
    .sedation-section .stColumns,
    .vitals-section .stColumns,
    .equipment-section .stColumns,
    .medical-review-section .stColumns,
    .special-section .stColumns {
        gap: 0 !important;
    }
    .stSelectbox > div > div { padding: 0px; }
    .row-widget { margin: 0px; padding: 0px; }
    
    /* Improve spacing within sections */
    .header-section .stRadio,
    .sedation-section .stRadio,
    .medical-review-section .stRadio,
    .special-section .stRadio { margin-bottom: 10px; }
    
    .header-section .stCheckbox,
    .sedation-section .stCheckbox,
    .special-section .stCheckbox { margin-bottom: 5px; }
    
    /* Section headers */
    .vitals-section h3,
    .equipment-section h3,
    .medical-review-section h3,
    .special-section h3 { 
        margin-top: 0; 
        margin-bottom: 15px; 
        font-size: 1.4em;
        font-weight: 600;
    }
    
    /* Typography improvements */
    .stMarkdown p {
        font-size: 1.1em;
        line-height: 1.5;
    }
    
    .stMarkdown p strong {
        font-size: 1.15em;
    }
    
    /* Main title */
    h1 {
        font-size: 2.2em !important;
        margin-bottom: 20px !important;
    }
    
    /* Section titles */
    h2 {
        font-size: 1.8em !important;
        margin-bottom: 15px !important;
    }
    
    /* Subsection titles */
    h3 {
        font-size: 1.5em !important;
        margin-bottom: 12px !important;
    }
    
    /* Input labels */
    .stTextInput label, .stNumberInput label, .stSelectbox label, 
    .stDateInput label, .stTextArea label {
        font-size: 1.1em !important;
        font-weight: 500;
    }
    
    /* Radio and checkbox labels */
    .stRadio > div > label > div > p,
    .stCheckbox > label > span {
        font-size: 1.1em !important;
    }
    
    /* Add visual separation between major sections */
    .header-section,
    .sedation-section,
    .vitals-section,
    .equipment-section,
    .medical-review-section,
    .special-section {
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 3px;
    }
    
    /* Internal row borders for better grouping */
    .medical-review-section .stColumns > div {
        border-bottom: 1px solid rgba(0,0,0,0.1);
        padding-bottom: 10px;
        margin-bottom: 10px;
    }
    
    .medical-review-section .stColumns:last-child > div {
        border-bottom: none;
    }
    
    /* Group related fields visually */
    .field-group {
        background-color: rgba(255,255,255,0.5);
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 10px;
    }
    
    /* Print-friendly styles */
    @media print {
        .stApp {
            background-color: white !important;
        }
        
        /* Keep colors in print */
        .header-section { 
            background-color: #ebf8ff !important;
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
        .sedation-section { background-color: #f0f9ff !important; }
        .vitals-section { background-color: #f0fdf4 !important; }
        .equipment-section { background-color: #fefcf3 !important; }
        .medical-review-section { background-color: #faf5ff !important; }
        .special-section { background-color: #fef2f2 !important; }
        
        /* Hide Streamlit UI elements */
        header, .stDeployButton, section[data-testid="stSidebar"], 
        div[data-testid="stDecoration"], iframe {
            display: none !important;
        }
        
        /* Compact spacing for print */
        .block-container {
            padding: 0 !important;
            max-width: 100% !important;
        }
        
        /* Ensure borders print */
        * {
            -webkit-print-color-adjust: exact;
            print-color-adjust: exact;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Header Section - Light Blue
    st.markdown('<div class="header-section">', unsafe_allow_html=True)
    
    # First row with borders between cells
    st.markdown('<div class="form-row" style="display: flex; align-items: stretch;">', unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        st.date_input("**Date**", key="procedure_date", label_visibility="visible")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        st.text_input("**Patient Name**", 
                     value=f"{st.session_state.get('patient_first_name', '')} {st.session_state.get('patient_last_name', '')}", 
                     key="patient_full_name")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="form-cell" style="border-right: none;">', unsafe_allow_html=True)
        dob = st.session_state.get('patient_dob', patient['date_of_birth'][:10] if patient else "1980-01-01")
        if isinstance(dob, str):
            st.text_input("**DOB**", value=dob, key="dob_display")
        else:
            st.text_input("**DOB**", value=dob.strftime("%Y-%m-%d"), key="dob_display")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Timeout verification row
    st.markdown('<div class="form-row" style="display: flex; align-items: stretch;">', unsafe_allow_html=True)
    timeout_cols = st.columns([5, 2, 2])
    
    with timeout_cols[0]:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        st.checkbox("Time-out w/ verification of correct Pt ID (full name/DOB) and correct procedure completed by surgical team", 
                    key="timeout_verification")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with timeout_cols[1]:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        providers = api_get("/providers/") or []
        surgeon_names = [""] + [p["name"] for p in providers]
        st.selectbox("**Surgeon Name**", surgeon_names, key="surgeon_name")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with timeout_cols[2]:
        st.markdown('<div class="form-cell" style="border-right: none;">', unsafe_allow_html=True)
        st.checkbox("Sedation administered by Surgeon", key="sedation_by_surgeon")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close header section
    
    # Level of Sedation Section - Light Blue
    st.markdown('<div class="sedation-section">', unsafe_allow_html=True)
    
    # First row - Level of Sedation
    st.markdown('<div class="form-row" style="display: flex; padding: 0;">', unsafe_allow_html=True)
    st.markdown('<div class="form-cell" style="width: 100%; border-right: none; padding: 10px;">', unsafe_allow_html=True)
    
    st.write("**Level of Sedation:**")
    sed_cols = st.columns(4)
    with sed_cols[0]:
        st.checkbox("Nitrous Oxide", key="sedation_nitrous")
    with sed_cols[1]:
        st.checkbox("Level 1: Minimal Sedation", key="sedation_minimal")
    with sed_cols[2]:
        st.checkbox("Level 2: Moderate Enteral", key="sedation_moderate_enteral")
    with sed_cols[3]:
        st.checkbox("Level 3: Moderate Parenteral", key="sedation_moderate_parenteral")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Second row - Written & Verbal Instructions
    st.markdown('<div class="form-row" style="display: flex; padding: 0; border-bottom: none;">', unsafe_allow_html=True)
    st.markdown('<div class="form-cell" style="width: 100%; border-right: none; padding: 10px;">', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 2])
    with col1:
        st.write("**In Advance of Surgery, the Patient was given Written & Verbal**")
    with col2:
        inst_cols = st.columns(2)
        with inst_cols[0]:
            st.checkbox("Pre-Op Instructions", key="written_preop_instructions")
        with inst_cols[1]:
            st.checkbox("Post-Op Instructions", key="written_postop_instructions")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)  # Close sedation section
    
    # Pre-Operative Vitals Section - Light Green
    st.markdown('<div class="vitals-section">', unsafe_allow_html=True)
    
    # Section header with dark background
    st.markdown('<div class="section-header">Pre-Operative Vitals (day of procedure)</div>', unsafe_allow_html=True)
    
    # Create table-like structure for vitals with labels row
    st.markdown('<div class="form-row" style="display: flex; padding: 0; border-bottom: 2px solid #000;">', unsafe_allow_html=True)
    label_cols = st.columns([1.5, 1.5, 1.2, 0.8, 0.8, 1.2, 0.8, 1.2])
    
    with label_cols[0]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; font-weight: bold;">Height</div>', unsafe_allow_html=True)
    with label_cols[1]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; font-weight: bold;">Weight</div>', unsafe_allow_html=True)
    with label_cols[2]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; font-weight: bold;">Blood Pressure</div>', unsafe_allow_html=True)
    with label_cols[3]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; font-weight: bold;">Pulse</div>', unsafe_allow_html=True)
    with label_cols[4]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; font-weight: bold;">SpO₂</div>', unsafe_allow_html=True)
    with label_cols[5]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; font-weight: bold;">RR (ECG)</div>', unsafe_allow_html=True)
    with label_cols[6]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; font-weight: bold;">NA</div>', unsafe_allow_html=True)
    with label_cols[7]:
        st.markdown('<div style="padding: 5px; font-weight: bold;">FSBG</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Input fields row
    st.markdown('<div class="form-row" style="display: flex; padding: 0; border-bottom: none;">', unsafe_allow_html=True)
    vitals_cols = st.columns([1.5, 1.5, 1.2, 0.8, 0.8, 1.2, 0.8, 1.2])
    
    with vitals_cols[0]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; min-height: 80px;">', unsafe_allow_html=True)
        if st.session_state.get('height_unit', 'Ft/In') == "Ft/In":
            h_cols = st.columns(2)
            with h_cols[0]:
                feet = st.number_input("ft", min_value=0, max_value=8, key="height_feet", label_visibility="visible")
            with h_cols[1]:
                inches = st.number_input("in", min_value=0, max_value=11, key="height_inches", label_visibility="visible")
            height = feet * 12 + inches
        else:
            height = st.number_input("cm", min_value=0, key="height_cm", label_visibility="visible")
        height_unit = st.radio("", ["Ft/In", "Cm"], horizontal=True, key="height_unit", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
        
    with vitals_cols[1]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; min-height: 80px;">', unsafe_allow_html=True)
        weight = st.number_input("", min_value=0.0, key="weight_preop", label_visibility="collapsed")
        weight_unit = st.radio("", ["lbs", "Kg"], horizontal=True, key="weight_unit", label_visibility="collapsed")
        # Calculate BMI
        if height > 0 and weight > 0:
            if height_unit == "Ft/In" and weight_unit == "lbs":
                bmi = (weight / (height ** 2)) * 703
            elif height_unit == "Cm" and weight_unit == "Kg":
                bmi = weight / ((height/100) ** 2)
            else:
                # Convert if mixed units
                if height_unit == "Ft/In" and weight_unit == "Kg":
                    bmi = weight / ((height * 2.54 / 100) ** 2)
                else:  # height_unit == "Cm" and weight_unit == "lbs"
                    bmi = (weight * 0.453592) / ((height/100) ** 2)
            
            # Determine BMI category and color
            if bmi < 18.5:
                category = "Underweight"
                color = "#FFA500"  # Orange
            elif 18.5 <= bmi <= 24.9:
                category = "Normal weight"
                color = "#00AA00"  # Green
            elif 25.0 <= bmi <= 29.9:
                category = "Overweight"
                color = "#00AA00"  # Green (per your request for 0-29.9)
            elif 30.0 <= bmi <= 34.9:
                category = "Obesity Class I (Moderate)"
                color = "#FFAA00"  # Yellow/Orange
            elif 35.0 <= bmi <= 39.9:
                category = "Obesity Class II (Severe)"
                color = "#FF0000"  # Red
            else:  # bmi >= 40.0
                category = "Obesity Class III (Very severe / morbid obesity)"
                color = "#FF0000"  # Red
            
            st.markdown(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-top: 10px;'>"
                       f"<p style='color: {color}; font-weight: bold; margin: 0;'>BMI: {bmi:.1f}</p>"
                       f"<p style='color: {color}; margin: 0; font-size: 0.9em;'>{category}</p>"
                       f"</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-top: 10px;'>"
                       "<p style='color: gray; margin: 0;'>BMI: --</p>"
                       "</div>", unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with vitals_cols[2]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; min-height: 80px;">', unsafe_allow_html=True)
        st.text_input("", key="bp_preop", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with vitals_cols[3]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; min-height: 80px;">', unsafe_allow_html=True)
        st.number_input("", min_value=0, max_value=300, key="pulse_preop", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with vitals_cols[4]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; min-height: 80px;">', unsafe_allow_html=True)
        st.number_input("", min_value=0, max_value=100, key="spo2_preop", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with vitals_cols[5]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; min-height: 80px;">', unsafe_allow_html=True)
        st.text_input("", key="rr_ecg", label_visibility="collapsed")
        st.checkbox("Defer", key="rr_defer")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with vitals_cols[6]:
        st.markdown('<div style="border-right: 2px solid #000; padding: 5px; min-height: 80px;">', unsafe_allow_html=True)
        st.checkbox("NA", key="vitals_na")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with vitals_cols[7]:
        st.markdown('<div style="padding: 5px; min-height: 80px;">', unsafe_allow_html=True)
        st.number_input("mg/dl", min_value=0, key="fsbg", label_visibility="visible")
        st.text_input("Time (24hr)", key="fsbg_time", label_visibility="visible")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close vitals container
    st.markdown('</div>', unsafe_allow_html=True)  # Close vitals section
    
    # Pre-Procedure Equipment Readiness Check - Light Yellow
    st.markdown('<div class="equipment-section">', unsafe_allow_html=True)
    st.markdown("### Pre-Procedure Equipment Readiness Check")
    
    eq_cols = st.columns([1.5, 2, 2.5])
    with eq_cols[0]:
        st.date_input("**Date**", key="equipment_check_date")
    with eq_cols[1]:
        st.text_input("**Completed By:**", key="equipment_completed_by")
    with eq_cols[2]:
        st.text_area("**Notes:**", height=80, key="equipment_notes")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Pre-Procedure Medical Review - Light Purple
    st.markdown('<div class="medical-review-section">', unsafe_allow_html=True)
    
    # Section header
    st.markdown('<div class="section-header">Pre-Procedure Medical Review (to be completed by the Surgeon ONLY)</div>', unsafe_allow_html=True)
    
    # Medical history row with table structure
    st.markdown('<div class="form-row" style="display: flex; padding: 0;">', unsafe_allow_html=True)
    review_cols = st.columns([3, 0.8, 3.2])
    with review_cols[0]:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        st.write("**Review of Patient's Medical History**")
        st.markdown('</div>', unsafe_allow_html=True)
    with review_cols[1]:
        st.markdown('<div class="form-cell" style="justify-content: center;">', unsafe_allow_html=True)
        st.radio("Select", ["Y", "N"], key="medical_history_radio", label_visibility="collapsed", horizontal=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with review_cols[2]:
        st.markdown('<div class="form-cell" style="border-right: none;">', unsafe_allow_html=True)
        st.text_input("Notes: See Surgical Health History Form for Patient's Medical History", 
                     key="medical_history_notes", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Allergies row
    st.markdown('<div class="form-row" style="display: flex; padding: 0;">', unsafe_allow_html=True)
    allergy_cols = st.columns([3, 0.8, 3.2])
    with allergy_cols[0]:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        st.write("**Review of Patient's Allergies**")
        st.markdown('</div>', unsafe_allow_html=True)
    with allergy_cols[1]:
        st.markdown('<div class="form-cell" style="justify-content: center;">', unsafe_allow_html=True)
        st.radio("Select", ["Y", "N"], key="allergies_radio", label_visibility="collapsed", horizontal=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with allergy_cols[2]:
        st.markdown('<div class="form-cell" style="border-right: none;">', unsafe_allow_html=True)
        st.text_input("Notes: See Surgical Health History Form for List of Patient's Allergies", 
                     key="allergies_notes", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Surgical history row
    st.markdown('<div class="form-row" style="display: flex; padding: 0;">', unsafe_allow_html=True)
    surg_cols = st.columns([3, 0.8, 3.2])
    with surg_cols[0]:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        st.write("**Review of Patient's Surgical/Anesthesia History**")
        st.markdown('</div>', unsafe_allow_html=True)
    with surg_cols[1]:
        st.markdown('<div class="form-cell" style="justify-content: center;">', unsafe_allow_html=True)
        st.radio("Select", ["Y", "N"], key="surg_history_radio", label_visibility="collapsed", horizontal=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with surg_cols[2]:
        st.markdown('<div class="form-cell" style="border-right: none;">', unsafe_allow_html=True)
        st.text_area("Notes:", height=60, key="surg_history_notes", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Family history row
    st.markdown('<div class="form-row" style="display: flex; padding: 0;">', unsafe_allow_html=True)
    family_cols = st.columns([3, 0.8, 3.2])
    with family_cols[0]:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        st.write("**Review of Patient's Family Surgical/Anesthesia Complication History**")
        st.markdown('</div>', unsafe_allow_html=True)
    with family_cols[1]:
        st.markdown('<div class="form-cell" style="justify-content: center;">', unsafe_allow_html=True)
        st.radio("Select", ["Y", "N"], key="family_history_radio", label_visibility="collapsed", horizontal=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with family_cols[2]:
        st.markdown('<div class="form-cell" style="border-right: none;">', unsafe_allow_html=True)
        st.text_area("Notes:", height=60, key="family_history_notes", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Medications row
    med_cols = st.columns([3, 0.6, 2.4])
    with med_cols[0]:
        st.write("**Review of Patient's Medication(s)**")
    with med_cols[1]:
        st.radio("Select", ["Y", "N"], key="medications_radio", label_visibility="collapsed", horizontal=True)
    with med_cols[2]:
        st.checkbox("See Surgical Health History Form for List of Medications", key="see_med_form")
        st.write("Pre-Op & Post Op Medication Modification Instructions Given Prior to Procedure:")
        mod_cols = st.columns(4)
        with mod_cols[0]:
            st.checkbox("Diabetic Medication", key="mod_diabetic")
        with mod_cols[1]:
            st.checkbox("Anticoagulant", key="mod_anticoagulant")
        with mod_cols[2]:
            st.checkbox("Immunosuppressive", key="mod_immunosuppressive")
        with mod_cols[3]:
            st.checkbox("Bisphosphonates", key="mod_bisphosphonates")
        st.text_input("Other/Notes:", key="med_other_notes")
    
    # Modifications needed row
    st.markdown('<div class="form-row" style="display: flex; padding: 0;">', unsafe_allow_html=True)
    mod_cols = st.columns([3, 0.8, 3.2])
    with mod_cols[0]:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        st.write("**Any Modification(s) as needed?**")
        st.markdown('</div>', unsafe_allow_html=True)
    with mod_cols[1]:
        st.markdown('<div class="form-cell" style="justify-content: center;">', unsafe_allow_html=True)
        st.radio("", ["Y", "N"], key="modifications_radio", label_visibility="collapsed", horizontal=True, index=1)
        st.markdown('</div>', unsafe_allow_html=True)
    with mod_cols[2]:
        st.markdown('<div class="form-cell" style="border-right: none;">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Medical consult row
    st.markdown('<div class="form-row" style="display: flex; padding: 0; border-bottom: none;">', unsafe_allow_html=True)
    consult_cols = st.columns([3, 1, 3])
    with consult_cols[0]:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        st.write("**Review of Medical Consult (If Necessary)**")
        st.markdown('</div>', unsafe_allow_html=True)
    with consult_cols[1]:
        st.markdown('<div class="form-cell" style="justify-content: center;">', unsafe_allow_html=True)
        st.radio("", ["Y", "N", "NA"], key="consult_radio", label_visibility="collapsed", horizontal=True, index=2)
        st.markdown('</div>', unsafe_allow_html=True)
    with consult_cols[2]:
        st.markdown('<div class="form-cell" style="border-right: none;">', unsafe_allow_html=True)
        st.text_area("Notes:", height=40, key="consult_notes", label_visibility="collapsed")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)  # Close medical review section
    
    # Special Pre-Operative Considerations - Light Red/Pink
    st.markdown('<div class="special-section">', unsafe_allow_html=True)
    
    # Section header
    st.markdown('<div class="section-header">Special Pre-Operative Consideration as indicated for sedation/anesthesia for the following</div>', unsafe_allow_html=True)
    
    # First row - Pediatric and High Risk
    st.markdown('<div class="form-row" style="display: flex; padding: 0;">', unsafe_allow_html=True)
    spec_cols = st.columns([2, 0.8, 1.4, 2, 0.8])
    with spec_cols[0]:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        st.write("**Pediatric Patient**")
        st.markdown('</div>', unsafe_allow_html=True)
    with spec_cols[1]:
        st.markdown('<div class="form-cell" style="justify-content: center;">', unsafe_allow_html=True)
        st.radio("", ["Y", "N"], key="pediatric_radio", label_visibility="collapsed", horizontal=True, index=1)
        st.markdown('</div>', unsafe_allow_html=True)
    with spec_cols[2]:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    with spec_cols[3]:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        st.write("**High Risk Patient**")
        st.markdown('</div>', unsafe_allow_html=True)
    with spec_cols[4]:
        st.markdown('<div class="form-cell" style="border-right: none; justify-content: center;">', unsafe_allow_html=True)
        st.radio("", ["Y", "N"], key="high_risk_radio", label_visibility="collapsed", horizontal=True, index=1)
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ASA Status row
    st.markdown('<div class="form-row" style="display: flex; padding: 0;">', unsafe_allow_html=True)
    asa_cols = st.columns([2, 4])
    with asa_cols[0]:
        st.markdown('<div class="form-cell">', unsafe_allow_html=True)
        st.write("**ASA Status**")
        st.markdown('</div>', unsafe_allow_html=True)
    with asa_cols[1]:
        st.markdown('<div class="form-cell" style="border-right: none;">', unsafe_allow_html=True)
        asa_check_cols = st.columns(3)
        with asa_check_cols[0]:
            st.checkbox("1", key="asa_1")
        with asa_check_cols[1]:
            st.checkbox("2", key="asa_2")
        with asa_check_cols[2]:
            st.checkbox("3", key="asa_3")
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Airway Exam row
    airway_cols = st.columns([2, 3])
    with airway_cols[0]:
        st.write("**Airway Exam: Mallampatti Score**")
    with airway_cols[1]:
        mall_cols = st.columns(4)
        with mall_cols[0]:
            st.checkbox("I", key="mallampatti_i", value=True)
        with mall_cols[1]:
            st.checkbox("II", key="mallampatti_ii")
        with mall_cols[2]:
            st.checkbox("III", key="mallampatti_iii")
        with mall_cols[3]:
            st.checkbox("IV", key="mallampatti_iv")
    
    # Lungs Ausculated row
    lungs_cols = st.columns([2, 0.8, 3.2])
    with lungs_cols[0]:
        st.write("**Lungs Ausculated**")
    with lungs_cols[1]:
        lungs_yn = st.radio("Select", ["Y", "N"], key="lungs_radio", label_visibility="collapsed", horizontal=True, index=0)
    with lungs_cols[2]:
        ctab_col, other_col = st.columns([0.8, 3.2])
        with ctab_col:
            st.checkbox("CTAB", key="lungs_ctab")
        with other_col:
            st.text_input("Other:", key="lungs_other")
    
    # Heart Ausculated row
    heart_cols = st.columns([2, 0.8, 3.2])
    with heart_cols[0]:
        st.write("**Heart Ausculated**")
    with heart_cols[1]:
        heart_yn = st.radio("Select", ["Y", "N"], key="heart_radio", label_visibility="collapsed", horizontal=True, index=0)
    with heart_cols[2]:
        rrr_col, other_col = st.columns([0.8, 3.2])
        with rrr_col:
            st.checkbox("RRR", key="heart_rrr")
        with other_col:
            st.text_input("Other:", key="heart_other")
    
    # NPO Status row
    npo_cols = st.columns([2, 0.8, 3.2])
    with npo_cols[0]:
        st.write("**NPO Status Verified**")
    with npo_cols[1]:
        npo_yn = st.radio("Select", ["Y", "N"], key="npo_radio", label_visibility="collapsed", horizontal=True, index=0)
    with npo_cols[2]:
        npo_time_cols = st.columns([1, 1, 2])
        with npo_time_cols[0]:
            st.checkbox("NPO: ≥8", key="npo_8")
        with npo_time_cols[1]:
            st.checkbox("NPO: ≥6", key="npo_6")
        with npo_time_cols[2]:
            st.text_input("Notes:", key="npo_notes")
    
    # Notes/Reason for omission
    st.text_area("**Notes/Reason for omission of any items**", height=60, key="omission_notes")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Check vital signs and save
    def check_vital_signs():
        warnings = []
        
        pulse = st.session_state.get('pulse_preop', 0)
        if pulse > 0 and (pulse < 60 or pulse > 120):
            warnings.append("Pulse Rate")
        
        bp = st.session_state.get('bp_preop', '')
        if bp and '/' in bp:
            try:
                sys, dia = map(int, bp.split('/'))
                if sys < 90 or sys > 140 or dia < 60 or dia > 99:
                    warnings.append("Blood Pressure")
            except:
                pass
        
        spo2 = st.session_state.get('spo2_preop', 0)
        if spo2 > 0 and (spo2 < 95 or spo2 > 100):
            warnings.append("SpO2")
        
        return warnings
    
    # Save buttons
    st.write("")
    col1, col2, col3 = st.columns([3, 1, 1])
    with col2:
        if st.button("💾 Save", type="primary", key="save_preop"):
            warnings = check_vital_signs()
            if warnings:
                st.warning("⚠️ Vital signs are outside of normal levels, consider taking them again")
                st.write(f"Out of range: {', '.join(warnings)}")
            save_record()
            st.success("Saved!")
    with col3:
        if st.button("💾 Save and Close", type="secondary", key="save_close_preop"):
            warnings = check_vital_signs()
            if warnings:
                st.warning("⚠️ Vital signs are outside of normal levels, consider taking them again")
                st.write(f"Out of range: {', '.join(warnings)}")
            save_record()
            st.success("Saved and Closed!")

def render_preop_checklist_tab_old():
    patient = load_patient()
    
    # Blue header section
    with st.container():
        st.markdown('<div style="background-color: #b3d9e6; padding: 15px; border-radius: 5px;">', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([2, 3, 2])
        with col1:
            # Editable patient fields
            st.text_input("**First Name:**", value=patient['first_name'] if patient else "", key="patient_first_name")
            st.text_input("**Last Name:**", value=patient['last_name'] if patient else "", key="patient_last_name")
            dob = patient['date_of_birth'][:10] if patient else "1980-01-01"
            st.date_input("**DOB:**", value=datetime.strptime(dob, "%Y-%m-%d").date(), key="patient_dob")
            st.date_input("**Procedure Date:**", key="procedure_date", label_visibility="visible")
            
        with col2:
            col2a, col2b = st.columns(2)
            with col2a:
                st.write("**Sedation Services Delegated**")
                sedation_delegated = st.radio("", ["Yes", "No"], horizontal=True, key="sedation_delegated", label_visibility="collapsed")
            
            with col2b:
                providers = api_get("/providers/") or []
                surgeon_names = [""] + [p["name"] for p in providers]
                st.selectbox("**Surgeon:**", surgeon_names, key="surgeon_name")
            
            st.write("**Level of Sedation**")
            sedation_cols = st.columns(3)
            with sedation_cols[0]:
                st.checkbox("Nitrous/Minimal", key="sedation_nitrous")
            with sedation_cols[1]:
                st.checkbox("Moderate Enteral", key="sedation_moderate_enteral")
            with sedation_cols[2]:
                st.checkbox("Moderate Parenteral", key="sedation_moderate_parenteral")
                
        with col3:
            st.checkbox("**Procedure Timeout**", key="procedure_timeout")
            st.text_input("Start surgical timeout", key="timeout_start")
            st.text_input("End surgical timeout", key="timeout_end")
            
            if sedation_delegated == "Yes":
                st.text_input("Sedation Provider (only if delegated):", key="sedation_provider")
            
            st.text_area("Notes:", height=50, key="header_notes")
            
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Yellow PRE-PROCEDURE CHECKLIST section
    st.markdown('<div style="background-color: #f9f3c9; padding: 10px; border-radius: 5px; margin-top: 10px;">', unsafe_allow_html=True)
    st.subheader("PRE-PROCEDURE CHECKLIST")
    
    col1, col2 = st.columns(2)
    with col1:
        st.checkbox("Equipment readiness check", key="equipment_check")
        st.checkbox("Written and verbal preop and postop instructions", key="instructions_given")
    with col2:
        st.checkbox("Correct patient", key="correct_patient")
        st.checkbox("Correct procedure verified", key="correct_procedure")
    
    st.text_area("Notes:", height=60, key="checklist_notes")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Blue PRE-OP VITALS section
    st.markdown('<div style="background-color: #b3d9e6; padding: 10px; border-radius: 5px; margin-top: 10px;">', unsafe_allow_html=True)
    st.subheader("PRE-OP VITALS")
    
    vitals_cols = st.columns([1, 1, 1, 1, 1, 1, 1, 1])
    
    with vitals_cols[0]:
        st.write("**Height:**")
        if st.session_state.get('height_unit', 'Ft/In') == "Ft/In":
            h_cols = st.columns(2)
            with h_cols[0]:
                feet = st.number_input("ft", min_value=0, max_value=8, key="height_feet", label_visibility="collapsed")
            with h_cols[1]:
                inches = st.number_input("in", min_value=0, max_value=11, key="height_inches", label_visibility="collapsed")
            height = feet * 12 + inches
        else:
            height = st.number_input("cm", min_value=0, key="height_cm", label_visibility="collapsed")
        height_unit = st.radio("", ["Ft/In", "Cm"], horizontal=True, key="height_unit", label_visibility="collapsed")
        
    with vitals_cols[1]:
        weight = st.number_input("Weight:", min_value=0.0, key="weight_preop")
        weight_unit = st.radio("", ["lbs", "Kg"], horizontal=True, key="weight_unit", label_visibility="collapsed")
        # Calculate BMI
        if height > 0 and weight > 0:
            if height_unit == "Ft/In" and weight_unit == "lbs":
                bmi = (weight / (height ** 2)) * 703
            elif height_unit == "Cm" and weight_unit == "Kg":
                bmi = weight / ((height/100) ** 2)
            else:
                # Convert if mixed units
                if height_unit == "Ft/In" and weight_unit == "Kg":
                    bmi = weight / ((height * 2.54 / 100) ** 2)
                else:  # height_unit == "Cm" and weight_unit == "lbs"
                    bmi = (weight * 0.453592) / ((height/100) ** 2)
            
            # Determine BMI category and color
            if bmi < 18.5:
                category = "Underweight"
                color = "#FFA500"  # Orange
            elif 18.5 <= bmi <= 24.9:
                category = "Normal weight"
                color = "#00AA00"  # Green
            elif 25.0 <= bmi <= 29.9:
                category = "Overweight"
                color = "#00AA00"  # Green (per your request for 0-29.9)
            elif 30.0 <= bmi <= 34.9:
                category = "Obesity Class I (Moderate)"
                color = "#FFAA00"  # Yellow/Orange
            elif 35.0 <= bmi <= 39.9:
                category = "Obesity Class II (Severe)"
                color = "#FF0000"  # Red
            else:  # bmi >= 40.0
                category = "Obesity Class III (Very severe / morbid obesity)"
                color = "#FF0000"  # Red
            
            st.markdown(f"<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-top: 10px;'>"
                       f"<p style='color: {color}; font-weight: bold; margin: 0;'>BMI: {bmi:.1f}</p>"
                       f"<p style='color: {color}; margin: 0; font-size: 0.9em;'>{category}</p>"
                       f"</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div style='background-color: #f0f0f0; padding: 10px; border-radius: 5px; margin-top: 10px;'>"
                       "<p style='color: gray; margin: 0;'>BMI: --</p>"
                       "</div>", unsafe_allow_html=True)
            
    with vitals_cols[2]:
        st.text_input("BP:", key="bp_preop")
        
    with vitals_cols[3]:
        st.number_input("Pulse Rate:", min_value=0, key="pulse_preop")
        
    with vitals_cols[4]:
        st.number_input("Respiration Rate:", min_value=0, key="resp_rate_preop")
        
    # Empty column where temp used to be
    with vitals_cols[5]:
        st.write("")  # Placeholder
        
    with vitals_cols[6]:
        st.number_input("O2 Saturation (SpO2):", min_value=0, max_value=100, key="spo2_preop")
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Purple PRE-PROCEDURE MEDICAL REVIEW section
    st.markdown('<div style="background-color: #c9d1e6; padding: 10px; border-radius: 5px; margin-top: 10px;">', unsafe_allow_html=True)
    st.subheader("PRE-PROCEDURE MEDICAL REVIEW:")
    
    # Medical review items in two columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.checkbox("Review of Patient's Medical History", key="review_medical_history")
        st.text_area("Notes:", height=60, key="medical_history_notes")
        
        st.checkbox("Review of Patient's Surgical/Anesthesia History", key="review_surgical_history")
        st.text_area("Notes:", height=60, key="surgical_history_notes")
        
        st.checkbox("Review of Patient's Medications and any modifications", key="review_medications")
        st.text_area("Notes:", height=60, key="medications_notes")
        
    with col2:
        st.checkbox("Smoker", key="is_smoker")
        
        st.checkbox("Review of Patient's Allergies", key="review_allergies")
        st.text_area("Notes:", height=60, key="allergies_notes")
        
        st.checkbox("Review of Patient's Family Surgical/Anesthesia History", key="review_family_history")
        st.text_area("Notes:", height=60, key="family_history_notes")
        
        st.checkbox("Review of Medical Consult (if needed)", key="review_consult")
        st.text_area("Notes:", height=60, key="consult_notes")
    
    # Physical examination section
    exam_cols = st.columns([2, 2, 2, 2])
    
    with exam_cols[0]:
        st.write("**Physical Examination: ASA Status**")
        asa_col = st.columns([1, 3])
        with asa_col[0]:
            asa_status = st.selectbox("ASA:", ["", "I", "II", "III", "IV", "V", "VI"], key="asa_status_preop", label_visibility="collapsed")
        
    with exam_cols[1]:
        st.write("**Physical Examination: NPO Status**")
        st.checkbox("", key="npo_status_checkbox")
        npo_col = st.columns([1, 3])
        with npo_col[0]:
            st.selectbox("NPO Time:", ["", "≥2h", "≥4h", "≥6h", "≥8h"], key="npo_time_preop", label_visibility="collapsed")
        
    with exam_cols[2]:
        st.write("**Anesthesia Exam: Airway Status**")
        mall_col = st.columns([1, 3])
        with mall_col[0]:
            st.selectbox("Mallampati:", ["", "I", "II", "III", "IV"], key="mallampati_preop", label_visibility="collapsed")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Check vital signs before saving
    def check_vital_signs():
        warnings = []
        
        # Check pulse rate (60-120)
        pulse = st.session_state.get('pulse_preop', 0)
        if pulse > 0 and (pulse < 60 or pulse > 120):
            warnings.append("Pulse Rate")
        
        # Check respiratory rate (12-20)
        resp = st.session_state.get('resp_rate_preop', 0)
        if resp > 0 and (resp < 12 or resp > 20):
            warnings.append("Respiratory Rate")
        
        # Check blood pressure (90-140/60-99)
        bp = st.session_state.get('bp_preop', '')
        if bp and '/' in bp:
            try:
                sys, dia = map(int, bp.split('/'))
                if sys < 90 or sys > 140 or dia < 60 or dia > 99:
                    warnings.append("Blood Pressure")
            except:
                pass
        
        # Check SpO2 (95-100)
        spo2 = st.session_state.get('spo2_preop', 0)
        if spo2 > 0 and (spo2 < 95 or spo2 > 100):
            warnings.append("SpO2")
        
        return warnings
    
    # Save buttons
    col1, col2, col3 = st.columns([2, 1, 1])
    with col2:
        if st.button("💾 Save", type="primary", key="save_preop"):
            warnings = check_vital_signs()
            if warnings:
                st.warning("⚠️ Vital signs are outside of normal levels, consider taking them again")
                st.write(f"Out of range: {', '.join(warnings)}")
            save_record()
            st.success("Saved!")
    with col3:
        if st.button("💾 Save and Close", type="secondary", key="save_close_preop"):
            warnings = check_vital_signs()
            if warnings:
                st.warning("⚠️ Vital signs are outside of normal levels, consider taking them again")
                st.write(f"Out of range: {', '.join(warnings)}")
            save_record()
            st.success("Saved and Closed!")

def render_anesthetic_record_tab():
    patient = load_patient()
    
    # Top section with patient info
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.write("**Patient**")
        # Editable patient fields that sync with preop
        if patient:
            # Sync with preop values
            first_name = st.session_state.get('patient_first_name', patient['first_name'])
            last_name = st.session_state.get('patient_last_name', patient['last_name'])
            st.text(f"{last_name}, {first_name}")
            dob_val = st.session_state.get('patient_dob', patient['date_of_birth'][:10])
            if isinstance(dob_val, str):
                st.text(dob_val)
            else:
                st.text(dob_val.strftime("%Y-%m-%d"))
        
        st.markdown(f"<h1 style='color: red;'>{st.session_state.patient_id}</h1>", unsafe_allow_html=True)
        
        st.write("**IV Anesthetics**")
        st.text_input("", value="", key="iv_anesthetics_time", label_visibility="collapsed")
        
        providers = api_get("/providers/") or []
        provider_names = [""] + [p["name"] for p in providers]
        
        st.selectbox("Anesthesia Provider", provider_names, key="anesthesia_provider")
        
        # Action buttons
        if st.button("🆕 New", key="new_record"):
            st.session_state.record_id = None
            st.rerun()
        
        if st.button("🗑️ Delete", key="delete_record"):
            if st.session_state.record_id:
                # Add delete functionality
                pass
    
    with col2:
        # Times section
        st.write("**Times**")
        times_cols = st.columns(4)
        
        with times_cols[0]:
            if st.button("Anesthesia Open", key="anes_open"):
                st.session_state.anesthesia_start = datetime.now()
        with times_cols[1]:
            if st.button("Surgery Open", key="surg_open"):
                st.session_state.surgery_start = datetime.now()
        with times_cols[2]:
            if st.button("Surgery Close", key="surg_close"):
                st.session_state.surgery_end = datetime.now()
        with times_cols[3]:
            if st.button("Anesthesia Close", key="anes_close"):
                st.session_state.anesthesia_end = datetime.now()
        
        # Provider dropdowns
        prov_cols = st.columns(4)
        with prov_cols[0]:
            st.selectbox("Surgeon", provider_names, key="surgeon_main")
        with prov_cols[1]:
            st.selectbox("Assistant", provider_names, key="assistant1_main")
        with prov_cols[2]:
            st.selectbox("Assistant", provider_names, key="assistant2_main")
        with prov_cols[3]:
            st.selectbox("Circulator", provider_names, key="circulator_main")
        
        # Main medication and vitals area
        main_cols = st.columns([2, 1])
        
        with main_cols[0]:
            # Anesthetic medications table
            st.write("**Anesthetic medication**")
            
            # Dose calculator buttons
            calc_cols = st.columns([2, 1])
            with calc_cols[0]:
                st.selectbox("", ["Versed 5 mg/mL", "Fentanyl 50 mcg/mL", "Zofran 4 mg/2mL", "Decadron 10 mg/mL"], 
                               key="selected_med", label_visibility="collapsed")
            with calc_cols[1]:
                st.text_input("Dose (ml)", key="dose_input", label_visibility="visible")
            
            # Number pad for manual push doses
            st.write("**Click to add dose (Manual IV Push)**")
            num_cols = st.columns(5)
            numbers = [
                ['7', '8', '9'],
                ['6', '5', '4'],
                ['3', '2', '1'],
                ['0', '.', 'Enter']
            ]
            
            for row in numbers:
                cols = st.columns(3)
                for i, num in enumerate(row):
                    if num:
                        with cols[i]:
                            st.button(num, key=f"num_{num}", use_container_width=True)
            
            st.write("**Quick dose buttons (mL)**")
            quick_cols = st.columns(4)
            with quick_cols[0]:
                st.button("0.5", key="quick_0.5", use_container_width=True)
            with quick_cols[1]:
                st.button("1.0", key="quick_1.0", use_container_width=True)
            with quick_cols[2]:
                st.button("2.0", key="quick_2.0", use_container_width=True)
            with quick_cols[3]:
                st.button("5.0", key="quick_5.0", use_container_width=True)
            
            # Medications table
            if st.session_state.record_id:
                medications = api_get("/medications/") or []
                
                # Only show the medications we use
                allowed_meds = ["Midazolam (Versed)", "Fentanyl", "Zofran", "Decadron"]
                med_data = []
                for med in medications:
                    if any(allowed in med["name"] for allowed in allowed_meds):
                        med_data.append({
                            "Medication": med["name"],
                            "Dose": 0,
                            "Waste": 0,
                            "TimeStamp": ""
                        })
                
                df = pd.DataFrame(med_data)
                st.dataframe(df, hide_index=True, use_container_width=True)
            
            # Vital signs section
            st.write("**Vital Signs**")
            st.button("Add VS manually", key="add_vs_manual")
            
            # Vital signs table placeholder
            vs_data = []
            df_vs = pd.DataFrame(columns=["Time Stamp", "BP", "MAP", "HR", "SpO2", "ETCO2", "Resp", "EKG"])
            st.dataframe(df_vs, hide_index=True, use_container_width=True)
            
        with main_cols[1]:
            # Right side panels
            st.write("**ASA Classification - Mallampati score - Sedation Administration Route**")
            
            asa_cols = st.columns(3)
            with asa_cols[0]:
                st.checkbox("IV Catheter", key="iv_catheter")
                st.checkbox("IV Butterfly", key="iv_butterfly")
            with asa_cols[1]:
                st.checkbox("PO", key="route_po")
                st.checkbox("Nasal", key="route_nasal")
            with asa_cols[2]:
                st.checkbox("IM", key="route_im")
                st.checkbox("Rectal", key="route_rectal")
            
            st.write("**O2 Delivery method**")
            o2_cols = st.columns(2)
            with o2_cols[0]:
                st.checkbox("Nasal cannula", key="o2_nasal")
                st.checkbox("Nasal hood", key="o2_hood")
            with o2_cols[1]:
                st.checkbox("Endotracheal tube", key="o2_ett")
                st.checkbox("Tracheostomy", key="o2_trach")
            
            # O2/N2O settings
            st.number_input("O2/N2O", min_value=0.0, max_value=10.0, value=0.0, step=1.0, key="o2_n2o_flow")
            st.slider("L/min", 0.0, 10.0, 0.0, step=1.0, key="flow_rate")
            
            # IV line status (single line for manual push)
            st.write("**IV Access**")
            st.checkbox("IV line active", key="iv_line_active")
            
            # IV Site and monitors
            st.selectbox("IV Site", ["", "Right hand", "Left hand", "Right arm", "Left arm"], key="iv_site")
            st.text_input("Attempts", key="iv_attempts")
            
            st.selectbox("Gauge", ["", "18G", "20G", "22G", "24G"], key="iv_gauge")
            
            st.write("**Monitors**")
            monitor_cols = st.columns(2)
            with monitor_cols[0]:
                st.checkbox("BP", key="monitor_bp")
                st.checkbox("SpO2", key="monitor_spo2")
                st.checkbox("EKG", key="monitor_ekg")
            with monitor_cols[1]:
                st.checkbox("EtCO2", key="monitor_etco2")
                st.checkbox("Precordial stethoscope", key="monitor_precordial")
            
            st.write(f"**Post anesthesia score: 0**")
            
            # Notes section
            st.text_area("Notes (record additional meds/routes/times here)", height=100, key="main_notes")
            
            # Height/Weight section
            hw_cols = st.columns(2)
            with hw_cols[0]:
                height = st.number_input("Height", min_value=0, key="height_main")
                height_unit_main = st.radio("Unit", ["in", "cm"], horizontal=True, key="height_unit_main", label_visibility="collapsed")
            with hw_cols[1]:
                weight = st.number_input("Weight", min_value=0.0, key="weight_main")
                weight_unit_main = st.radio("Unit", ["lbs", "kg"], horizontal=True, key="weight_unit_main", label_visibility="collapsed")
            
            st.text_input("NPO Since", key="npo_since_main")
            
            # Escort info
            st.text_input("Escort name", key="escort_name")
            st.selectbox("Escort Cell #", [""], key="escort_cell")
            st.selectbox("Relationship", ["", "Parent", "Spouse", "Friend", "Other"], key="escort_relationship")
            
            st.checkbox("Complications (see notes)", key="complications_checkbox")
            
            # Save buttons
            save_cols = st.columns(3)
            with save_cols[1]:
                if st.button("💾 Save", type="primary", key="save_main"):
                    save_record()
                    st.success("Saved!")
            with save_cols[2]:
                if st.button("Save and Close", key="save_close_main"):
                    save_record()
                    st.success("Saved and Closed!")
    
    # Bottom medication summary tables
    bottom_cols = st.columns(2)
    
    with bottom_cols[0]:
        st.write("**Anesthetic Medication Summary**")
        summary_data = {
            "Medication": ["Versed 5 mg/mL"],
            "Total Administered": [1],
            "Total Qty Wasted": [0]
        }
        df_summary = pd.DataFrame(summary_data)
        st.dataframe(df_summary, hide_index=True)
    
    with bottom_cols[1]:
        st.write("**IV Push Medications Log**")
        # Show a log of manual push medications
        push_data = {
            "Time": [],
            "Medication": [],
            "Dose (mL)": [],
            "Route": []
        }
        df_push = pd.DataFrame(push_data)
        st.dataframe(df_push, hide_index=True)
    
    # Inhalational agents table
    st.write("**Inhalational Agents**")
    inhal_data = {
        "Agent": [],
        "MAC": [],
        "L/Min": [],
        "TimeStamp": []
    }
    df_inhal = pd.DataFrame(inhal_data)
    st.dataframe(df_inhal, hide_index=True)

def render_post_anesthesia_score_tab():
    st.subheader("Post Anesthesia Score (Aldrete)")
    
    # Aldrete scoring with same layout as original
    score_items = [
        ("Activity", ["Unable to move", "Moves 2 extremities", "Moves 4 extremities"]),
        ("Respiration", ["Apneic", "Dyspnea/shallow", "Breathes deeply"]),
        ("Circulation", ["BP ±50% pre-op", "BP ±20-50% pre-op", "BP ±20% pre-op"]),
        ("Consciousness", ["Not responding", "Arousable", "Fully awake"]),
        ("Color", ["Cyanotic", "Pale/dusky", "Normal"])
    ]
    
    total_score = 0
    for item, options in score_items:
        score = st.radio(item, options=[0, 1, 2], 
                        format_func=lambda x: options[x], 
                        key=f"aldrete_{item.lower()}")
        total_score += score
    
    st.metric("Total Aldrete Score", f"{total_score}/10")
    
    # Discharge info
    col1, col2 = st.columns(2)
    with col1:
        st.time_input("Discharge Time", key="discharge_time")
        st.checkbox("Escort Present", key="escort_present")
    with col2:
        st.checkbox("Post-op Instructions Given", key="postop_given")
    
    if st.button("Save Post Anesthesia Score", type="primary"):
        save_record()
        st.success("Saved!")

def render_inventory_tab():
    st.subheader("Medication Inventory")
    
    # Location selector
    locations = api_get("/locations/") or []
    location_names = [loc["name"] for loc in locations] if locations else ["Default Location"]
    selected_location = st.selectbox("Location", location_names)
    
    # Add new medication
    with st.expander("Add New Medication to Inventory"):
        col1, col2 = st.columns(2)
        with col1:
            med_name = st.text_input("Medication Name")
            concentration = st.text_input("Concentration (e.g., 5mg/mL)")
            dea_schedule = st.selectbox("DEA Schedule", ["Non-controlled", "C-II", "C-III", "C-IV", "C-V"])
        with col2:
            quantity = st.number_input("Quantity", min_value=0)
            lot_number = st.text_input("Lot Number")
            exp_date = st.date_input("Expiration Date")
        
        if st.button("Add to Inventory"):
            st.success("Added to inventory!")
    
    # Display current inventory
    st.write("**Current Inventory**")
    inventory_data = {
        "Medication": ["Versed 5mg/mL", "Fentanyl 50mcg/mL", "Propofol 10mg/mL"],
        "DEA Schedule": ["C-IV", "C-II", "Non-controlled"],
        "Quantity": [25, 10, 50],
        "Lot #": ["A123", "B456", "C789"],
        "Expires": ["2024-12-31", "2024-11-30", "2025-01-31"]
    }
    df_inventory = pd.DataFrame(inventory_data)
    st.dataframe(df_inventory, hide_index=True)

# Auto-save function
def auto_save():
    if datetime.now() - st.session_state.last_save > timedelta(seconds=30):
        if save_record():
            st.session_state.last_save = datetime.now()

if __name__ == "__main__":
    main()
    auto_save()