from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from models.control import ControlType, ControlStatus


class ControlBase(BaseModel):
    title: str
    description: Optional[str] = None
    control_type: ControlType
    implementation_description: Optional[str] = None
    owner: Optional[str] = None
    responsible_team: Optional[str] = None
    test_procedure: Optional[str] = None
    test_frequency_days: Optional[int] = None


class ControlCreate(ControlBase):
    pass


class ControlUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[ControlStatus] = None
    implementation_description: Optional[str] = None
    owner: Optional[str] = None
    effectiveness_rating: Optional[int] = None
    system_orchestration_level: Optional[int] = None


class ControlResponse(ControlBase):
    id: int
    control_id: str
    status: ControlStatus
    effectiveness_rating: Optional[int]
    system_orchestration_level: Optional[int]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ControlFrameworkResponse(BaseModel):
    id: int
    name: str
    version: Optional[str]
    description: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True