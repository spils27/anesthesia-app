from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List, Dict

class LocationBase(BaseModel):
    name: str
    address: Optional[str] = None

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int
    
    class Config:
        from_attributes = True

class ProviderBase(BaseModel):
    name: str
    role: str
    license_number: Optional[str] = None

class ProviderCreate(ProviderBase):
    pass

class Provider(ProviderBase):
    id: int
    
    class Config:
        from_attributes = True

class MedicationBase(BaseModel):
    name: str
    concentration: str
    unit_dose: str
    dea_schedule: str
    how_supplied: str

class MedicationCreate(MedicationBase):
    pass

class Medication(MedicationBase):
    id: int
    
    class Config:
        from_attributes = True

class MedicationInventoryBase(BaseModel):
    medication_id: int
    location_id: int
    quantity: float
    lot_number: str
    expiration_date: datetime
    supplier: str
    invoice_number: str
    date_received: datetime

class MedicationInventoryCreate(MedicationInventoryBase):
    pass

class MedicationInventory(MedicationInventoryBase):
    id: int
    
    class Config:
        from_attributes = True

class PatientBase(BaseModel):
    open_dental_id: str
    first_name: str
    last_name: str
    date_of_birth: datetime
    medical_record_number: Optional[str] = None

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int
    
    class Config:
        from_attributes = True

class VitalSignBase(BaseModel):
    bp_systolic: Optional[int] = None
    bp_diastolic: Optional[int] = None
    map: Optional[int] = None
    heart_rate: Optional[int] = None
    spo2: Optional[int] = None
    etco2: Optional[int] = None
    temperature: Optional[float] = None

class VitalSignCreate(VitalSignBase):
    record_id: int

class VitalSign(VitalSignBase):
    id: int
    record_id: int
    timestamp: datetime
    
    class Config:
        from_attributes = True

class MedicationAdministrationBase(BaseModel):
    medication_id: int
    dose_ml: float
    waste_ml: float = 0

class MedicationAdministrationCreate(MedicationAdministrationBase):
    record_id: int

class MedicationAdministration(MedicationAdministrationBase):
    id: int
    record_id: int
    timestamp: datetime
    medication: Optional[Medication] = None
    
    class Config:
        from_attributes = True

class AnesthesiaRecordBase(BaseModel):
    patient_id: int
    location_id: int
    
    # Physical assessment
    asa_class: Optional[str] = None
    asa_modifier_e: bool = False
    mallampati: Optional[str] = None
    height_cm: Optional[float] = None
    weight_kg: Optional[float] = None
    bmi: Optional[float] = None
    npo_since: Optional[datetime] = None
    
    # Providers
    anesthetist_id: Optional[int] = None
    surgeon_id: Optional[int] = None
    assistant_id: Optional[int] = None
    circulator_id: Optional[int] = None
    
    # Inhalational agents
    o2_flow_rate: Optional[float] = None
    n2o_flow_rate: Optional[float] = None
    inhalation_start: Optional[datetime] = None
    inhalation_end: Optional[datetime] = None
    
    # IV access
    iv_route: Optional[str] = None
    iv_gauge: Optional[str] = None
    iv_site: Optional[str] = None
    iv_attempts: Optional[int] = None
    
    # Monitors
    monitors: Optional[List[str]] = []
    
    # Times
    anesthesia_start: Optional[datetime] = None
    anesthesia_end: Optional[datetime] = None
    surgery_start: Optional[datetime] = None
    surgery_end: Optional[datetime] = None
    
    # Notes
    notes: Optional[str] = None
    
    # Preop checklist
    equipment_ready: Optional[bool] = None
    preop_instructions_given: Optional[bool] = None
    patient_procedure_verified: Optional[bool] = None
    timeout_start: Optional[datetime] = None
    timeout_end: Optional[datetime] = None
    medical_history_reviewed: Optional[bool] = None
    allergies_reviewed: Optional[bool] = None
    medications_reviewed: Optional[bool] = None
    consults_reviewed: Optional[bool] = None
    
    # Post anesthesia score
    aldrete_activity: Optional[int] = None
    aldrete_respiration: Optional[int] = None
    aldrete_circulation: Optional[int] = None
    aldrete_consciousness: Optional[int] = None
    aldrete_color: Optional[int] = None
    aldrete_total: Optional[int] = None
    discharge_time: Optional[datetime] = None
    escort_present: Optional[bool] = None
    postop_instructions_given: Optional[bool] = None
    
    # Local anesthetics
    local_anesthetics: Optional[Dict[str, int]] = {}

class AnesthesiaRecordCreate(AnesthesiaRecordBase):
    pass

class AnesthesiaRecordUpdate(AnesthesiaRecordBase):
    patient_id: Optional[int] = None
    location_id: Optional[int] = None

class AnesthesiaRecord(AnesthesiaRecordBase):
    id: int
    created_at: datetime
    updated_at: datetime
    patient: Optional[Patient] = None
    medication_administrations: List[MedicationAdministration] = []
    vital_signs: List[VitalSign] = []
    
    class Config:
        from_attributes = True