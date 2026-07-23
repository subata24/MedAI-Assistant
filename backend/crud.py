from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from backend.models.patient import Patient


def create_patient(
    db: Session,
    name: str,
    discharge_summary: str,
    risk_level: str,
) -> Patient:
    """
    Create and store a new patient record.
    """

    patient = Patient(
        name=name,
        discharge_summary=discharge_summary,
        risk_level=risk_level,
    )

    try:
        db.add(patient)
        db.commit()
        db.refresh(patient)
        return patient

    except SQLAlchemyError:
        db.rollback()
        raise


def get_patients(db: Session) -> list[Patient]:
    """
    Retrieve all patients ordered by newest first.
    """

    return (
        db.query(Patient)
        .order_by(Patient.id.desc())
        .all()
    )


def get_patient(db: Session, patient_id: int) -> Patient | None:
    """
    Retrieve a single patient by ID.
    """

    return (
        db.query(Patient)
        .filter(Patient.id == patient_id)
        .first()
    )