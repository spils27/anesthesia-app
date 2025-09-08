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
    page_title="Anesthesia Record System",
    page_icon="💉",
    layout="wide"
)

# Initialize session state
if 'record_id' not in st.session_state:
    st.session_state.record_id = None
if 'patient_id' not in st.session_state:
    st.session_state.patient_id = st.query_params.get('patient_id', None)
if 'location_id' not in st.session_state:
    st.session_state.location_id = 1
if 'last_save' not in st.session_state:
    st.session_state.last_save = datetime.now()
if 'medications_given' not in st.session_state:
    st.session_state.medications_given = []
if 'vital_signs' not in st.session_state:
    st.session_state.vital_signs = []
if 'local_anesthetics' not in st.session_state:
    st.session_state.local_anesthetics = {
        "Articaine 4% 1:100k epi": 0,
        "Lidocaine 2% 1:100k epi": 0,
        "Mepivacaine 3% plain": 0,
        "Bupivacaine 0.5% 1:200k epi": 0
    }

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
        st.error(f"API Error: {str(e)}")
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
                "first_name": "John",
                "last_name": "Doe",
                "date_of_birth": "1990-01-01T00:00:00",
                "medical_record_number": "MRN123456"
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
        # Gather all form data
        update_data = {
            "asa_class": st.session_state.get("asa_class"),
            "asa_modifier_e": st.session_state.get("asa_modifier_e", False),
            "mallampati": st.session_state.get("mallampati"),
            "height_cm": st.session_state.get("height_cm"),
            "weight_kg": st.session_state.get("weight_kg"),
            "npo_since": st.session_state.get("npo_since").isoformat() if st.session_state.get("npo_since") else None,
            "anesthetist_id": st.session_state.get("anesthetist_id"),
            "surgeon_id": st.session_state.get("surgeon_id"),
            "assistant_id": st.session_state.get("assistant_id"),
            "circulator_id": st.session_state.get("circulator_id"),
            "o2_flow_rate": st.session_state.get("o2_flow_rate"),
            "n2o_flow_rate": st.session_state.get("n2o_flow_rate"),
            "iv_route": st.session_state.get("iv_route"),
            "iv_gauge": st.session_state.get("iv_gauge"),
            "iv_site": st.session_state.get("iv_site"),
            "iv_attempts": st.session_state.get("iv_attempts"),
            "monitors": st.session_state.get("monitors", []),
            "notes": st.session_state.get("notes"),
            "local_anesthetics": st.session_state.local_anesthetics
        }
        
        # Add timer values if they exist
        for timer in ["anesthesia_start", "anesthesia_end", "surgery_start", "surgery_end", 
                     "inhalation_start", "inhalation_end"]:
            if timer in st.session_state and st.session_state[timer]:
                update_data[timer] = st.session_state[timer].isoformat()
        
        # Calculate BMI if height and weight present
        if update_data["height_cm"] and update_data["weight_kg"]:
            height_m = update_data["height_cm"] / 100
            update_data["bmi"] = update_data["weight_kg"] / (height_m ** 2)
        
        result = api_put(f"/records/{st.session_state.record_id}", update_data)
        if result:
            st.session_state.last_save = datetime.now()
            return True
    return False

# Auto-save function
def auto_save():
    if datetime.now() - st.session_state.last_save > timedelta(seconds=30):
        if save_record():
            st.success("Auto-saved", icon="✅")

# Main app
def main():
    st.title("Anesthesia Record System")
    
    # Load or create record
    record = create_or_load_record()
    
    # Top bar with save button and patient info
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        patient = load_patient()
        if patient:
            st.write(f"**Patient:** {patient['first_name']} {patient['last_name']}")
            st.write(f"**DOB:** {patient['date_of_birth'][:10]}")
    
    with col2:
        st.write(f"**Location:** Default Location")
        st.write(f"**Last saved:** {st.session_state.last_save.strftime('%H:%M:%S')}")
    
    with col3:
        if st.button("💾 SAVE", type="primary", use_container_width=True):
            if save_record():
                st.success("Record saved!")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["Anesthetic Record", "Preop Checklist", "Post Anesthesia Score"])
    
    with tab1:
        render_anesthetic_record_tab()
    
    with tab2:
        render_preop_checklist_tab()
    
    with tab3:
        render_post_anesthesia_score_tab()
    
    # Auto-save every 30 seconds
    auto_save()

def render_anesthetic_record_tab():
    # Physical Assessment
    st.subheader("Physical Assessment")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        asa_options = ["I", "II", "III", "IV", "V", "VI"]
        st.selectbox("ASA Class", asa_options, key="asa_class")
        st.checkbox("E Modifier", key="asa_modifier_e")
    
    with col2:
        mallampati_options = ["I", "II", "III", "IV"]
        st.selectbox("Mallampati", mallampati_options, key="mallampati")
    
    with col3:
        st.number_input("Height (cm)", min_value=0.0, key="height_cm")
        st.number_input("Weight (kg)", min_value=0.0, key="weight_kg")
    
    with col4:
        if st.session_state.get("height_cm") and st.session_state.get("weight_kg"):
            height_m = st.session_state.height_cm / 100
            bmi = st.session_state.weight_kg / (height_m ** 2)
            st.metric("BMI", f"{bmi:.1f}")
        st.time_input("NPO Since", key="npo_since")
    
    # Providers
    st.subheader("Providers")
    providers = api_get("/providers/") or []
    provider_names = ["None"] + [p["name"] for p in providers]
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.selectbox("Anesthetist", provider_names, key="anesthetist_id")
    with col2:
        st.selectbox("Surgeon", provider_names, key="surgeon_id")
    with col3:
        st.selectbox("Assistant", provider_names, key="assistant_id")
    with col4:
        st.selectbox("Circulator", provider_names, key="circulator_id")
    
    # Inhalational Agents & IV Access
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Inhalational Agents")
        st.number_input("O2 Flow (L/min)", min_value=0.0, max_value=15.0, step=0.5, key="o2_flow_rate")
        st.number_input("N2O Flow (L/min)", min_value=0.0, max_value=10.0, step=0.5, key="n2o_flow_rate")
        
        col_start, col_end = st.columns(2)
        with col_start:
            if st.button("Inhalation Start"):
                st.session_state.inhalation_start = datetime.now()
                st.write(f"Started: {st.session_state.inhalation_start.strftime('%H:%M')}")
        with col_end:
            if st.button("Inhalation End"):
                st.session_state.inhalation_end = datetime.now()
                st.write(f"Ended: {st.session_state.inhalation_end.strftime('%H:%M')}")
    
    with col2:
        st.subheader("IV Access")
        st.selectbox("Route", ["Catheter", "Butterfly", "IM", "PO"], key="iv_route")
        st.selectbox("Gauge", ["18G", "20G", "22G", "24G"], key="iv_gauge")
        st.text_input("Site", key="iv_site")
        st.number_input("Attempts", min_value=1, max_value=10, key="iv_attempts")
    
    # Monitors
    st.subheader("Monitors")
    monitor_options = ["BP", "SpO2", "EKG", "EtCO2", "Temp", "Precordial"]
    st.multiselect("Select monitors in use", monitor_options, key="monitors")
    
    # Timer Buttons
    st.subheader("Procedure Times")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Anesthesia Open"):
            st.session_state.anesthesia_start = datetime.now()
            save_record()
    with col2:
        if st.button("Anesthesia Close"):
            st.session_state.anesthesia_end = datetime.now()
            save_record()
    with col3:
        if st.button("Surgery Open"):
            st.session_state.surgery_start = datetime.now()
            save_record()
    with col4:
        if st.button("Surgery Close"):
            st.session_state.surgery_end = datetime.now()
            save_record()
    
    # Display times
    times_col1, times_col2 = st.columns(2)
    with times_col1:
        if "anesthesia_start" in st.session_state:
            st.write(f"Anesthesia Start: {st.session_state.anesthesia_start.strftime('%H:%M')}")
        if "surgery_start" in st.session_state:
            st.write(f"Surgery Start: {st.session_state.surgery_start.strftime('%H:%M')}")
    with times_col2:
        if "anesthesia_end" in st.session_state:
            st.write(f"Anesthesia End: {st.session_state.anesthesia_end.strftime('%H:%M')}")
        if "surgery_end" in st.session_state:
            st.write(f"Surgery End: {st.session_state.surgery_end.strftime('%H:%M')}")
    
    # Medications
    render_medications_section()
    
    # Vital Signs
    render_vital_signs_section()
    
    # Local Anesthetics
    render_local_anesthetics_section()
    
    # Notes
    st.subheader("Notes")
    st.text_area("Additional notes", height=100, key="notes")

def render_medications_section():
    st.subheader("Medications")
    
    medications = api_get("/medications/") or []
    
    # Medication administration form
    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
    
    with col1:
        med_names = [m["name"] for m in medications]
        selected_med = st.selectbox("Medication", med_names, key="selected_medication")
    
    with col2:
        dose_ml = st.number_input("Dose (mL)", min_value=0.0, max_value=50.0, step=0.1, key="dose_ml")
    
    with col3:
        waste_ml = st.number_input("Waste (mL)", min_value=0.0, max_value=50.0, step=0.1, key="waste_ml")
    
    with col4:
        if st.button("Add", type="primary"):
            if selected_med and dose_ml > 0:
                # Find medication ID
                med_id = next((m["id"] for m in medications if m["name"] == selected_med), None)
                if med_id and st.session_state.record_id:
                    admin_data = {
                        "medication_id": med_id,
                        "dose_ml": dose_ml,
                        "waste_ml": waste_ml
                    }
                    result = api_post(f"/records/{st.session_state.record_id}/medications/", admin_data)
                    if result:
                        st.session_state.medications_given.append(result)
                        st.rerun()
    
    # Quick dose buttons
    st.write("Quick Dose:")
    cols = st.columns(12)
    for i in range(10):
        with cols[i]:
            if st.button(str(i), key=f"dose_btn_{i}"):
                st.rerun()
    
    with cols[10]:
        if st.button("25", key="dose_btn_25"):
            st.rerun()
    
    with cols[11]:
        if st.button("50", key="dose_btn_50"):
            st.rerun()
    
    # Display administered medications
    if st.session_state.record_id:
        record = api_get(f"/records/{st.session_state.record_id}")
        if record and record.get("medication_administrations"):
            df_data = []
            for admin in record["medication_administrations"]:
                # Get medication details
                med = next((m for m in medications if m["id"] == admin["medication_id"]), {})
                df_data.append({
                    "Time": datetime.fromisoformat(admin["timestamp"]).strftime("%H:%M"),
                    "Medication": med.get("name", "Unknown"),
                    "Dose (mL)": admin["dose_ml"],
                    "Waste (mL)": admin["waste_ml"],
                    "Total (mL)": admin["dose_ml"] + admin["waste_ml"]
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, hide_index=True)
                
                # Show totals
                st.write(f"**Total Used:** {df['Dose (mL)'].sum():.1f} mL")
                st.write(f"**Total Waste:** {df['Waste (mL)'].sum():.1f} mL")
                st.write(f"**Total Drawn:** {df['Total (mL)'].sum():.1f} mL")

def render_vital_signs_section():
    st.subheader("Vital Signs")
    
    with st.expander("Add Vital Signs"):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            bp_sys = st.number_input("BP Systolic", min_value=0, max_value=300, key="bp_sys")
            bp_dia = st.number_input("BP Diastolic", min_value=0, max_value=200, key="bp_dia")
        
        with col2:
            hr = st.number_input("Heart Rate", min_value=0, max_value=300, key="hr")
            spo2 = st.number_input("SpO2 (%)", min_value=0, max_value=100, key="spo2")
        
        with col3:
            etco2 = st.number_input("EtCO2", min_value=0, max_value=100, key="etco2")
            temp = st.number_input("Temp (°C)", min_value=30.0, max_value=42.0, step=0.1, key="temp")
        
        with col4:
            st.write("")  # Spacing
            st.write("")
            if st.button("Add VS", type="primary"):
                if st.session_state.record_id:
                    # Calculate MAP if BP values present
                    map_value = None
                    if bp_sys and bp_dia:
                        map_value = int((bp_sys + 2 * bp_dia) / 3)
                    
                    vital_data = {
                        "bp_systolic": bp_sys if bp_sys > 0 else None,
                        "bp_diastolic": bp_dia if bp_dia > 0 else None,
                        "map": map_value,
                        "heart_rate": hr if hr > 0 else None,
                        "spo2": spo2 if spo2 > 0 else None,
                        "etco2": etco2 if etco2 > 0 else None,
                        "temperature": temp if temp > 30 else None
                    }
                    
                    result = api_post(f"/records/{st.session_state.record_id}/vitals/", vital_data)
                    if result:
                        st.success("Vital signs added")
                        st.rerun()
    
    # Display vital signs
    if st.session_state.record_id:
        record = api_get(f"/records/{st.session_state.record_id}")
        if record and record.get("vital_signs"):
            df_data = []
            for vs in record["vital_signs"]:
                df_data.append({
                    "Time": datetime.fromisoformat(vs["timestamp"]).strftime("%H:%M"),
                    "BP": f"{vs['bp_systolic']}/{vs['bp_diastolic']}" if vs['bp_systolic'] else "",
                    "MAP": vs['map'] or "",
                    "HR": vs['heart_rate'] or "",
                    "SpO2": f"{vs['spo2']}%" if vs['spo2'] else "",
                    "EtCO2": vs['etco2'] or "",
                    "Temp": f"{vs['temperature']}°C" if vs['temperature'] else ""
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                st.dataframe(df, hide_index=True)

def render_local_anesthetics_section():
    st.subheader("Local Anesthetics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        for anes_type in ["Articaine 4% 1:100k epi", "Lidocaine 2% 1:100k epi"]:
            col_name, col_minus, col_count, col_plus = st.columns([3, 1, 1, 1])
            
            with col_name:
                st.write(anes_type)
            with col_minus:
                if st.button("-", key=f"minus_{anes_type}"):
                    if st.session_state.local_anesthetics[anes_type] > 0:
                        st.session_state.local_anesthetics[anes_type] -= 1
            with col_count:
                st.write(st.session_state.local_anesthetics[anes_type])
            with col_plus:
                if st.button("+", key=f"plus_{anes_type}"):
                    st.session_state.local_anesthetics[anes_type] += 1
    
    with col2:
        for anes_type in ["Mepivacaine 3% plain", "Bupivacaine 0.5% 1:200k epi"]:
            col_name, col_minus, col_count, col_plus = st.columns([3, 1, 1, 1])
            
            with col_name:
                st.write(anes_type)
            with col_minus:
                if st.button("-", key=f"minus_{anes_type}"):
                    if st.session_state.local_anesthetics[anes_type] > 0:
                        st.session_state.local_anesthetics[anes_type] -= 1
            with col_count:
                st.write(st.session_state.local_anesthetics[anes_type])
            with col_plus:
                if st.button("+", key=f"plus_{anes_type}"):
                    st.session_state.local_anesthetics[anes_type] += 1

def render_preop_checklist_tab():
    # Header with patient info in blue box style
    with st.container():
        st.markdown("""
        <style>
        .blue-header { background-color: #b3d9e6; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        .yellow-section { background-color: #f9f3c9; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        .purple-section { background-color: #c9d1e6; padding: 10px; border-radius: 5px; margin-bottom: 10px; }
        </style>
        """, unsafe_allow_html=True)
    
    # Patient info and timeout verification
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        patient = load_patient()
        if patient:
            st.write(f"**Patient Name:** {patient['first_name']} {patient['last_name']}")
        st.write(f"**Date:** {datetime.now().strftime('%Y-%m-%d')}")
    with col2:
        providers = api_get("/providers/") or []
        surgeon_names = [""] + [p["name"] for p in providers if p.get("role") == "Surgeon" or not p.get("role")]
        st.selectbox("Surgeon Name", surgeon_names, key="preop_surgeon")
    with col3:
        if patient:
            st.write(f"**DOB:** {patient['date_of_birth'][:10]}")
        st.checkbox("Sedation by Surgeon", key="sedation_by_surgeon")
    
    # Timeout verification
    st.checkbox("Time-out w/ verification of correct Pt ID (full name/DOB) and correct procedure completed by surgical team", 
                key="timeout_verification")
    
    # Level of Sedation
    st.subheader("Level of Sedation")
    sedation_levels = st.columns(4)
    with sedation_levels[0]:
        st.checkbox("Nitrous Oxide", key="sedation_nitrous")
    with sedation_levels[1]:
        st.checkbox("Level 1: Minimal Sedation", key="sedation_level1")
    with sedation_levels[2]:
        st.checkbox("Level 2: Moderate Enteral", key="sedation_level2")
    with sedation_levels[3]:
        st.checkbox("Level 3: Moderate Parenteral", key="sedation_level3")
    
    # Written & Verbal Instructions
    st.write("**In Advance of Surgery, the Patient was given Written & Verbal:**")
    inst_cols = st.columns(2)
    with inst_cols[0]:
        st.checkbox("Pre-Op Instructions", key="written_preop_instructions")
    with inst_cols[1]:
        st.checkbox("Post-Op Instructions", key="written_postop_instructions")
    
    # Pre-Operative Vitals
    st.subheader("Pre-Operative Vitals (day of procedure)")
    vitals_cols = st.columns(8)
    
    with vitals_cols[0]:
        height_ft = st.number_input("Height (ft)", min_value=0, max_value=10, key="preop_height_ft")
        height_in = st.number_input("Height (in)", min_value=0, max_value=11, key="preop_height_in")
    
    with vitals_cols[1]:
        weight_lbs = st.number_input("Weight (lbs)", min_value=0.0, key="preop_weight_lbs")
        weight_kg = st.number_input("Weight (kg)", min_value=0.0, value=weight_lbs*0.453592 if weight_lbs else 0.0, key="preop_weight_kg")
    
    with vitals_cols[2]:
        st.text_input("Blood Pressure", key="preop_bp")
    
    with vitals_cols[3]:
        st.number_input("Pulse", min_value=0, max_value=300, key="preop_pulse")
    
    with vitals_cols[4]:
        st.number_input("SpO₂", min_value=0, max_value=100, key="preop_spo2")
    
    with vitals_cols[5]:
        st.text_input("RR (ECG)", key="preop_rr")
        st.checkbox("Defer", key="preop_rr_defer")
    
    with vitals_cols[6]:
        st.number_input("Temp", min_value=90.0, max_value=110.0, key="preop_temp")
        st.checkbox("NA", key="preop_temp_na")
    
    with vitals_cols[7]:
        st.number_input("FSBG (mg/dl)", min_value=0, key="preop_fsbg")
        st.time_input("Time (24hr format)", key="preop_fsbg_time")
    
    # Equipment Readiness Check
    st.subheader("Pre-Procedure Equipment Readiness Check")
    eq_cols = st.columns([1, 2, 3])
    with eq_cols[0]:
        st.date_input("Date", key="equipment_check_date")
    with eq_cols[1]:
        st.text_input("Completed By:", key="equipment_completed_by")
    with eq_cols[2]:
        st.text_area("Notes:", height=60, key="equipment_notes")
    
    # Pre-Procedure Medical Review
    st.subheader("Pre-Procedure Medical Review (to be completed by the Surgeon ONLY)")
    
    # Medical History Review
    review_cols = st.columns([3, 1, 4])
    with review_cols[0]:
        st.write("**Review of Patient's Medical History**")
    with review_cols[1]:
        med_hist_cols = st.columns(2)
        with med_hist_cols[0]:
            st.checkbox("Y", key="medical_history_y")
        with med_hist_cols[1]:
            st.checkbox("N", key="medical_history_n")
    with review_cols[2]:
        st.text_input("Notes: See Surgical Health History Form for Patient's Medical History", key="medical_history_notes")
    
    # Allergies Review
    allergy_cols = st.columns([3, 1, 4])
    with allergy_cols[0]:
        st.write("**Review of Patient's Allergies**")
    with allergy_cols[1]:
        allergy_check_cols = st.columns(2)
        with allergy_check_cols[0]:
            st.checkbox("Y", key="allergies_y")
        with allergy_check_cols[1]:
            st.checkbox("N", key="allergies_n")
    with allergy_cols[2]:
        st.text_input("Notes: See Surgical Health History Form for List of Patient's Allergies", key="allergies_notes")
    
    # Surgical/Anesthesia History
    surg_hist_cols = st.columns([3, 1, 4])
    with surg_hist_cols[0]:
        st.write("**Review of Patient's Surgical/Anesthesia History**")
    with surg_hist_cols[1]:
        surg_hist_check_cols = st.columns(2)
        with surg_hist_check_cols[0]:
            st.checkbox("Y", key="surg_history_y")
        with surg_hist_check_cols[1]:
            st.checkbox("N", key="surg_history_n")
    with surg_hist_cols[2]:
        st.text_area("Notes:", height=60, key="surg_history_notes")
    
    # Family Complication History
    family_hist_cols = st.columns([3, 1, 4])
    with family_hist_cols[0]:
        st.write("**Review of Patient's Family Surgical/Anesthesia Complication History**")
    with family_hist_cols[1]:
        family_hist_check_cols = st.columns(2)
        with family_hist_check_cols[0]:
            st.checkbox("Y", key="family_history_y")
        with family_hist_check_cols[1]:
            st.checkbox("N", key="family_history_n")
    with family_hist_cols[2]:
        st.text_area("Notes:", height=60, key="family_history_notes")
    
    # Medications Review
    med_review_cols = st.columns([3, 1, 4])
    with med_review_cols[0]:
        st.write("**Review of Patient's Medication(s)**")
    with med_review_cols[1]:
        med_review_check_cols = st.columns(2)
        with med_review_check_cols[0]:
            st.checkbox("Y", key="medications_y")
        with med_review_check_cols[1]:
            st.checkbox("N", key="medications_n")
    with med_review_cols[2]:
        st.checkbox("See Surgical Health History Form for List of Medications", key="see_med_form")
        st.write("Pre-Op & Post Op Medication Modification Instructions Given Prior to Procedure:")
        med_mod_cols = st.columns(4)
        with med_mod_cols[0]:
            st.checkbox("Diabetic Medication", key="mod_diabetic")
        with med_mod_cols[1]:
            st.checkbox("Anticoagulant", key="mod_anticoagulant")
        with med_mod_cols[2]:
            st.checkbox("Immunosuppressive", key="mod_immunosuppressive")
        with med_mod_cols[3]:
            st.checkbox("Bisphosphonates", key="mod_bisphosphonates")
        st.text_input("Other/Notes:", key="med_other_notes")
    
    # Modifications needed
    mod_needed_cols = st.columns([3, 1, 4])
    with mod_needed_cols[0]:
        st.write("**Any Modification(s) as needed?**")
    with mod_needed_cols[1]:
        mod_needed_check_cols = st.columns(2)
        with mod_needed_check_cols[0]:
            st.checkbox("Y", key="modifications_y")
        with mod_needed_check_cols[1]:
            st.checkbox("N", key="modifications_n", value=True)
    
    # Medical Consult
    consult_cols = st.columns([3, 1, 4])
    with consult_cols[0]:
        st.write("**Review of Medical Consult (If Necessary)**")
    with consult_cols[1]:
        consult_check_cols = st.columns(3)
        with consult_check_cols[0]:
            st.checkbox("Y", key="consult_y")
        with consult_check_cols[1]:
            st.checkbox("N", key="consult_n")
        with consult_check_cols[2]:
            st.checkbox("NA", key="consult_na", value=True)
    with consult_cols[2]:
        st.text_area("Notes:", height=60, key="consult_notes")
    
    # Special Pre-Operative Considerations
    st.subheader("Special Pre-Operative Consideration as indicated for sedation/anesthesia for the following")
    
    special_cols = st.columns(2)
    with special_cols[0]:
        # Pediatric Patient
        ped_cols = st.columns([2, 1])
        with ped_cols[0]:
            st.write("**Pediatric Patient**")
        with ped_cols[1]:
            ped_check = st.columns(2)
            with ped_check[0]:
                st.checkbox("Y", key="pediatric_y")
            with ped_check[1]:
                st.checkbox("N", key="pediatric_n", value=True)
        
        # ASA Status
        st.write("**ASA Status**")
        asa_cols = st.columns(3)
        with asa_cols[0]:
            st.checkbox("1", key="asa_1")
        with asa_cols[1]:
            st.checkbox("2", key="asa_2")
        with asa_cols[2]:
            st.checkbox("3", key="asa_3")
        
        # Airway Exam
        st.write("**Airway Exam: Mallampatti Score**")
        mall_cols = st.columns(4)
        with mall_cols[0]:
            st.checkbox("I", key="mallampatti_i", value=True)
        with mall_cols[1]:
            st.checkbox("II", key="mallampatti_ii")
        with mall_cols[2]:
            st.checkbox("III", key="mallampatti_iii")
        with mall_cols[3]:
            st.checkbox("IV", key="mallampatti_iv")
    
    with special_cols[1]:
        # High Risk Patient
        hr_cols = st.columns([2, 1])
        with hr_cols[0]:
            st.write("**High Risk Patient**")
        with hr_cols[1]:
            hr_check = st.columns(2)
            with hr_check[0]:
                st.checkbox("Y", key="high_risk_y")
            with hr_check[1]:
                st.checkbox("N", key="high_risk_n", value=True)
        
        # Lungs Ausculated
        lungs_cols = st.columns([2, 1, 2])
        with lungs_cols[0]:
            st.write("**Lungs Ausculated**")
        with lungs_cols[1]:
            lungs_check = st.columns(2)
            with lungs_check[0]:
                st.checkbox("Y", key="lungs_y")
            with lungs_check[1]:
                st.checkbox("N", key="lungs_n")
        with lungs_cols[2]:
            st.checkbox("CTAB", key="lungs_ctab")
            st.text_input("Other:", key="lungs_other")
        
        # Heart Ausculated
        heart_cols = st.columns([2, 1, 2])
        with heart_cols[0]:
            st.write("**Heart Ausculated**")
        with heart_cols[1]:
            heart_check = st.columns(2)
            with heart_check[0]:
                st.checkbox("Y", key="heart_y")
            with heart_check[1]:
                st.checkbox("N", key="heart_n")
        with heart_cols[2]:
            st.checkbox("RRR", key="heart_rrr")
            st.text_input("Other:", key="heart_other")
        
        # NPO Status
        npo_cols = st.columns([2, 1, 3])
        with npo_cols[0]:
            st.write("**NPO Status Verified**")
        with npo_cols[1]:
            npo_check = st.columns(2)
            with npo_check[0]:
                st.checkbox("Y", key="npo_y")
            with npo_check[1]:
                st.checkbox("N", key="npo_n")
        with npo_cols[2]:
            npo_time_cols = st.columns(3)
            with npo_time_cols[0]:
                st.checkbox("NPO: ≥8", key="npo_8")
            with npo_time_cols[1]:
                st.checkbox("NPO: ≥6", key="npo_6")
            with npo_time_cols[2]:
                st.text_input("Notes:", key="npo_notes")
    
    # Notes/Reason for omission
    st.text_area("Notes/Reason for omission of any items", height=100, key="omission_notes")
    
    # Attestation
    st.write("---")
    st.write("**I hereby attest that the patient is cleared for surgery and the above pre-procedures, systems and items have been reviewed and completed.**")
    
    # Signature section
    sig_cols = st.columns(3)
    with sig_cols[0]:
        st.text_input("Surgeon Name:", key="surgeon_signature_name")
        st.checkbox("Melanny Valencia", key="surgeon_melanny")
        st.checkbox("Karina Mendieta", key="surgeon_karina")
    with sig_cols[1]:
        st.text_input("Signature:", key="surgeon_signature")
    with sig_cols[2]:
        st.date_input("Date:", key="surgeon_signature_date")
    
    asst_cols = st.columns(3)
    with asst_cols[0]:
        st.text_input("Assistant Name:", key="assistant_signature_name")
    with asst_cols[1]:
        st.text_input("Signature:", key="assistant_signature")
    with asst_cols[2]:
        st.date_input("Date:", key="assistant_signature_date")
    
    # Save button
    if st.button("Save Pre-Operative Checklist", type="primary"):
        # Gather all the preop data
        preop_data = {}
        
        # Collect all checkbox and input values
        for key in st.session_state:
            if key.startswith(("preop_", "sedation_", "medical_", "allergies_", "surg_", "family_", 
                            "medications_", "mod_", "consult_", "pediatric_", "asa_", "mallampatti_",
                            "high_risk_", "lungs_", "heart_", "npo_", "surgeon_", "assistant_",
                            "timeout_", "written_", "equipment_", "omission_")):
                preop_data[key] = st.session_state[key]
        
        # Store in the main record
        if st.session_state.record_id:
            # For now, store in notes field as JSON
            import json
            update_data = {
                "notes": json.dumps({"preop_checklist": preop_data}, indent=2)
            }
            result = api_put(f"/records/{st.session_state.record_id}", update_data)
            if result:
                st.success("Pre-Operative Checklist saved!")

def render_post_anesthesia_score_tab():
    st.subheader("Post Anesthesia Score (Aldrete)")
    
    # Aldrete scoring
    aldrete_scores = {}
    
    col1, col2 = st.columns(2)
    
    with col1:
        aldrete_scores["activity"] = st.radio(
            "Activity",
            options=[0, 1, 2],
            format_func=lambda x: {
                0: "0 - Unable to move",
                1: "1 - Moves 2 extremities",
                2: "2 - Moves 4 extremities"
            }[x],
            key="aldrete_activity"
        )
        
        aldrete_scores["respiration"] = st.radio(
            "Respiration",
            options=[0, 1, 2],
            format_func=lambda x: {
                0: "0 - Apneic",
                1: "1 - Dyspnea/shallow",
                2: "2 - Breathes deeply"
            }[x],
            key="aldrete_respiration"
        )
        
        aldrete_scores["circulation"] = st.radio(
            "Circulation",
            options=[0, 1, 2],
            format_func=lambda x: {
                0: "0 - BP ±50% pre-op",
                1: "1 - BP ±20-50% pre-op",
                2: "2 - BP ±20% pre-op"
            }[x],
            key="aldrete_circulation"
        )
    
    with col2:
        aldrete_scores["consciousness"] = st.radio(
            "Consciousness",
            options=[0, 1, 2],
            format_func=lambda x: {
                0: "0 - Not responding",
                1: "1 - Arousable",
                2: "2 - Fully awake"
            }[x],
            key="aldrete_consciousness"
        )
        
        aldrete_scores["color"] = st.radio(
            "Color",
            options=[0, 1, 2],
            format_func=lambda x: {
                0: "0 - Cyanotic",
                1: "1 - Pale/dusky",
                2: "2 - Normal"
            }[x],
            key="aldrete_color"
        )
    
    # Calculate total
    total_score = sum(aldrete_scores.values())
    st.metric("Total Aldrete Score", f"{total_score}/10")
    
    # Discharge information
    st.subheader("Discharge Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        discharge_time = st.time_input("Discharge Time", key="discharge_time_input")
        st.checkbox("Escort Present", key="escort_present")
    
    with col2:
        st.checkbox("Post-op Instructions Given", key="postop_instructions_given")
    
    # Save post-anesthesia data
    if st.button("Save Post-Anesthesia Score", type="primary"):
        update_data = {
            "aldrete_activity": aldrete_scores["activity"],
            "aldrete_respiration": aldrete_scores["respiration"],
            "aldrete_circulation": aldrete_scores["circulation"],
            "aldrete_consciousness": aldrete_scores["consciousness"],
            "aldrete_color": aldrete_scores["color"],
            "aldrete_total": total_score,
            "escort_present": st.session_state.get("escort_present", False),
            "postop_instructions_given": st.session_state.get("postop_instructions_given", False)
        }
        
        if discharge_time:
            discharge_datetime = datetime.combine(datetime.today(), discharge_time)
            update_data["discharge_time"] = discharge_datetime.isoformat()
        
        if st.session_state.record_id:
            result = api_put(f"/records/{st.session_state.record_id}", update_data)
            if result:
                st.success("Post-anesthesia score saved!")
    
    # Export options
    st.subheader("Export Options")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Generate Note (Markdown)"):
            if st.session_state.record_id:
                result = api_get(f"/records/{st.session_state.record_id}/export/markdown")
                if result:
                    st.text_area("Anesthesia Note", value=result["markdown"], height=400)
    
    with col2:
        if st.button("Export to PDF"):
            st.info("PDF export functionality will be implemented")
    
    with col3:
        if st.button("Push to Open Dental"):
            if st.session_state.record_id:
                result = api_post(f"/open-dental/push-record/{st.session_state.record_id}", {})
                if result:
                    st.success("Record pushed to Open Dental (stub)")

if __name__ == "__main__":
    main()