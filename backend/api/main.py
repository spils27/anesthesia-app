from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import os

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models import Base, engine, get_db
from schemas import schemas
from services import crud

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Anesthesia Record API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8501"],  # Streamlit default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize default medications
@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    crud.initialize_default_medications(db)
    db.close()

# Patient endpoints
@app.get("/api/patients/{open_dental_id}", response_model=schemas.Patient)
def get_patient_by_open_dental_id(open_dental_id: str, db: Session = Depends(get_db)):
    patient = crud.get_patient_by_open_dental_id(db, open_dental_id)
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    return patient

@app.post("/api/patients/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    return crud.create_patient(db, patient)

# Location endpoints
@app.get("/api/locations/", response_model=List[schemas.Location])
def get_locations(db: Session = Depends(get_db)):
    return crud.get_locations(db)

@app.post("/api/locations/", response_model=schemas.Location)
def create_location(location: schemas.LocationCreate, db: Session = Depends(get_db)):
    return crud.create_location(db, location)

# Provider endpoints
@app.get("/api/providers/", response_model=List[schemas.Provider])
def get_providers(role: str = None, db: Session = Depends(get_db)):
    return crud.get_providers(db, role)

@app.post("/api/providers/", response_model=schemas.Provider)
def create_provider(provider: schemas.ProviderCreate, db: Session = Depends(get_db)):
    return crud.create_provider(db, provider)

# Medication endpoints
@app.get("/api/medications/", response_model=List[schemas.Medication])
def get_medications(db: Session = Depends(get_db)):
    return crud.get_medications(db)

@app.post("/api/medications/", response_model=schemas.Medication)
def create_medication(medication: schemas.MedicationCreate, db: Session = Depends(get_db)):
    return crud.create_medication(db, medication)

# Medication inventory endpoints
@app.get("/api/inventory/location/{location_id}", response_model=List[schemas.MedicationInventory])
def get_inventory_by_location(location_id: int, db: Session = Depends(get_db)):
    return crud.get_inventory_by_location(db, location_id)

@app.post("/api/inventory/", response_model=schemas.MedicationInventory)
def add_inventory(inventory: schemas.MedicationInventoryCreate, db: Session = Depends(get_db)):
    return crud.add_inventory(db, inventory)

# Anesthesia record endpoints
@app.get("/api/records/{record_id}", response_model=schemas.AnesthesiaRecord)
def get_record(record_id: int, db: Session = Depends(get_db)):
    record = crud.get_anesthesia_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@app.post("/api/records/", response_model=schemas.AnesthesiaRecord)
def create_record(record: schemas.AnesthesiaRecordCreate, db: Session = Depends(get_db)):
    return crud.create_anesthesia_record(db, record)

@app.put("/api/records/{record_id}", response_model=schemas.AnesthesiaRecord)
def update_record(record_id: int, record: schemas.AnesthesiaRecordUpdate, db: Session = Depends(get_db)):
    return crud.update_anesthesia_record(db, record_id, record)

# Medication administration endpoints
@app.post("/api/records/{record_id}/medications/", response_model=schemas.MedicationAdministration)
def add_medication_administration(
    record_id: int,
    administration: schemas.MedicationAdministrationBase,
    db: Session = Depends(get_db)
):
    admin_create = schemas.MedicationAdministrationCreate(
        record_id=record_id,
        **administration.dict()
    )
    return crud.add_medication_administration(db, admin_create)

# Vital signs endpoints
@app.post("/api/records/{record_id}/vitals/", response_model=schemas.VitalSign)
def add_vital_sign(
    record_id: int,
    vital_sign: schemas.VitalSignBase,
    db: Session = Depends(get_db)
):
    vital_create = schemas.VitalSignCreate(
        record_id=record_id,
        **vital_sign.dict()
    )
    return crud.add_vital_sign(db, vital_create)

# Export endpoints
@app.get("/api/records/{record_id}/export/markdown")
def export_markdown(record_id: int, db: Session = Depends(get_db)):
    record = crud.get_anesthesia_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"markdown": crud.generate_anesthesia_note(record)}

@app.get("/api/records/{record_id}/export/json")
def export_json(record_id: int, db: Session = Depends(get_db)):
    record = crud.get_anesthesia_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return schemas.AnesthesiaRecord.from_orm(record)

# Open Dental integration stubs
@app.post("/api/open-dental/push-record/{record_id}")
def push_to_open_dental(record_id: int, db: Session = Depends(get_db)):
    # Stub for Open Dental integration
    record = crud.get_anesthesia_record(db, record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    
    # TODO: Implement actual Open Dental API integration
    return {"status": "success", "message": "Record pushed to Open Dental (stub)"}

@app.get("/api/open-dental/patient/{patient_id}")
def get_open_dental_patient(patient_id: str):
    # Stub for Open Dental patient data retrieval
    # TODO: Implement actual Open Dental API integration
    return {
        "open_dental_id": patient_id,
        "first_name": "John",
        "last_name": "Doe",
        "date_of_birth": "1990-01-01",
        "medical_record_number": "MRN123456"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)