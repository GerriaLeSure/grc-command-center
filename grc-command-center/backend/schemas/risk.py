from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from models.risk import RiskCategory, RiskStatus, RiskLikelihood, RiskImpact


class RiskBase(BaseModel):
    title: str
    description: Optional[str] = None
    category: RiskCategory
    likelihood: RiskLikelihood
    impact: RiskImpact
    owner: Optional[str] = None
    affected_assets: Optional[List[str]] = None
    threat_source: Optional[str] = None
    vulnerability: Optional[str] = None
    mitigation_strategy: Optional[str] = None
    tags: Optional[List[str]] = None


class RiskCreate(RiskBase):
    pass


class RiskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[RiskCategory] = None
    status: Optional[RiskStatus] = None
    likelihood: Optional[RiskLikelihood] = None
    impact: Optional[RiskImpact] = None
    owner: Optional[str] = None
    mitigation_strategy: Optional[str] = None
    residual_risk_score: Optional[float] = None
    tags: Optional[List[str]] = None


class RiskResponse(RiskBase):
    id: int
    risk_id: str
    status: RiskStatus
    inherent_risk_score: Optional[float]
    residual_risk_score: Optional[float]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RiskHeatmapData(BaseModel):
    likelihood: int
    impact: int
    count: int
    risk_level: str
    risks: List[str]  # List of risk IDs


class RiskImportData(BaseModel):
    risks: List[RiskCreate]


class RiskExportFilter(BaseModel):
    category: Optional[RiskCategory] = None
    status: Optional[RiskStatus] = None
    min_score: Optional[float] = None
    max_score: Optional[float] = None