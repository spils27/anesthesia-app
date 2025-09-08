from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from .database import Base

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    address = Column(String)
    
    inventories = relationship("MedicationInventory", back_populates="location")
    records = relationship("AnesthesiaRecord", back_populates="location")

class Provider(Base):
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    role = Column(String)  # Anesthetist, Surgeon, Assistant, Circulator
    license_number = Column(String)

class Medication(Base):
    __tablename__ = "medications"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    concentration = Column(String)  # e.g., "5mg/mL"
    unit_dose = Column(String)
    dea_schedule = Column(String)  # C-II, C-III, C-IV, C-V, Non-controlled
    how_supplied = Column(String)
    
    inventories = relationship("MedicationInventory", back_populates="medication")
    administrations = relationship("MedicationAdministration", back_populates="medication")

class MedicationInventory(Base):
    __tablename__ = "medication_inventory"
    
    id = Column(Integer, primary_key=True, index=True)
    medication_id = Column(Integer, ForeignKey("medications.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    quantity = Column(Float)
    lot_number = Column(String)
    expiration_date = Column(DateTime)
    supplier = Column(String)
    invoice_number = Column(String)
    date_received = Column(DateTime)
    
    medication = relationship("Medication", back_populates="inventories")
    location = relationship("Location", back_populates="inventories")

class Patient(Base):
    __tablename__ = "patients"
    
    id = Column(Integer, primary_key=True, index=True)
    open_dental_id = Column(String, unique=True, index=True)
    first_name = Column(String)
    last_name = Column(String)
    date_of_birth = Column(DateTime)
    medical_record_number = Column(String)
    
    records = relationship("AnesthesiaRecord", back_populates="patient")

class AnesthesiaRecord(Base):
    __tablename__ = "anesthesia_records"
    
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Physical assessment
    asa_class = Column(String)  # I, II, III, IV, V, VI
    asa_modifier_e = Column(Boolean, default=False)
    mallampati = Column(String)  # I, II, III, IV
    height_cm = Column(Float)
    weight_kg = Column(Float)
    bmi = Column(Float)
    npo_since = Column(DateTime)
    
    # Providers
    anesthetist_id = Column(Integer, ForeignKey("providers.id"))
    surgeon_id = Column(Integer, ForeignKey("providers.id"))
    assistant_id = Column(Integer, ForeignKey("providers.id"))
    circulator_id = Column(Integer, ForeignKey("providers.id"))
    
    # Inhalational agents
    o2_flow_rate = Column(Float)
    n2o_flow_rate = Column(Float)
    inhalation_start = Column(DateTime)
    inhalation_end = Column(DateTime)
    
    # IV access
    iv_route = Column(String)  # Catheter, Butterfly, IM, PO
    iv_gauge = Column(String)  # 18G-24G
    iv_site = Column(String)
    iv_attempts = Column(Integer)
    
    # Monitors
    monitors = Column(JSON)  # List of active monitors
    
    # Times
    anesthesia_start = Column(DateTime)
    anesthesia_end = Column(DateTime)
    surgery_start = Column(DateTime)
    surgery_end = Column(DateTime)
    
    # Notes
    notes = Column(Text)
    
    # Preop checklist
    equipment_ready = Column(Boolean)
    preop_instructions_given = Column(Boolean)
    patient_procedure_verified = Column(Boolean)
    timeout_start = Column(DateTime)
    timeout_end = Column(DateTime)
    medical_history_reviewed = Column(Boolean)
    allergies_reviewed = Column(Boolean)
    medications_reviewed = Column(Boolean)
    consults_reviewed = Column(Boolean)
    
    # Post anesthesia score
    aldrete_activity = Column(Integer)
    aldrete_respiration = Column(Integer)
    aldrete_circulation = Column(Integer)
    aldrete_consciousness = Column(Integer)
    aldrete_color = Column(Integer)
    aldrete_total = Column(Integer)
    discharge_time = Column(DateTime)
    escort_present = Column(Boolean)
    postop_instructions_given = Column(Boolean)
    
    # Local anesthetics
    local_anesthetics = Column(JSON)  # Dict of type -> carpules used
    
    patient = relationship("Patient", back_populates="records")
    location = relationship("Location", back_populates="records")
    medication_administrations = relationship("MedicationAdministration", back_populates="record")
    vital_signs = relationship("VitalSign", back_populates="record")

class MedicationAdministration(Base):
    __tablename__ = "medication_administrations"
    
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("anesthesia_records.id"))
    medication_id = Column(Integer, ForeignKey("medications.id"))
    dose_ml = Column(Float)
    waste_ml = Column(Float, default=0)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    record = relationship("AnesthesiaRecord", back_populates="medication_administrations")
    medication = relationship("Medication", back_populates="administrations")

class VitalSign(Base):
    __tablename__ = "vital_signs"
    
    id = Column(Integer, primary_key=True, index=True)
    record_id = Column(Integer, ForeignKey("anesthesia_records.id"))
    timestamp = Column(DateTime, default=datetime.utcnow)
    bp_systolic = Column(Integer)
    bp_diastolic = Column(Integer)
    map = Column(Integer)  # Mean Arterial Pressure
    heart_rate = Column(Integer)
    spo2 = Column(Integer)
    etco2 = Column(Integer)
    temperature = Column(Float)
    
    record = relationship("AnesthesiaRecord", back_populates="vital_signs")