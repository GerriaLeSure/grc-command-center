from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.compliance import ComplianceFramework, ComplianceRequirement, ComplianceStatus
from schemas.compliance import ComplianceFrameworkResponse, ComplianceRequirementResponse, ComplianceDashboardData

router = APIRouter()


@router.post("/frameworks/initialize")
async def initialize_compliance_frameworks(db: Session = Depends(get_db)):
    """Initialize standard compliance frameworks"""
    frameworks_data = [
        {
            "framework_id": "SOC2",
            "name": "SOC 2 Type II",
            "version": "2017",
            "description": "Service Organization Control 2 - Security, Availability, Processing Integrity, Confidentiality, Privacy"
        },
        {
            "framework_id": "NIST-CSF",
            "name": "NIST Cybersecurity Framework",
            "version": "1.1",
            "description": "National Institute of Standards and Technology Cybersecurity Framework"
        },
        {
            "framework_id": "ISO-27001",
            "name": "ISO/IEC 27001",
            "version": "2013",
            "description": "Information Security Management System Standard"
        },
        {
            "framework_id": "GDPR",
            "name": "General Data Protection Regulation",
            "version": "2016",
            "description": "EU Data Protection Regulation"
        },
        {
            "framework_id": "HIPAA",
            "name": "HIPAA",
            "version": "1996",
            "description": "Health Insurance Portability and Accountability Act"
        }
    ]
    
    created = []
    for framework_data in frameworks_data:
        existing = db.query(ComplianceFramework).filter(
            ComplianceFramework.framework_id == framework_data["framework_id"]
        ).first()
        
        if not existing:
            framework = ComplianceFramework(**framework_data)
            db.add(framework)
            created.append(framework_data["name"])
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Initialized frameworks: {', '.join(created) if created else 'All frameworks already exist'}"
    }


@router.get("/frameworks/", response_model=List[ComplianceFrameworkResponse])
async def get_compliance_frameworks(
    is_active: bool = True,
    db: Session = Depends(get_db)
):
    """Get all compliance frameworks"""
    query = db.query(ComplianceFramework)
    if is_active is not None:
        query = query.filter(ComplianceFramework.is_active == is_active)
    
    frameworks = query.all()
    return frameworks


@router.get("/frameworks/{framework_id}", response_model=ComplianceFrameworkResponse)
async def get_compliance_framework(framework_id: str, db: Session = Depends(get_db)):
    """Get specific compliance framework"""
    framework = db.query(ComplianceFramework).filter(
        ComplianceFramework.framework_id == framework_id
    ).first()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    return framework


@router.get("/frameworks/{framework_id}/requirements", response_model=List[ComplianceRequirementResponse])
async def get_framework_requirements(framework_id: str, db: Session = Depends(get_db)):
    """Get all requirements for a framework"""
    framework = db.query(ComplianceFramework).filter(
        ComplianceFramework.framework_id == framework_id
    ).first()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    requirements = db.query(ComplianceRequirement).filter(
        ComplianceRequirement.framework_id == framework.id
    ).all()
    
    return requirements


@router.put("/frameworks/{framework_id}/calculate")
async def calculate_framework_compliance(framework_id: str, db: Session = Depends(get_db)):
    """Calculate compliance percentage for a framework"""
    framework = db.query(ComplianceFramework).filter(
        ComplianceFramework.framework_id == framework_id
    ).first()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    requirements = db.query(ComplianceRequirement).filter(
        ComplianceRequirement.framework_id == framework.id
    ).all()
    
    total = len(requirements)
    compliant = sum(1 for r in requirements if r.status == ComplianceStatus.COMPLIANT)
    partially_compliant = sum(1 for r in requirements if r.status == ComplianceStatus.PARTIALLY_COMPLIANT)
    non_compliant = sum(1 for r in requirements if r.status == ComplianceStatus.NON_COMPLIANT)
    
    # Calculate weighted compliance percentage
    compliance_percentage = 0.0
    if total > 0:
        compliance_percentage = (
            (compliant * 100 + partially_compliant * 50) / total
        )
    
    # Update framework
    framework.total_requirements = total
    framework.compliant_requirements = compliant
    framework.partially_compliant_requirements = partially_compliant
    framework.non_compliant_requirements = non_compliant
    framework.overall_compliance_percentage = compliance_percentage
    
    # Set status based on compliance
    if compliance_percentage >= 95:
        framework.status = ComplianceStatus.COMPLIANT
    elif compliance_percentage >= 70:
        framework.status = ComplianceStatus.PARTIALLY_COMPLIANT
    else:
        framework.status = ComplianceStatus.NON_COMPLIANT
    
    framework.updated_at = datetime.utcnow()
    db.commit()
    
    return {
        "framework": framework_id,
        "compliance_percentage": compliance_percentage,
        "status": framework.status.value,
        "total_requirements": total,
        "compliant": compliant,
        "partially_compliant": partially_compliant,
        "non_compliant": non_compliant
    }


@router.post("/requirements/")
async def create_requirement(
    framework_id: str,
    requirement_id: str,
    title: str,
    description: str,
    category: str,
    owner: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a compliance requirement"""
    framework = db.query(ComplianceFramework).filter(
        ComplianceFramework.framework_id == framework_id
    ).first()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    requirement = ComplianceRequirement(
        framework_id=framework.id,
        requirement_id=requirement_id,
        title=title,
        description=description,
        category=category,
        owner=owner,
        status=ComplianceStatus.IN_PROGRESS,
        compliance_percentage=0.0
    )
    
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    
    return {
        "success": True,
        "requirement_id": requirement.requirement_id,
        "framework": framework_id
    }


@router.put("/requirements/{requirement_id}")
async def update_requirement_status(
    requirement_id: str,
    status: ComplianceStatus,
    compliance_percentage: float,
    implementation_notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Update compliance requirement status"""
    requirement = db.query(ComplianceRequirement).filter(
        ComplianceRequirement.requirement_id == requirement_id
    ).first()
    if not requirement:
        raise HTTPException(status_code=404, detail="Requirement not found")
    
    requirement.status = status
    requirement.compliance_percentage = compliance_percentage
    if implementation_notes:
        requirement.implementation_notes = implementation_notes
    requirement.updated_at = datetime.utcnow()
    
    db.commit()
    
    return {
        "success": True,
        "requirement_id": requirement_id,
        "status": status.value,
        "compliance_percentage": compliance_percentage
    }


@router.get("/dashboard", response_model=List[ComplianceDashboardData])
async def get_compliance_dashboard(db: Session = Depends(get_db)):
    """Get compliance dashboard data for all frameworks"""
    frameworks = db.query(ComplianceFramework).filter(
        ComplianceFramework.is_active == True
    ).all()
    
    dashboard_data = []
    for framework in frameworks:
        # Get critical gaps (non-compliant high priority requirements)
        critical_gaps = db.query(ComplianceRequirement).filter(
            ComplianceRequirement.framework_id == framework.id,
            ComplianceRequirement.status == ComplianceStatus.NON_COMPLIANT,
            ComplianceRequirement.priority >= 8
        ).all()
        
        dashboard_data.append(
            ComplianceDashboardData(
                framework_name=framework.name,
                compliance_percentage=framework.overall_compliance_percentage or 0.0,
                status=framework.status.value if framework.status else "In Progress",
                compliant_count=framework.compliant_requirements or 0,
                total_count=framework.total_requirements or 0,
                critical_gaps=[f"{gap.requirement_id}: {gap.title}" for gap in critical_gaps[:5]]
            )
        )
    
    return dashboard_data


@router.get("/analytics/gap-analysis/{framework_id}")
async def get_gap_analysis(framework_id: str, db: Session = Depends(get_db)):
    """Get gap analysis for a framework"""
    framework = db.query(ComplianceFramework).filter(
        ComplianceFramework.framework_id == framework_id
    ).first()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    
    requirements = db.query(ComplianceRequirement).filter(
        ComplianceRequirement.framework_id == framework.id
    ).all()
    
    gaps = []
    for req in requirements:
        if req.status in [ComplianceStatus.NON_COMPLIANT, ComplianceStatus.PARTIALLY_COMPLIANT]:
            gaps.append({
                "requirement_id": req.requirement_id,
                "title": req.title,
                "category": req.category,
                "status": req.status.value,
                "compliance_percentage": req.compliance_percentage,
                "priority": req.priority,
                "owner": req.owner,
                "remediation_plan": req.remediation_plan,
                "remediation_deadline": req.remediation_deadline.isoformat() if req.remediation_deadline else None
            })
    
    # Sort by priority
    gaps.sort(key=lambda x: x["priority"], reverse=True)
    
    return {
        "framework": framework_id,
        "total_gaps": len(gaps),
        "gaps": gaps
    }