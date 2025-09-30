from sqlalchemy import Column, Integer, String, DateTime, Text, Enum, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class EvidenceType(enum.Enum):
    SCREENSHOT = "Screenshot"
    LOG_FILE = "Log File"
    DOCUMENT = "Document"
    CONFIGURATION = "Configuration"
    REPORT = "Report"
    VIDEO = "Video"
    OTHER = "Other"


class EvidenceStatus(enum.Enum):
    PENDING = "Pending"
    COLLECTED = "Collected"
    VERIFIED = "Verified"
    EXPIRED = "Expired"
    REJECTED = "Rejected"


class CollectionMethod(enum.Enum):
    MANUAL = "Manual"
    AUTOMATED = "Automated"
    API = "API"
    SCHEDULED = "Scheduled"


class Evidence(Base):
    __tablename__ = "evidence"
    
    id = Column(Integer, primary_key=True, index=True)
    evidence_id = Column(String(100), unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    evidence_type = Column(Enum(EvidenceType), nullable=False)
    status = Column(Enum(EvidenceStatus), default=EvidenceStatus.PENDING)
    
    # File information
    file_name = Column(String(255))
    file_path = Column(String(500))
    file_size = Column(Integer)
    file_hash = Column(String(100))  # SHA-256 hash for integrity
    
    # Collection details
    collection_method = Column(Enum(CollectionMethod))
    collected_by = Column(String(100))
    collection_date = Column(DateTime)
    collection_source = Column(String(255))  # System, API, etc.
    
    # Associations
    control_id = Column(String(100))
    framework = Column(String(100))
    requirement_id = Column(String(100))
    
    # Validity
    valid_from = Column(DateTime)
    valid_until = Column(DateTime)
    is_expired = Column(Boolean, default=False)
    
    # Review
    reviewed_by = Column(String(100))
    review_date = Column(DateTime)
    review_notes = Column(Text)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    tags = Column(JSON)
    metadata = Column(JSON)
    
    # Relationships
    collection_id = Column(Integer, ForeignKey("evidence_collections.id"))
    collection = relationship("EvidenceCollection", back_populates="evidence_items")


class EvidenceCollection(Base):
    """Represents an automated evidence collection job"""
    __tablename__ = "evidence_collections"
    
    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(String(100), unique=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Collection configuration
    collection_type = Column(String(100))  # AWS Logs, Screenshots, ServiceNow Tickets, etc.
    schedule = Column(String(100))  # Cron expression
    is_active = Column(Boolean, default=True)
    
    # Collection parameters
    source_system = Column(String(100))
    collection_params = Column(JSON)  # API endpoints, filters, etc.
    
    # Status
    last_run = Column(DateTime)
    next_run = Column(DateTime)
    last_status = Column(String(50))
    error_message = Column(Text)
    
    # Statistics
    total_collections = Column(Integer, default=0)
    successful_collections = Column(Integer, default=0)
    failed_collections = Column(Integer, default=0)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    evidence_items = relationship("Evidence", back_populates="collection")