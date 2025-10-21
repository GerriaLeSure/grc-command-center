from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.compliance import ComplianceStatus


class ComplianceFrameworkResponse(BaseModel):
    id: int
    framework_id: str
    name: str
    version: Optional[str]
    overall_compliance_percentage: float
    status: Optional[ComplianceStatus]
    total_requirements: int
    compliant_requirements: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class ComplianceRequirementResponse(BaseModel):
    id: int
    requirement_id: str
    title: str
    description: Optional[str]
    category: Optional[str]
    status: ComplianceStatus
    compliance_percentage: float
    owner: Optional[str]
    
    class Config:
        from_attributes = True


class ComplianceDashboardData(BaseModel):
    framework_name: str
    compliance_percentage: float
    status: str
    compliant_count: int
    total_count: int
    critical_gaps: List[str]