from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime
from typing import List, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import models
from schemas import schemas

def initialize_default_medications(db: Session):
    """Initialize default medications if they don't exist"""
    default_meds = [
        {"name": "Midazolam (Versed)", "concentration": "5mg/mL", "unit_dose": "5mg", "dea_schedule": "C-IV", "how_supplied": "5mL vial"},
        {"name": "Fentanyl", "concentration": "50mcg/mL", "unit_dose": "100mcg", "dea_schedule": "C-II", "how_supplied": "2mL ampule"},
        {"name": "Propofol", "concentration": "10mg/mL", "unit_dose": "200mg", "dea_schedule": "Non-controlled", "how_supplied": "20mL vial"},
        {"name": "Ketamine", "concentration": "50mg/mL", "unit_dose": "100mg", "dea_schedule": "C-III", "how_supplied": "2mL vial"},
        {"name": "Dexmedetomidine", "concentration": "100mcg/mL", "unit_dose": "200mcg", "dea_schedule": "Non-controlled", "how_supplied": "2mL vial"},
        {"name": "Decadron", "concentration": "10mg/mL", "unit_dose": "10mg", "dea_schedule": "Non-controlled", "how_supplied": "1mL vial"},
        {"name": "Zofran", "concentration": "4mg/2mL", "unit_dose": "4mg", "dea_schedule": "Non-controlled", "how_supplied": "2mL vial"}
    ]
    
    for med_data in default_meds:
        existing = db.query(models.Medication).filter_by(name=med_data["name"]).first()
        if not existing:
            med = models.Medication(**med_data)
            db.add(med)
    
    db.commit()

# Patient CRUD
def get_patient_by_open_dental_id(db: Session, open_dental_id: str):
    return db.query(models.Patient).filter(models.Patient.open_dental_id == open_dental_id).first()

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

# Location CRUD
def get_locations(db: Session):
    return db.query(models.Location).all()

def create_location(db: Session, location: schemas.LocationCreate):
    db_location = models.Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location

# Provider CRUD
def get_providers(db: Session, role: Optional[str] = None):
    query = db.query(models.Provider)
    if role:
        query = query.filter(models.Provider.role == role)
    return query.all()

def create_provider(db: Session, provider: schemas.ProviderCreate):
    db_provider = models.Provider(**provider.dict())
    db.add(db_provider)
    db.commit()
    db.refresh(db_provider)
    return db_provider

# Medication CRUD
def get_medications(db: Session):
    return db.query(models.Medication).all()

def create_medication(db: Session, medication: schemas.MedicationCreate):
    db_medication = models.Medication(**medication.dict())
    db.add(db_medication)
    db.commit()
    db.refresh(db_medication)
    return db_medication

# Inventory CRUD
def get_inventory_by_location(db: Session, location_id: int):
    return db.query(models.MedicationInventory).filter(
        models.MedicationInventory.location_id == location_id
    ).all()

def add_inventory(db: Session, inventory: schemas.MedicationInventoryCreate):
    db_inventory = models.MedicationInventory(**inventory.dict())
    db.add(db_inventory)
    db.commit()
    db.refresh(db_inventory)
    return db_inventory

def decrement_inventory(db: Session, medication_id: int, location_id: int, amount: float):
    inventory = db.query(models.MedicationInventory).filter(
        and_(
            models.MedicationInventory.medication_id == medication_id,
            models.MedicationInventory.location_id == location_id,
            models.MedicationInventory.quantity >= amount
        )
    ).first()
    
    if inventory:
        inventory.quantity -= amount
        db.commit()
        return True
    return False

# Anesthesia Record CRUD
def get_anesthesia_record(db: Session, record_id: int):
    return db.query(models.AnesthesiaRecord).filter(models.AnesthesiaRecord.id == record_id).first()

def create_anesthesia_record(db: Session, record: schemas.AnesthesiaRecordCreate):
    db_record = models.AnesthesiaRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return db_record

def update_anesthesia_record(db: Session, record_id: int, record_update: schemas.AnesthesiaRecordUpdate):
    db_record = get_anesthesia_record(db, record_id)
    if not db_record:
        return None
    
    update_data = record_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)
    
    db_record.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_record)
    return db_record

# Medication Administration CRUD
def add_medication_administration(db: Session, administration: schemas.MedicationAdministrationCreate):
    db_admin = models.MedicationAdministration(**administration.dict())
    db.add(db_admin)
    
    # Decrement inventory
    record = get_anesthesia_record(db, administration.record_id)
    if record:
        total_used = administration.dose_ml + administration.waste_ml
        decrement_inventory(db, administration.medication_id, record.location_id, total_used)
    
    db.commit()
    db.refresh(db_admin)
    return db_admin

# Vital Signs CRUD
def add_vital_sign(db: Session, vital_sign: schemas.VitalSignCreate):
    db_vital = models.VitalSign(**vital_sign.dict())
    db.add(db_vital)
    db.commit()
    db.refresh(db_vital)
    return db_vital

# Export functions
def generate_anesthesia_note(record: models.AnesthesiaRecord) -> str:
    """Generate markdown formatted anesthesia note"""
    note = f"""# Anesthesia Record

## Patient Information
- Name: {record.patient.first_name} {record.patient.last_name}
- DOB: {record.patient.date_of_birth.strftime('%Y-%m-%d')}
- MRN: {record.patient.medical_record_number or 'N/A'}

## Physical Assessment
- ASA Class: {record.asa_class}{' E' if record.asa_modifier_e else ''}
- Mallampati: {record.mallampati or 'Not assessed'}
- Height: {record.height_cm} cm
- Weight: {record.weight_kg} kg
- BMI: {record.bmi:.1f if record.bmi else 'Not calculated'}
- NPO Since: {record.npo_since.strftime('%H:%M') if record.npo_since else 'Not recorded'}

## Providers
- Anesthetist: {record.anesthetist_id or 'Not assigned'}
- Surgeon: {record.surgeon_id or 'Not assigned'}
- Assistant: {record.assistant_id or 'Not assigned'}
- Circulator: {record.circulator_id or 'Not assigned'}

## Monitors
{', '.join(record.monitors) if record.monitors else 'None selected'}

## IV Access
- Route: {record.iv_route or 'N/A'}
- Gauge: {record.iv_gauge or 'N/A'}
- Site: {record.iv_site or 'N/A'}
- Attempts: {record.iv_attempts or 'N/A'}

## Inhalational Agents
- O2 Flow: {record.o2_flow_rate} L/min
- N2O Flow: {record.n2o_flow_rate} L/min
- Start: {record.inhalation_start.strftime('%H:%M') if record.inhalation_start else 'Not started'}
- End: {record.inhalation_end.strftime('%H:%M') if record.inhalation_end else 'Not ended'}

## Times
- Anesthesia Start: {record.anesthesia_start.strftime('%H:%M') if record.anesthesia_start else 'Not recorded'}
- Anesthesia End: {record.anesthesia_end.strftime('%H:%M') if record.anesthesia_end else 'Not recorded'}
- Surgery Start: {record.surgery_start.strftime('%H:%M') if record.surgery_start else 'Not recorded'}
- Surgery End: {record.surgery_end.strftime('%H:%M') if record.surgery_end else 'Not recorded'}

## Medications Administered
"""
    
    for admin in record.medication_administrations:
        note += f"- {admin.medication.name}: {admin.dose_ml} mL (Waste: {admin.waste_ml} mL) at {admin.timestamp.strftime('%H:%M')}\n"
    
    if record.local_anesthetics:
        note += "\n## Local Anesthetics\n"
        for anes_type, carpules in record.local_anesthetics.items():
            note += f"- {anes_type}: {carpules} carpules\n"
    
    note += f"\n## Notes\n{record.notes or 'None'}\n"
    
    if record.aldrete_total is not None:
        note += f"""
## Post Anesthesia Score (Aldrete)
- Activity: {record.aldrete_activity}
- Respiration: {record.aldrete_respiration}
- Circulation: {record.aldrete_circulation}
- Consciousness: {record.aldrete_consciousness}
- Color: {record.aldrete_color}
- Total: {record.aldrete_total}/10
- Discharge Time: {record.discharge_time.strftime('%H:%M') if record.discharge_time else 'Not discharged'}
- Escort Present: {'Yes' if record.escort_present else 'No'}
- Post-op Instructions Given: {'Yes' if record.postop_instructions_given else 'No'}
"""
    
    return note