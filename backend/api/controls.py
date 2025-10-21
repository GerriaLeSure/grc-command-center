from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models.control import Control, ControlFramework, ControlMapping, ControlStatus
from schemas.control import ControlCreate, ControlUpdate, ControlResponse, ControlFrameworkResponse

router = APIRouter()


def generate_control_id(db: Session, framework: str = "GEN") -> str:
    """Generate unique control ID"""
    count = db.query(Control).count()
    return f"{framework}-{count + 1:04d}"


@router.post("/", response_model=ControlResponse, status_code=status.HTTP_201_CREATED)
async def create_control(control: ControlCreate, db: Session = Depends(get_db)):
    """Create a new control"""
    db_control = Control(
        control_id=generate_control_id(db),
        **control.dict()
    )
    
    db.add(db_control)
    db.commit()
    db.refresh(db_control)
    return db_control


@router.get("/", response_model=List[ControlResponse])
async def get_controls(
    skip: int = 0,
    limit: int = 100,
    status: Optional[ControlStatus] = None,
    db: Session = Depends(get_db)
):
    """Get all controls with optional filters"""
    query = db.query(Control)
    
    if status:
        query = query.filter(Control.status == status)
    
    controls = query.offset(skip).limit(limit).all()
    return controls


@router.get("/{control_id}", response_model=ControlResponse)
async def get_control(control_id: str, db: Session = Depends(get_db)):
    """Get a specific control by ID"""
    control = db.query(Control).filter(Control.control_id == control_id).first()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    return control


@router.put("/{control_id}", response_model=ControlResponse)
async def update_control(
    control_id: str,
    control_update: ControlUpdate,
    db: Session = Depends(get_db)
):
    """Update a control"""
    db_control = db.query(Control).filter(Control.control_id == control_id).first()
    if not db_control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    update_data = control_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_control, field, value)
    
    db_control.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_control)
    return db_control


@router.get("/frameworks/", response_model=List[ControlFrameworkResponse])
async def get_frameworks(db: Session = Depends(get_db)):
    """Get all control frameworks"""
    frameworks = db.query(ControlFramework).all()
    return frameworks


@router.post("/frameworks/initialize")
async def initialize_frameworks(db: Session = Depends(get_db)):
    """Initialize standard control frameworks (SOC2, NIST, ISO)"""
    frameworks_data = [
        {
            "name": "SOC2",
            "version": "2017",
            "description": "SOC 2 Trust Service Criteria"
        },
        {
            "name": "NIST CSF",
            "version": "1.1",
            "description": "NIST Cybersecurity Framework"
        },
        {
            "name": "ISO 27001",
            "version": "2013",
            "description": "ISO/IEC 27001:2013 Information Security Management"
        }
    ]
    
    created = []
    for framework_data in frameworks_data:
        existing = db.query(ControlFramework).filter(
            ControlFramework.name == framework_data["name"]
        ).first()
        
        if not existing:
            framework = ControlFramework(**framework_data)
            db.add(framework)
            created.append(framework_data["name"])
    
    db.commit()
    
    return {
        "success": True,
        "message": f"Initialized frameworks: {', '.join(created) if created else 'All frameworks already exist'}"
    }


@router.get("/mappings/{control_id}")
async def get_control_mappings(control_id: str, db: Session = Depends(get_db)):
    """Get framework mappings for a control"""
    control = db.query(Control).filter(Control.control_id == control_id).first()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    
    mappings = db.query(ControlMapping).filter(
        ControlMapping.control_id == control.id
    ).all()
    
    return {
        "control_id": control_id,
        "mappings": [
            {
                "framework": mapping.framework.name,
                "framework_control_id": mapping.framework_control_id,
                "status": mapping.compliance_status.value if mapping.compliance_status else None
            }
            for mapping in mappings
        ]
    }


@router.get("/analytics/coverage")
async def get_control_coverage(db: Session = Depends(get_db)):
    """Get control coverage analytics"""
    total_controls = db.query(Control).count()
    
    coverage_by_status = {}
    for status in ControlStatus:
        count = db.query(Control).filter(Control.status == status).count()
        coverage_by_status[status.value] = {
            "count": count,
            "percentage": (count / total_controls * 100) if total_controls > 0 else 0
        }
    
    # Framework coverage
    frameworks = db.query(ControlFramework).all()
    framework_coverage = []
    
    for framework in frameworks:
        total_mappings = db.query(ControlMapping).filter(
            ControlMapping.framework_id == framework.id
        ).count()
        
        implemented_mappings = db.query(ControlMapping).filter(
            ControlMapping.framework_id == framework.id,
            ControlMapping.compliance_status == ControlStatus.IMPLEMENTED
        ).count()
        
        framework_coverage.append({
            "framework": framework.name,
            "total_controls": total_mappings,
            "implemented": implemented_mappings,
            "coverage_percentage": (implemented_mappings / total_mappings * 100) if total_mappings > 0 else 0
        })
    
    return {
        "total_controls": total_controls,
        "by_status": coverage_by_status,
        "by_framework": framework_coverage
    }