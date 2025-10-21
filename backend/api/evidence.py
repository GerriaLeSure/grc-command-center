from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta
import hashlib
import os

from database import get_db
from models.evidence import Evidence, EvidenceCollection, EvidenceStatus, EvidenceType, CollectionMethod
from schemas.evidence import EvidenceCreate, EvidenceResponse

router = APIRouter()

UPLOAD_DIR = "/workspace/grc-command-center/backend/evidence_storage"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def generate_evidence_id(db: Session) -> str:
    """Generate unique evidence ID"""
    count = db.query(Evidence).count()
    return f"EVD-{count + 1:06d}"


def calculate_file_hash(file_content: bytes) -> str:
    """Calculate SHA-256 hash of file"""
    return hashlib.sha256(file_content).hexdigest()


@router.post("/", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence(evidence: EvidenceCreate, db: Session = Depends(get_db)):
    """Create a new evidence record"""
    db_evidence = Evidence(
        evidence_id=generate_evidence_id(db),
        collection_method=CollectionMethod.MANUAL,
        **evidence.dict()
    )
    
    db.add(db_evidence)
    db.commit()
    db.refresh(db_evidence)
    return db_evidence


@router.post("/upload")
async def upload_evidence(
    file: UploadFile = File(...),
    title: str = "",
    description: str = "",
    evidence_type: EvidenceType = EvidenceType.DOCUMENT,
    control_id: Optional[str] = None,
    framework: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Upload evidence file"""
    try:
        # Read file content
        content = await file.read()
        file_hash = calculate_file_hash(content)
        
        # Save file
        file_path = os.path.join(UPLOAD_DIR, f"{file_hash}_{file.filename}")
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Create evidence record
        evidence = Evidence(
            evidence_id=generate_evidence_id(db),
            title=title or file.filename,
            description=description,
            evidence_type=evidence_type,
            file_name=file.filename,
            file_path=file_path,
            file_size=len(content),
            file_hash=file_hash,
            collection_method=CollectionMethod.MANUAL,
            collection_date=datetime.utcnow(),
            control_id=control_id,
            framework=framework,
            status=EvidenceStatus.COLLECTED
        )
        
        db.add(evidence)
        db.commit()
        db.refresh(evidence)
        
        return {
            "success": True,
            "evidence_id": evidence.evidence_id,
            "file_name": file.filename,
            "file_size": len(content),
            "file_hash": file_hash
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload evidence: {str(e)}")


@router.get("/", response_model=List[EvidenceResponse])
async def get_evidence(
    skip: int = 0,
    limit: int = 100,
    evidence_type: Optional[EvidenceType] = None,
    status: Optional[EvidenceStatus] = None,
    control_id: Optional[str] = None,
    framework: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all evidence with optional filters"""
    query = db.query(Evidence)
    
    if evidence_type:
        query = query.filter(Evidence.evidence_type == evidence_type)
    if status:
        query = query.filter(Evidence.status == status)
    if control_id:
        query = query.filter(Evidence.control_id == control_id)
    if framework:
        query = query.filter(Evidence.framework == framework)
    
    evidence = query.offset(skip).limit(limit).all()
    return evidence


@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence_by_id(evidence_id: str, db: Session = Depends(get_db)):
    """Get specific evidence by ID"""
    evidence = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence


@router.put("/{evidence_id}/verify")
async def verify_evidence(
    evidence_id: str,
    reviewer: str,
    notes: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Verify evidence"""
    evidence = db.query(Evidence).filter(Evidence.evidence_id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    
    evidence.status = EvidenceStatus.VERIFIED
    evidence.reviewed_by = reviewer
    evidence.review_date = datetime.utcnow()
    evidence.review_notes = notes
    
    db.commit()
    
    return {
        "success": True,
        "evidence_id": evidence_id,
        "status": "verified"
    }


@router.post("/collections/", status_code=status.HTTP_201_CREATED)
async def create_evidence_collection(
    name: str,
    description: str,
    collection_type: str,
    source_system: str,
    schedule: str,
    collection_params: dict,
    db: Session = Depends(get_db)
):
    """Create an automated evidence collection job"""
    count = db.query(EvidenceCollection).count()
    collection_id = f"COLL-{count + 1:05d}"
    
    collection = EvidenceCollection(
        collection_id=collection_id,
        name=name,
        description=description,
        collection_type=collection_type,
        source_system=source_system,
        schedule=schedule,
        collection_params=collection_params,
        is_active=True
    )
    
    db.add(collection)
    db.commit()
    db.refresh(collection)
    
    return {
        "success": True,
        "collection_id": collection.collection_id,
        "message": "Evidence collection job created"
    }


@router.get("/collections/")
async def get_evidence_collections(db: Session = Depends(get_db)):
    """Get all evidence collection jobs"""
    collections = db.query(EvidenceCollection).all()
    return [
        {
            "collection_id": c.collection_id,
            "name": c.name,
            "collection_type": c.collection_type,
            "source_system": c.source_system,
            "is_active": c.is_active,
            "last_run": c.last_run,
            "next_run": c.next_run,
            "total_collections": c.total_collections,
            "successful_collections": c.successful_collections
        }
        for c in collections
    ]


@router.get("/analytics/summary")
async def get_evidence_summary(db: Session = Depends(get_db)):
    """Get evidence collection summary"""
    total_evidence = db.query(Evidence).count()
    
    by_status = {}
    for status in EvidenceStatus:
        count = db.query(Evidence).filter(Evidence.status == status).count()
        by_status[status.value] = count
    
    by_type = {}
    for etype in EvidenceType:
        count = db.query(Evidence).filter(Evidence.evidence_type == etype).count()
        by_type[etype.value] = count
    
    # Expiring evidence (next 30 days)
    expiring_soon = db.query(Evidence).filter(
        Evidence.valid_until <= datetime.utcnow() + timedelta(days=30),
        Evidence.valid_until >= datetime.utcnow()
    ).count()
    
    # Evidence by framework
    frameworks = db.query(Evidence.framework).distinct().all()
    by_framework = {}
    for (framework,) in frameworks:
        if framework:
            count = db.query(Evidence).filter(Evidence.framework == framework).count()
            by_framework[framework] = count
    
    return {
        "total_evidence": total_evidence,
        "by_status": by_status,
        "by_type": by_type,
        "expiring_within_30_days": expiring_soon,
        "by_framework": by_framework
    }