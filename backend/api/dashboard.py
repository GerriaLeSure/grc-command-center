from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from models.risk import Risk, RiskStatus
from models.control import Control, ControlStatus
from models.vendor import Vendor, VendorAssessment, VendorStatus
from models.evidence import Evidence, EvidenceStatus
from models.compliance import ComplianceFramework, ComplianceStatus

router = APIRouter()


@router.get("/overview")
async def get_dashboard_overview(db: Session = Depends(get_db)):
    """Get comprehensive dashboard overview"""
    
    # Risk metrics
    total_risks = db.query(Risk).count()
    open_risks = db.query(Risk).filter(Risk.status == RiskStatus.OPEN).count()
    critical_risks = db.query(Risk).filter(
        Risk.inherent_risk_score >= 15
    ).count()
    
    # Control metrics
    total_controls = db.query(Control).count()
    implemented_controls = db.query(Control).filter(
        Control.status == ControlStatus.IMPLEMENTED
    ).count()
    controls_needing_testing = db.query(Control).filter(
        Control.next_test_date <= datetime.utcnow()
    ).count()
    
    # Vendor metrics
    total_vendors = db.query(Vendor).filter(Vendor.status == VendorStatus.ACTIVE).count()
    high_risk_vendors = db.query(Vendor).filter(
        Vendor.status == VendorStatus.ACTIVE,
        Vendor.risk_score >= 75
    ).count()
    assessments_due = db.query(Vendor).filter(
        Vendor.next_assessment_date <= datetime.utcnow() + timedelta(days=30)
    ).count()
    
    # Evidence metrics
    total_evidence = db.query(Evidence).count()
    verified_evidence = db.query(Evidence).filter(
        Evidence.status == EvidenceStatus.VERIFIED
    ).count()
    expiring_evidence = db.query(Evidence).filter(
        Evidence.valid_until <= datetime.utcnow() + timedelta(days=30),
        Evidence.valid_until >= datetime.utcnow()
    ).count()
    
    # Compliance metrics
    frameworks = db.query(ComplianceFramework).filter(
        ComplianceFramework.is_active == True
    ).all()
    
    avg_compliance = 0.0
    if frameworks:
        avg_compliance = sum(f.overall_compliance_percentage or 0 for f in frameworks) / len(frameworks)
    
    compliance_by_framework = [
        {
            "framework": f.name,
            "percentage": f.overall_compliance_percentage or 0,
            "status": f.status.value if f.status else "In Progress"
        }
        for f in frameworks
    ]
    
    return {
        "summary": {
            "total_risks": total_risks,
            "open_risks": open_risks,
            "critical_risks": critical_risks,
            "total_controls": total_controls,
            "implemented_controls": implemented_controls,
            "total_vendors": total_vendors,
            "high_risk_vendors": high_risk_vendors,
            "total_evidence": total_evidence,
            "verified_evidence": verified_evidence,
            "average_compliance": round(avg_compliance, 2)
        },
        "alerts": {
            "critical_risks": critical_risks,
            "controls_needing_testing": controls_needing_testing,
            "assessments_due_30_days": assessments_due,
            "expiring_evidence": expiring_evidence
        },
        "compliance_by_framework": compliance_by_framework
    }


@router.get("/metrics/trends")
async def get_metrics_trends(days: int = 30, db: Session = Depends(get_db)):
    """Get trend data for the past N days"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Risk trends
    new_risks = db.query(Risk).filter(Risk.created_at >= start_date).count()
    closed_risks = db.query(Risk).filter(
        Risk.status == RiskStatus.CLOSED,
        Risk.updated_at >= start_date
    ).count()
    
    # Control trends
    new_controls = db.query(Control).filter(Control.created_at >= start_date).count()
    
    # Vendor trends
    new_vendors = db.query(Vendor).filter(Vendor.created_at >= start_date).count()
    completed_assessments = db.query(VendorAssessment).filter(
        VendorAssessment.completion_date >= start_date
    ).count()
    
    # Evidence trends
    new_evidence = db.query(Evidence).filter(Evidence.created_at >= start_date).count()
    
    return {
        "period_days": days,
        "start_date": start_date.isoformat(),
        "trends": {
            "risks": {
                "new": new_risks,
                "closed": closed_risks,
                "net_change": new_risks - closed_risks
            },
            "controls": {
                "new": new_controls
            },
            "vendors": {
                "new": new_vendors,
                "assessments_completed": completed_assessments
            },
            "evidence": {
                "new": new_evidence
            }
        }
    }


@router.get("/metrics/kpis")
async def get_key_performance_indicators(db: Session = Depends(get_db)):
    """Get key performance indicators for GRC program"""
    
    # Risk KPIs
    all_risks = db.query(Risk).all()
    avg_inherent_risk = sum(r.inherent_risk_score or 0 for r in all_risks) / max(len(all_risks), 1)
    avg_residual_risk = sum(r.residual_risk_score or 0 for r in all_risks) / max(len(all_risks), 1)
    risk_reduction = ((avg_inherent_risk - avg_residual_risk) / max(avg_inherent_risk, 1)) * 100
    
    # Control KPIs
    total_controls = db.query(Control).count()
    implemented_controls = db.query(Control).filter(
        Control.status == ControlStatus.IMPLEMENTED
    ).count()
    control_implementation_rate = (implemented_controls / max(total_controls, 1)) * 100
    
    orchestrated_controls = db.query(Control).filter(
        Control.system_orchestration_level >= 80
    ).count()
    orchestration_rate = (orchestrated_controls / max(total_controls, 1)) * 100
    
    # Vendor KPIs
    active_vendors = db.query(Vendor).filter(Vendor.status == VendorStatus.ACTIVE).count()
    assessed_this_year = db.query(Vendor).filter(
        Vendor.last_assessment_date >= datetime(datetime.utcnow().year, 1, 1)
    ).count()
    vendor_assessment_rate = (assessed_this_year / max(active_vendors, 1)) * 100
    
    # Compliance KPIs
    frameworks = db.query(ComplianceFramework).filter(
        ComplianceFramework.is_active == True
    ).all()
    avg_compliance = sum(f.overall_compliance_percentage or 0 for f in frameworks) / max(len(frameworks), 1)
    
    # Evidence KPIs
    total_evidence = db.query(Evidence).count()
    verified_evidence = db.query(Evidence).filter(
        Evidence.status == EvidenceStatus.VERIFIED
    ).count()
    evidence_verification_rate = (verified_evidence / max(total_evidence, 1)) * 100
    
    # Calculate time savings (estimated)
    # Before: 3 months = 90 days
    # After: 2 weeks = 14 days
    time_saved_days = 90 - 14
    time_saved_percentage = (time_saved_days / 90) * 100
    
    return {
        "risk_metrics": {
            "average_inherent_risk": round(avg_inherent_risk, 2),
            "average_residual_risk": round(avg_residual_risk, 2),
            "risk_reduction_percentage": round(risk_reduction, 2)
        },
        "control_metrics": {
            "implementation_rate": round(control_implementation_rate, 2),
            "orchestration_rate": round(orchestration_rate, 2),
            "total_controls": total_controls,
            "implemented_controls": implemented_controls
        },
        "vendor_metrics": {
            "total_active_vendors": active_vendors,
            "assessment_rate_ytd": round(vendor_assessment_rate, 2),
            "assessed_this_year": assessed_this_year
        },
        "compliance_metrics": {
            "average_compliance_percentage": round(avg_compliance, 2),
            "active_frameworks": len(frameworks)
        },
        "evidence_metrics": {
            "total_evidence": total_evidence,
            "verification_rate": round(evidence_verification_rate, 2)
        },
        "impact_metrics": {
            "audit_prep_time_saved_days": time_saved_days,
            "audit_prep_efficiency_gain": round(time_saved_percentage, 2),
            "estimated_annual_assessments": 500,
            "estimated_cost_avoidance": "Supports compliance monitoring to prevent penalties"
        }
    }


@router.get("/action-items")
async def get_action_items(db: Session = Depends(get_db)):
    """Get prioritized action items across all GRC areas"""
    action_items = []
    
    # Critical risks
    critical_risks = db.query(Risk).filter(
        Risk.status.in_([RiskStatus.OPEN, RiskStatus.IN_PROGRESS]),
        Risk.inherent_risk_score >= 15
    ).limit(10).all()
    
    for risk in critical_risks:
        action_items.append({
            "type": "Risk",
            "priority": "Critical",
            "id": risk.risk_id,
            "title": f"Address critical risk: {risk.title}",
            "owner": risk.owner,
            "due_date": risk.mitigation_deadline.isoformat() if risk.mitigation_deadline else None
        })
    
    # Controls needing testing
    controls_needing_test = db.query(Control).filter(
        Control.next_test_date <= datetime.utcnow()
    ).limit(10).all()
    
    for control in controls_needing_test:
        action_items.append({
            "type": "Control",
            "priority": "High",
            "id": control.control_id,
            "title": f"Test control: {control.title}",
            "owner": control.owner,
            "due_date": control.next_test_date.isoformat() if control.next_test_date else None
        })
    
    # Upcoming vendor assessments
    upcoming_assessments = db.query(Vendor).filter(
        Vendor.next_assessment_date <= datetime.utcnow() + timedelta(days=30),
        Vendor.status == VendorStatus.ACTIVE
    ).limit(10).all()
    
    for vendor in upcoming_assessments:
        action_items.append({
            "type": "Vendor",
            "priority": "Medium",
            "id": vendor.vendor_id,
            "title": f"Complete vendor assessment: {vendor.name}",
            "owner": vendor.primary_contact_name,
            "due_date": vendor.next_assessment_date.isoformat() if vendor.next_assessment_date else None
        })
    
    # Expiring evidence
    expiring_evidence = db.query(Evidence).filter(
        Evidence.valid_until <= datetime.utcnow() + timedelta(days=30),
        Evidence.valid_until >= datetime.utcnow()
    ).limit(10).all()
    
    for evidence in expiring_evidence:
        action_items.append({
            "type": "Evidence",
            "priority": "Medium",
            "id": evidence.evidence_id,
            "title": f"Renew evidence: {evidence.title}",
            "owner": evidence.collected_by,
            "due_date": evidence.valid_until.isoformat() if evidence.valid_until else None
        })
    
    # Sort by priority and due date
    priority_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3}
    action_items.sort(key=lambda x: (
        priority_order.get(x["priority"], 4),
        x["due_date"] or "9999-12-31"
    ))
    
    return {
        "total_action_items": len(action_items),
        "action_items": action_items[:50]  # Return top 50
    }