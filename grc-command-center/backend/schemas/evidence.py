from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from models.evidence import EvidenceType, EvidenceStatus, CollectionMethod


class EvidenceBase(BaseModel):
    title: str
    description: Optional[str] = None
    evidence_type: EvidenceType
    control_id: Optional[str] = None
    framework: Optional[str] = None
    requirement_id: Optional[str] = None


class EvidenceCreate(EvidenceBase):
    file_name: Optional[str] = None
    file_path: Optional[str] = None
    collection_source: Optional[str] = None


class EvidenceResponse(EvidenceBase):
    id: int
    evidence_id: str
    status: EvidenceStatus
    file_name: Optional[str]
    collection_date: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True