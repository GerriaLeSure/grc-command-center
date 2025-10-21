#!/usr/bin/env python3
"""
Sample Data Generator for GRC Command Center
This script populates the database with sample data for demonstration

Developed and documented by Gerria LeSure.
"""

import sys
import os
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(__file__))

from database import SessionLocal, engine, Base
from models.risk import Risk, RiskCategory, RiskStatus, RiskLikelihood, RiskImpact
from models.control import Control, ControlFramework, ControlMapping, ControlType, ControlStatus
from models.vendor import Vendor, VendorAssessment, VendorQuestionnaire, VendorStatus, VendorRiskLevel
from models.evidence import Evidence, EvidenceType, EvidenceStatus, CollectionMethod
from models.compliance import ComplianceFramework, ComplianceRequirement, ComplianceStatus


def create_sample_risks(db: Session):
    """Create sample risk data"""
    print("Creating sample risks...")
    
    sample_risks = [
        {
            "risk_id": "RISK-00001",
            "title": "Data Breach via Phishing Attack",
            "description": "Risk of data breach through successful phishing attack on employees",
            "category": RiskCategory.TECHNOLOGY,
            "likelihood": RiskLikelihood.LIKELY,
            "impact": RiskImpact.CATASTROPHIC,
            "owner": "CISO",
            "threat_source": "External threat actors",
            "vulnerability": "Insufficient security awareness training",
            "mitigation_strategy": "Implement monthly security training and phishing simulations"
        },
        {
            "risk_id": "RISK-00002",
            "title": "Third-Party Vendor Data Exposure",
            "description": "Risk of data exposure through compromised third-party vendor",
            "category": RiskCategory.OPERATIONAL,
            "likelihood": RiskLikelihood.POSSIBLE,
            "impact": RiskImpact.MAJOR,
            "owner": "Vendor Management Team",
            "threat_source": "Third-party vendors",
            "vulnerability": "Inadequate vendor security assessments",
            "mitigation_strategy": "Implement comprehensive vendor risk assessment program"
        },
        {
            "risk_id": "RISK-00003",
            "title": "Non-compliance with SOC2 Requirements",
            "description": "Risk of failing SOC2 audit due to control gaps",
            "category": RiskCategory.COMPLIANCE,
            "likelihood": RiskLikelihood.UNLIKELY,
            "impact": RiskImpact.MAJOR,
            "owner": "Compliance Manager",
            "threat_source": "Internal process gaps",
            "vulnerability": "Incomplete control implementation",
            "mitigation_strategy": "Close identified control gaps before audit"
        },
        {
            "risk_id": "RISK-00004",
            "title": "Cloud Infrastructure Misconfiguration",
            "description": "Risk of data exposure due to misconfigured cloud resources",
            "category": RiskCategory.TECHNOLOGY,
            "likelihood": RiskLikelihood.POSSIBLE,
            "impact": RiskImpact.MODERATE,
            "owner": "Cloud Architecture Team",
            "threat_source": "Human error",
            "vulnerability": "Manual cloud resource configuration",
            "mitigation_strategy": "Implement infrastructure as code and automated scanning"
        },
        {
            "risk_id": "RISK-00005",
            "title": "Business Continuity Disruption",
            "description": "Risk of extended downtime due to disaster",
            "category": RiskCategory.OPERATIONAL,
            "likelihood": RiskLikelihood.RARE,
            "impact": RiskImpact.CATASTROPHIC,
            "owner": "COO",
            "threat_source": "Natural disasters, system failures",
            "vulnerability": "Incomplete disaster recovery plan",
            "mitigation_strategy": "Develop and test comprehensive BCP/DR plans"
        }
    ]
    
    for risk_data in sample_risks:
        risk = Risk(**risk_data)
        risk.calculate_inherent_risk()
        risk.residual_risk_score = risk.inherent_risk_score * 0.6  # Assume 40% mitigation
        db.add(risk)
    
    db.commit()
    print(f"✓ Created {len(sample_risks)} sample risks")


def create_sample_controls(db: Session):
    """Create sample control data"""
    print("Creating sample controls...")
    
    # First ensure frameworks exist
    frameworks = db.query(ControlFramework).all()
    if not frameworks:
        print("  Initializing frameworks first...")
        frameworks_data = [
            {"name": "SOC2", "version": "2017", "description": "SOC 2 Trust Service Criteria"},
            {"name": "NIST CSF", "version": "1.1", "description": "NIST Cybersecurity Framework"},
            {"name": "ISO 27001", "version": "2013", "description": "ISO/IEC 27001:2013"}
        ]
        for fw_data in frameworks_data:
            framework = ControlFramework(**fw_data)
            db.add(framework)
        db.commit()
        frameworks = db.query(ControlFramework).all()
    
    sample_controls = [
        {
            "control_id": "AC-001",
            "title": "Multi-Factor Authentication",
            "description": "Require MFA for all user access to critical systems",
            "control_type": ControlType.PREVENTIVE,
            "status": ControlStatus.IMPLEMENTED,
            "owner": "Security Team",
            "implementation_description": "MFA enforced via SSO provider for all applications",
            "effectiveness_rating": 5,
            "system_orchestration_level": 95
        },
        {
            "control_id": "AC-002",
            "title": "Access Review Process",
            "description": "Quarterly review of user access rights",
            "control_type": ControlType.DETECTIVE,
            "status": ControlStatus.IMPLEMENTED,
            "owner": "IT Operations",
            "implementation_description": "Streamlined quarterly access review workflow",
            "effectiveness_rating": 4,
            "system_orchestration_level": 70
        },
        {
            "control_id": "LOG-001",
            "title": "Security Event Logging",
            "description": "Log all security-relevant events",
            "control_type": ControlType.DETECTIVE,
            "status": ControlStatus.IMPLEMENTED,
            "owner": "Security Operations",
            "implementation_description": "Centralized SIEM solution collecting all logs",
            "effectiveness_rating": 5,
            "system_orchestration_level": 100
        },
        {
            "control_id": "ENC-001",
            "title": "Data Encryption at Rest",
            "description": "Encrypt all sensitive data at rest",
            "control_type": ControlType.PREVENTIVE,
            "status": ControlStatus.IMPLEMENTED,
            "owner": "Data Security Team",
            "implementation_description": "AES-256 encryption for all databases and storage",
            "effectiveness_rating": 5,
            "system_orchestration_level": 100
        },
        {
            "control_id": "BC-001",
            "title": "Backup and Recovery",
            "description": "Regular backups with tested recovery procedures",
            "control_type": ControlType.CORRECTIVE,
            "status": ControlStatus.PARTIALLY_IMPLEMENTED,
            "owner": "Infrastructure Team",
            "implementation_description": "Daily streamlined backups, quarterly recovery tests",
            "effectiveness_rating": 3,
            "system_orchestration_level": 80
        }
    ]
    
    for ctrl_data in sample_controls:
        control = Control(**ctrl_data)
        db.add(control)
    
    db.commit()
    print(f"✓ Created {len(sample_controls)} sample controls")


def create_sample_vendors(db: Session):
    """Create sample vendor data"""
    print("Creating sample vendors...")
    
    sample_vendors = [
        {
            "vendor_id": "VND-00001",
            "name": "CloudStorage Corp",
            "description": "Cloud storage and backup services",
            "status": VendorStatus.ACTIVE,
            "service_type": "Cloud Storage",
            "data_access": True,
            "annual_spend": 150000.00,
            "risk_level": VendorRiskLevel.MEDIUM,
            "risk_score": 45.0,
            "primary_contact_name": "John Smith",
            "primary_contact_email": "john.smith@cloudstorage.example.com"
        },
        {
            "vendor_id": "VND-00002",
            "name": "SecureAuth Solutions",
            "description": "Identity and access management provider",
            "status": VendorStatus.ACTIVE,
            "service_type": "IAM/SSO",
            "data_access": True,
            "annual_spend": 200000.00,
            "risk_level": VendorRiskLevel.LOW,
            "risk_score": 20.0,
            "primary_contact_name": "Sarah Johnson",
            "primary_contact_email": "sarah.j@secureauth.example.com"
        },
        {
            "vendor_id": "VND-00003",
            "name": "DataAnalytics Inc",
            "description": "Business intelligence and analytics platform",
            "status": VendorStatus.ACTIVE,
            "service_type": "Analytics",
            "data_access": True,
            "annual_spend": 500000.00,
            "risk_level": VendorRiskLevel.HIGH,
            "risk_score": 65.0,
            "primary_contact_name": "Michael Chen",
            "primary_contact_email": "m.chen@dataanalytics.example.com"
        }
    ]
    
    for vendor_data in sample_vendors:
        vendor = Vendor(**vendor_data)
        vendor.last_assessment_date = datetime.utcnow() - timedelta(days=180)
        vendor.next_assessment_date = datetime.utcnow() + timedelta(days=185)
        db.add(vendor)
    
    db.commit()
    print(f"✓ Created {len(sample_vendors)} sample vendors")


def create_sample_evidence(db: Session):
    """Create sample evidence data"""
    print("Creating sample evidence...")
    
    sample_evidence = [
        {
            "evidence_id": "EVD-000001",
            "title": "MFA Configuration Screenshot",
            "description": "Screenshot showing MFA enabled for all users",
            "evidence_type": EvidenceType.SCREENSHOT,
            "status": EvidenceStatus.VERIFIED,
            "control_id": "AC-001",
            "framework": "SOC2",
            "collection_method": CollectionMethod.MANUAL,
            "collection_date": datetime.utcnow()
        },
        {
            "evidence_id": "EVD-000002",
            "title": "Access Review Report Q1 2024",
            "description": "Quarterly access review report",
            "evidence_type": EvidenceType.REPORT,
            "status": EvidenceStatus.VERIFIED,
            "control_id": "AC-002",
            "framework": "SOC2",
            "collection_method": CollectionMethod.AUTOMATED,
            "collection_date": datetime.utcnow() - timedelta(days=30)
        },
        {
            "evidence_id": "EVD-000003",
            "title": "SIEM Audit Logs",
            "description": "Security event logs from SIEM",
            "evidence_type": EvidenceType.LOG_FILE,
            "status": EvidenceStatus.COLLECTED,
            "control_id": "LOG-001",
            "framework": "NIST CSF",
            "collection_method": CollectionMethod.API,
            "collection_date": datetime.utcnow()
        }
    ]
    
    for evidence_data in sample_evidence:
        evidence = Evidence(**evidence_data)
        evidence.valid_from = datetime.utcnow()
        evidence.valid_until = datetime.utcnow() + timedelta(days=365)
        db.add(evidence)
    
    db.commit()
    print(f"✓ Created {len(sample_evidence)} sample evidence items")


def main():
    """Main function to populate sample data"""
    print("\n" + "="*50)
    print("GRC Command Center - Sample Data Generator")
    print("="*50 + "\n")
    
    # Create database tables
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Database tables ready\n")
    
    # Create database session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        existing_risks = db.query(Risk).count()
        if existing_risks > 0:
            response = input(f"Database already contains {existing_risks} risks. Continue? (y/n): ")
            if response.lower() != 'y':
                print("Aborted.")
                return
        
        # Create sample data
        create_sample_risks(db)
        create_sample_controls(db)
        create_sample_vendors(db)
        create_sample_evidence(db)
        
        print("\n" + "="*50)
        print("✓ Sample data creation complete!")
        print("="*50)
        print("\nYou can now:")
        print("- View risks at: http://localhost:3000/risks")
        print("- View controls at: http://localhost:3000/controls")
        print("- View vendors at: http://localhost:3000/vendors")
        print("- View evidence at: http://localhost:3000/evidence")
        print("\n")
        
    except Exception as e:
        print(f"\n✗ Error creating sample data: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()