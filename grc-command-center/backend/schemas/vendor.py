from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.vendor import VendorRiskLevel, VendorStatus, AssessmentStatus


class VendorBase(BaseModel):
    name: str
    description: Optional[str] = None
    service_type: Optional[str] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    website: Optional[str] = None
    data_access: bool = False
    annual_spend: Optional[float] = None


class VendorCreate(VendorBase):
    pass


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    status: Optional[VendorStatus] = None
    risk_level: Optional[VendorRiskLevel] = None
    risk_score: Optional[float] = None
    primary_contact_email: Optional[str] = None
    annual_spend: Optional[float] = None


class VendorResponse(VendorBase):
    id: int
    vendor_id: str
    status: VendorStatus
    risk_level: Optional[VendorRiskLevel]
    risk_score: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class VendorAssessmentCreate(BaseModel):
    vendor_id: int
    assessment_type: str
    assessor: Optional[str] = None
    due_date: Optional[datetime] = None


class VendorAssessmentResponse(BaseModel):
    id: int
    assessment_id: str
    vendor_id: int
    assessment_type: str
    status: AssessmentStatus
    overall_score: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True