from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class ComplianceStatus(enum.Enum):
    COMPLIANT = "Compliant"
    PARTIALLY_COMPLIANT = "Partially Compliant"
    NON_COMPLIANT = "Non-Compliant"
    NOT_APPLICABLE = "Not Applicable"
    IN_PROGRESS = "In Progress"


class ComplianceFramework(Base):
    __tablename__ = "compliance_frameworks"
    
    id = Column(Integer, primary_key=True, index=True)
    framework_id = Column(String(100), unique=True, index=True)
    name = Column(String(255), nullable=False)  # SOC2, NIST CSF, ISO 27001, etc.
    version = Column(String(50))
    description = Column(Text)
    
    # Compliance tracking
    overall_compliance_percentage = Column(Float, default=0.0)
    status = Column(Enum(ComplianceStatus))
    
    # Dates
    target_certification_date = Column(DateTime)
    last_audit_date = Column(DateTime)
    next_audit_date = Column(DateTime)
    
    # Requirements
    total_requirements = Column(Integer, default=0)
    compliant_requirements = Column(Integer, default=0)
    partially_compliant_requirements = Column(Integer, default=0)
    non_compliant_requirements = Column(Integer, default=0)
    
    # Metadata
    is_active = Column(Boolean, default=True)
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    requirements = relationship("ComplianceRequirement", back_populates="framework")


class ComplianceRequirement(Base):
    __tablename__ = "compliance_requirements"
    
    id = Column(Integer, primary_key=True, index=True)
    framework_id = Column(Integer, ForeignKey("compliance_frameworks.id"))
    requirement_id = Column(String(100), index=True)
    
    # Requirement details
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    sub_category = Column(String(100))
    
    # Compliance status
    status = Column(Enum(ComplianceStatus), default=ComplianceStatus.IN_PROGRESS)
    compliance_percentage = Column(Float, default=0.0)
    
    # Implementation
    owner = Column(String(100))
    implementation_notes = Column(Text)
    remediation_plan = Column(Text)
    remediation_deadline = Column(DateTime)
    
    # Controls mapping
    mapped_controls = Column(JSON)  # List of control IDs
    
    # Evidence
    required_evidence = Column(JSON)
    collected_evidence = Column(JSON)
    evidence_status = Column(String(50))
    
    # Testing
    test_procedure = Column(Text)
    last_tested = Column(DateTime)
    test_results = Column(Text)
    
    # Metadata
    priority = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    framework = relationship("ComplianceFramework", back_populates="requirements")