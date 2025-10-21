from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Enum, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from database import Base


class RiskCategory(enum.Enum):
    STRATEGIC = "Strategic"
    OPERATIONAL = "Operational"
    FINANCIAL = "Financial"
    COMPLIANCE = "Compliance"
    TECHNOLOGY = "Technology"
    REPUTATIONAL = "Reputational"


class RiskStatus(enum.Enum):
    OPEN = "Open"
    IN_PROGRESS = "In Progress"
    MITIGATED = "Mitigated"
    ACCEPTED = "Accepted"
    CLOSED = "Closed"


class RiskLikelihood(enum.Enum):
    RARE = 1
    UNLIKELY = 2
    POSSIBLE = 3
    LIKELY = 4
    ALMOST_CERTAIN = 5


class RiskImpact(enum.Enum):
    INSIGNIFICANT = 1
    MINOR = 2
    MODERATE = 3
    MAJOR = 4
    CATASTROPHIC = 5


class Risk(Base):
    __tablename__ = "risks"
    
    id = Column(Integer, primary_key=True, index=True)
    risk_id = Column(String(50), unique=True, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(Enum(RiskCategory), nullable=False)
    status = Column(Enum(RiskStatus), default=RiskStatus.OPEN)
    
    # Risk Scoring
    likelihood = Column(Enum(RiskLikelihood), nullable=False)
    impact = Column(Enum(RiskImpact), nullable=False)
    inherent_risk_score = Column(Float)  # likelihood * impact
    residual_risk_score = Column(Float)  # after controls
    
    # Details
    owner = Column(String(100))
    affected_assets = Column(JSON)  # List of affected systems/assets
    threat_source = Column(String(255))
    vulnerability = Column(Text)
    
    # Mitigation
    mitigation_strategy = Column(Text)
    mitigation_deadline = Column(DateTime)
    control_ids = Column(JSON)  # List of control IDs
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_reviewed = Column(DateTime)
    review_frequency_days = Column(Integer, default=90)
    
    # Additional fields
    tags = Column(JSON)
    custom_fields = Column(JSON)
    
    def calculate_inherent_risk(self):
        """Calculate inherent risk score"""
        if self.likelihood and self.impact:
            self.inherent_risk_score = self.likelihood.value * self.impact.value
    
    def get_risk_level(self, score: float) -> str:
        """Get risk level based on score"""
        if score >= 15:
            return "Critical"
        elif score >= 10:
            return "High"
        elif score >= 5:
            return "Medium"
        else:
            return "Low"