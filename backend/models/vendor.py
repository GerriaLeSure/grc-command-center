from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class VendorRiskLevel(enum.Enum):
    CRITICAL = "Critical"
    HIGH = "High"
    MEDIUM = "Medium"
    LOW = "Low"


class VendorStatus(enum.Enum):
    ACTIVE = "Active"
    ONBOARDING = "Onboarding"
    OFFBOARDING = "Offboarding"
    INACTIVE = "Inactive"
    SUSPENDED = "Suspended"


class AssessmentStatus(enum.Enum):
    NOT_STARTED = "Not Started"
    IN_PROGRESS = "In Progress"
    UNDER_REVIEW = "Under Review"
    COMPLETED = "Completed"
    EXPIRED = "Expired"


class Vendor(Base):
    __tablename__ = "vendors"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(String(100), unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(Enum(VendorStatus), default=VendorStatus.ACTIVE)
    
    # Contact information
    primary_contact_name = Column(String(100))
    primary_contact_email = Column(String(100))
    primary_contact_phone = Column(String(50))
    website = Column(String(255))
    
    # Risk assessment
    risk_level = Column(Enum(VendorRiskLevel))
    risk_score = Column(Float)
    criticality_level = Column(String(50))
    
    # Business details
    service_type = Column(String(255))
    contract_start_date = Column(DateTime)
    contract_end_date = Column(DateTime)
    annual_spend = Column(Float)
    
    # Compliance
    data_access = Column(Boolean, default=False)
    data_types = Column(JSON)  # List of data types accessed
    compliance_requirements = Column(JSON)  # List of required certifications
    certifications = Column(JSON)  # List of vendor certifications (SOC2, ISO, etc.)
    
    # Assessment tracking
    last_assessment_date = Column(DateTime)
    next_assessment_date = Column(DateTime)
    assessment_frequency_days = Column(Integer, default=365)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = Column(JSON)
    custom_fields = Column(JSON)
    
    # Relationships
    assessments = relationship("VendorAssessment", back_populates="vendor")


class VendorAssessment(Base):
    __tablename__ = "vendor_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    vendor_id = Column(Integer, ForeignKey("vendors.id"))
    assessment_id = Column(String(100), unique=True, index=True)
    
    # Assessment details
    assessment_type = Column(String(100))  # Initial, Annual, Ad-hoc
    status = Column(Enum(AssessmentStatus), default=AssessmentStatus.NOT_STARTED)
    assessor = Column(String(100))
    
    # Dates
    start_date = Column(DateTime)
    completion_date = Column(DateTime)
    due_date = Column(DateTime)
    
    # Scoring
    overall_score = Column(Float)
    security_score = Column(Float)
    privacy_score = Column(Float)
    operational_score = Column(Float)
    financial_score = Column(Float)
    
    # Results
    findings = Column(JSON)
    recommendations = Column(JSON)
    action_items = Column(JSON)
    
    # Questionnaire
    questionnaire_id = Column(Integer, ForeignKey("vendor_questionnaires.id"))
    responses = Column(JSON)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vendor = relationship("Vendor", back_populates="assessments")
    questionnaire = relationship("VendorQuestionnaire")


class VendorQuestionnaire(Base):
    __tablename__ = "vendor_questionnaires"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(50))
    
    # Questionnaire structure
    categories = Column(JSON)  # Security, Privacy, Operational, etc.
    questions = Column(JSON)  # List of questions with scoring
    
    # Metadata
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)