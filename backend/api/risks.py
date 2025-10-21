from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import pandas as pd
import io
import json

from database import get_db
from models.risk import Risk, RiskCategory, RiskStatus, RiskLikelihood, RiskImpact
from schemas.risk import (
    RiskCreate, RiskUpdate, RiskResponse, RiskHeatmapData, 
    RiskImportData, RiskExportFilter
)

router = APIRouter()


def generate_risk_id(db: Session) -> str:
    """Generate unique risk ID"""
    count = db.query(Risk).count()
    return f"RISK-{count + 1:05d}"


@router.post("/", response_model=RiskResponse, status_code=status.HTTP_201_CREATED)
async def create_risk(risk: RiskCreate, db: Session = Depends(get_db)):
    """Create a new risk entry"""
    db_risk = Risk(
        risk_id=generate_risk_id(db),
        **risk.dict()
    )
    db_risk.calculate_inherent_risk()
    db_risk.residual_risk_score = db_risk.inherent_risk_score
    
    db.add(db_risk)
    db.commit()
    db.refresh(db_risk)
    return db_risk


@router.get("/", response_model=List[RiskResponse])
async def get_risks(
    skip: int = 0,
    limit: int = 100,
    category: Optional[RiskCategory] = None,
    status: Optional[RiskStatus] = None,
    db: Session = Depends(get_db)
):
    """Get all risks with optional filters"""
    query = db.query(Risk)
    
    if category:
        query = query.filter(Risk.category == category)
    if status:
        query = query.filter(Risk.status == status)
    
    risks = query.offset(skip).limit(limit).all()
    return risks


@router.get("/{risk_id}", response_model=RiskResponse)
async def get_risk(risk_id: str, db: Session = Depends(get_db)):
    """Get a specific risk by ID"""
    risk = db.query(Risk).filter(Risk.risk_id == risk_id).first()
    if not risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    return risk


@router.put("/{risk_id}", response_model=RiskResponse)
async def update_risk(risk_id: str, risk_update: RiskUpdate, db: Session = Depends(get_db)):
    """Update a risk"""
    db_risk = db.query(Risk).filter(Risk.risk_id == risk_id).first()
    if not db_risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    update_data = risk_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_risk, field, value)
    
    # Recalculate risk score if likelihood or impact changed
    if 'likelihood' in update_data or 'impact' in update_data:
        db_risk.calculate_inherent_risk()
    
    db_risk.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(db_risk)
    return db_risk


@router.delete("/{risk_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_risk(risk_id: str, db: Session = Depends(get_db)):
    """Delete a risk"""
    db_risk = db.query(Risk).filter(Risk.risk_id == risk_id).first()
    if not db_risk:
        raise HTTPException(status_code=404, detail="Risk not found")
    
    db.delete(db_risk)
    db.commit()
    return None


@router.get("/analytics/heatmap", response_model=List[RiskHeatmapData])
async def get_risk_heatmap(db: Session = Depends(get_db)):
    """Generate risk heatmap data"""
    risks = db.query(Risk).filter(Risk.status != RiskStatus.CLOSED).all()
    
    heatmap_data = {}
    for risk in risks:
        if risk.likelihood and risk.impact:
            key = (risk.likelihood.value, risk.impact.value)
            if key not in heatmap_data:
                heatmap_data[key] = {
                    "likelihood": risk.likelihood.value,
                    "impact": risk.impact.value,
                    "count": 0,
                    "risk_level": risk.get_risk_level(risk.inherent_risk_score),
                    "risks": []
                }
            heatmap_data[key]["count"] += 1
            heatmap_data[key]["risks"].append(risk.risk_id)
    
    return list(heatmap_data.values())


@router.get("/analytics/statistics")
async def get_risk_statistics(db: Session = Depends(get_db)):
    """Get risk register statistics"""
    total_risks = db.query(Risk).count()
    
    risks_by_status = {}
    for status in RiskStatus:
        count = db.query(Risk).filter(Risk.status == status).count()
        risks_by_status[status.value] = count
    
    risks_by_category = {}
    for category in RiskCategory:
        count = db.query(Risk).filter(Risk.category == category).count()
        risks_by_category[category.value] = count
    
    # Risk level distribution
    all_risks = db.query(Risk).all()
    risk_levels = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for risk in all_risks:
        if risk.inherent_risk_score:
            level = risk.get_risk_level(risk.inherent_risk_score)
            risk_levels[level] += 1
    
    return {
        "total_risks": total_risks,
        "by_status": risks_by_status,
        "by_category": risks_by_category,
        "by_risk_level": risk_levels,
        "average_inherent_score": sum(r.inherent_risk_score or 0 for r in all_risks) / max(len(all_risks), 1),
        "average_residual_score": sum(r.residual_risk_score or 0 for r in all_risks) / max(len(all_risks), 1)
    }


@router.post("/import/excel")
async def import_risks_excel(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Import risks from Excel file"""
    try:
        contents = await file.read()
        df = pd.read_excel(io.BytesIO(contents))
        
        imported_count = 0
        errors = []
        
        for index, row in df.iterrows():
            try:
                risk_data = {
                    "title": row.get("Title"),
                    "description": row.get("Description"),
                    "category": RiskCategory[row.get("Category", "OPERATIONAL").upper()],
                    "likelihood": RiskLikelihood[row.get("Likelihood", "POSSIBLE").upper()],
                    "impact": RiskImpact[row.get("Impact", "MODERATE").upper()],
                    "owner": row.get("Owner"),
                    "threat_source": row.get("Threat Source"),
                    "vulnerability": row.get("Vulnerability"),
                    "mitigation_strategy": row.get("Mitigation Strategy")
                }
                
                db_risk = Risk(risk_id=generate_risk_id(db), **risk_data)
                db_risk.calculate_inherent_risk()
                db_risk.residual_risk_score = db_risk.inherent_risk_score
                
                db.add(db_risk)
                imported_count += 1
            except Exception as e:
                errors.append(f"Row {index + 2}: {str(e)}")
        
        db.commit()
        
        return {
            "success": True,
            "imported_count": imported_count,
            "errors": errors
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to import file: {str(e)}")


@router.post("/export/excel")
async def export_risks_excel(
    filters: Optional[RiskExportFilter] = None,
    db: Session = Depends(get_db)
):
    """Export risks to Excel file"""
    query = db.query(Risk)
    
    if filters:
        if filters.category:
            query = query.filter(Risk.category == filters.category)
        if filters.status:
            query = query.filter(Risk.status == filters.status)
        if filters.min_score:
            query = query.filter(Risk.inherent_risk_score >= filters.min_score)
        if filters.max_score:
            query = query.filter(Risk.inherent_risk_score <= filters.max_score)
    
    risks = query.all()
    
    # Convert to DataFrame
    data = []
    for risk in risks:
        data.append({
            "Risk ID": risk.risk_id,
            "Title": risk.title,
            "Description": risk.description,
            "Category": risk.category.value if risk.category else None,
            "Status": risk.status.value if risk.status else None,
            "Likelihood": risk.likelihood.value if risk.likelihood else None,
            "Impact": risk.impact.value if risk.impact else None,
            "Inherent Risk Score": risk.inherent_risk_score,
            "Residual Risk Score": risk.residual_risk_score,
            "Risk Level": risk.get_risk_level(risk.inherent_risk_score) if risk.inherent_risk_score else None,
            "Owner": risk.owner,
            "Threat Source": risk.threat_source,
            "Vulnerability": risk.vulnerability,
            "Mitigation Strategy": risk.mitigation_strategy,
            "Created At": risk.created_at,
            "Updated At": risk.updated_at
        })
    
    df = pd.DataFrame(data)
    
    # Create Excel file in memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Risk Register')
    output.seek(0)
    
    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=risk_register_{datetime.now().strftime('%Y%m%d')}.xlsx"}
    )