from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, JSON, Boolean, Table
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class ControlType(enum.Enum):
    PREVENTIVE = "Preventive"
    DETECTIVE = "Detective"
    CORRECTIVE = "Corrective"
    DIRECTIVE = "Directive"


class ControlStatus(enum.Enum):
    IMPLEMENTED = "Implemented"
    PARTIALLY_IMPLEMENTED = "Partially Implemented"
    NOT_IMPLEMENTED = "Not Implemented"
    NOT_APPLICABLE = "Not Applicable"


class ControlFramework(Base):
    __tablename__ = "control_frameworks"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)  # SOC2, NIST, ISO27001
    version = Column(String(50))
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    mappings = relationship("ControlMapping", back_populates="framework")


class Control(Base):
    __tablename__ = "controls"
    
    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(String(100), unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    control_type = Column(Enum(ControlType), nullable=False)
    status = Column(Enum(ControlStatus), default=ControlStatus.NOT_IMPLEMENTED)
    
    # Implementation details
    implementation_description = Column(Text)
    owner = Column(String(100))
    responsible_team = Column(String(100))
    
    # Testing and validation
    test_procedure = Column(Text)
    test_frequency_days = Column(Integer)
    last_tested = Column(DateTime)
    next_test_date = Column(DateTime)
    test_status = Column(String(50))
    
    # Effectiveness
    effectiveness_rating = Column(Integer)  # 1-5 scale
    automation_level = Column(Integer)  # 0-100%
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Additional fields
    tags = Column(JSON)
    custom_fields = Column(JSON)
    
    # Relationships
    mappings = relationship("ControlMapping", back_populates="control")


class ControlMapping(Base):
    """Maps controls to compliance frameworks"""
    __tablename__ = "control_mappings"
    
    id = Column(Integer, primary_key=True, index=True)
    control_id = Column(Integer, ForeignKey("controls.id"))
    framework_id = Column(Integer, ForeignKey("control_frameworks.id"))
    
    # Framework-specific details
    framework_control_id = Column(String(100))  # e.g., "CC6.1" for SOC2
    requirement_text = Column(Text)
    compliance_status = Column(Enum(ControlStatus))
    
    # Evidence
    evidence_required = Column(JSON)
    evidence_collected = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    control = relationship("Control", back_populates="mappings")
    framework = relationship("ControlFramework", back_populates="mappings")