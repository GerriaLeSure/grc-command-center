from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from models.vendor import Vendor, VendorAssessment, VendorQuestionnaire, VendorStatus, VendorRiskLevel, AssessmentStatus
from schemas.vendor import VendorCreate, VendorUpdate, VendorResponse, VendorAssessmentCreate, VendorAssessmentResponse

router = APIRouter()


def generate_vendor_id(db: Session) -> str:
    """Generate unique vendor ID"""
    count = db.query(Vendor).count()
    return f"VND-{count + 1:05d}"


def generate_assessment_id(db: Session) -> str:
    """Generate unique assessment ID"""
    count = db.query(VendorAssessment).count()
    return f"ASSESS-{count + 1:05d}"


def calculate_vendor_risk_score(vendor: Vendor, assessment: VendorAssessment = None) -> float:
    """Calculate vendor risk score based on various factors"""
    score = 0.0
    
    # Base score on data access
    if vendor.data_access:
        score += 30
    
    # Score based on spend
    if vendor.annual_spend:
        if vendor.annual_spend > 1000000:
            score += 30
        elif vendor.annual_spend > 100000:
            score += 20
        else:
            score += 10
    
    # Assessment score
    if assessment and assessment.overall_score:
        score += (100 - assessment.overall_score) * 0.4
    
    return min(score, 100)


@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(vendor: VendorCreate, db: Session = Depends(get_db)):
    """Create a new vendor"""
    db_vendor = Vendor(
        vendor_id=generate_vendor_id(db),
        **vendor.dict()
    )
    
    db.add(db_vendor)
    db.commit()
    db.refresh(db_vendor)
    return db_vendor


@router.get("/", response_model=List[VendorResponse])
async def get_vendors(
    skip: int = 0,
    limit: int = 100,
    status: Optional[VendorStatus] = None,
    risk_level: Optional[VendorRiskLevel] = None,
    db: Session = Depends(get_db)
):
    """Get all vendors with optional filters"""
    query = db.query(Vendor)
    
    if status:
        query = query.filter(Vendor.status == status)
    if risk_level:
        query = query.filter(Vendor.risk_level == risk_level)
    
    vendors = query.offset(skip).limit(limit).all()
    return vendors


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(vendor_id: str, db: Session = Depends(get_db)):
    """Get a specific vendor by ID"""
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.put("/{vendor_id}", response_model=VendorResponse)
async def update_vendor(
    vendor_id: str,
    vendor_update: VendorUpdate,
    db: Session = Depends(get_db)
):
    """Update a vendor"""
    db_vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not db_vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    update_data = vendor_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_vendor, field, value)
    
    db_vendor.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_vendor)
    return db_vendor


@router.post("/assessments/", response_model=VendorAssessmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assessment(
    assessment: VendorAssessmentCreate,
    db: Session = Depends(get_db)
):
    """Create a new vendor assessment"""
    vendor = db.query(Vendor).filter(Vendor.id == assessment.vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    db_assessment = VendorAssessment(
        assessment_id=generate_assessment_id(db),
        start_date=datetime.utcnow(),
        **assessment.dict()
    )
    
    db.add(db_assessment)
    db.commit()
    db.refresh(db_assessment)
    return db_assessment


@router.get("/assessments/{vendor_id}", response_model=List[VendorAssessmentResponse])
async def get_vendor_assessments(vendor_id: str, db: Session = Depends(get_db)):
    """Get all assessments for a vendor"""
    vendor = db.query(Vendor).filter(Vendor.vendor_id == vendor_id).first()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    
    assessments = db.query(VendorAssessment).filter(
        VendorAssessment.vendor_id == vendor.id
    ).all()
    
    return assessments


@router.post("/assessments/{assessment_id}/complete")
async def complete_assessment(
    assessment_id: str,
    scores: dict,
    db: Session = Depends(get_db)
):
    """Complete a vendor assessment with scores"""
    assessment = db.query(VendorAssessment).filter(
        VendorAssessment.assessment_id == assessment_id
    ).first()
    if not assessment:
        raise HTTPException(status_code=404, detail="Assessment not found")
    
    assessment.status = AssessmentStatus.COMPLETED
    assessment.completion_date = datetime.utcnow()
    assessment.security_score = scores.get("security_score", 0)
    assessment.privacy_score = scores.get("privacy_score", 0)
    assessment.operational_score = scores.get("operational_score", 0)
    assessment.financial_score = scores.get("financial_score", 0)
    
    # Calculate overall score
    assessment.overall_score = (
        assessment.security_score * 0.4 +
        assessment.privacy_score * 0.3 +
        assessment.operational_score * 0.2 +
        assessment.financial_score * 0.1
    )
    
    # Update vendor risk score
    vendor = assessment.vendor
    vendor.risk_score = calculate_vendor_risk_score(vendor, assessment)
    
    # Determine risk level
    if vendor.risk_score >= 75:
        vendor.risk_level = VendorRiskLevel.CRITICAL
    elif vendor.risk_score >= 50:
        vendor.risk_level = VendorRiskLevel.HIGH
    elif vendor.risk_score >= 25:
        vendor.risk_level = VendorRiskLevel.MEDIUM
    else:
        vendor.risk_level = VendorRiskLevel.LOW
    
    vendor.last_assessment_date = datetime.utcnow()
    vendor.next_assessment_date = datetime.utcnow() + timedelta(days=vendor.assessment_frequency_days)
    
    db.commit()
    
    return {
        "success": True,
        "assessment_id": assessment_id,
        "overall_score": assessment.overall_score,
        "vendor_risk_level": vendor.risk_level.value
    }


@router.get("/analytics/risk-distribution")
async def get_vendor_risk_distribution(db: Session = Depends(get_db)):
    """Get vendor risk distribution analytics"""
    total_vendors = db.query(Vendor).filter(Vendor.status == VendorStatus.ACTIVE).count()
    
    risk_distribution = {}
    for risk_level in VendorRiskLevel:
        count = db.query(Vendor).filter(
            Vendor.status == VendorStatus.ACTIVE,
            Vendor.risk_level == risk_level
        ).count()
        risk_distribution[risk_level.value] = {
            "count": count,
            "percentage": (count / total_vendors * 100) if total_vendors > 0 else 0
        }
    
    # Upcoming assessments
    upcoming_assessments = db.query(Vendor).filter(
        Vendor.next_assessment_date <= datetime.utcnow() + timedelta(days=30),
        Vendor.status == VendorStatus.ACTIVE
    ).count()
    
    # Total assessments completed this year
    year_start = datetime(datetime.utcnow().year, 1, 1)
    assessments_this_year = db.query(VendorAssessment).filter(
        VendorAssessment.completion_date >= year_start
    ).count()
    
    return {
        "total_active_vendors": total_vendors,
        "risk_distribution": risk_distribution,
        "upcoming_assessments_30_days": upcoming_assessments,
        "assessments_completed_this_year": assessments_this_year
    }