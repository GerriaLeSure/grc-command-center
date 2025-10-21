from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Optional, List
import boto3
from jira import JIRA
import httpx

from database import get_db
from config import settings
from models.risk import Risk, RiskCategory, RiskLikelihood, RiskImpact
from models.evidence import Evidence, EvidenceType, CollectionMethod, EvidenceStatus
from datetime import datetime

router = APIRouter()


@router.get("/aws/security-hub/findings")
async def get_aws_security_hub_findings(
    severity: Optional[str] = None,
    limit: int = 100
):
    """Fetch findings from AWS Security Hub"""
    try:
        if not settings.AWS_ACCESS_KEY_ID:
            raise HTTPException(status_code=400, detail="AWS credentials not configured")
        
        client = boto3.client(
            'securityhub',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        filters = {}
        if severity:
            filters['SeverityLabel'] = [{'Value': severity, 'Comparison': 'EQUALS'}]
        
        response = client.get_findings(
            Filters=filters,
            MaxResults=limit
        )
        
        findings = response.get('Findings', [])
        
        return {
            "success": True,
            "count": len(findings),
            "findings": [
                {
                    "id": f.get('Id'),
                    "title": f.get('Title'),
                    "description": f.get('Description'),
                    "severity": f.get('Severity', {}).get('Label'),
                    "resource_type": f.get('Resources', [{}])[0].get('Type') if f.get('Resources') else None,
                    "compliance_status": f.get('Compliance', {}).get('Status'),
                    "created_at": f.get('CreatedAt')
                }
                for f in findings
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch AWS Security Hub findings: {str(e)}")


@router.post("/aws/security-hub/import-risks")
async def import_aws_findings_as_risks(
    severity_filter: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Import AWS Security Hub findings as risks"""
    try:
        if not settings.AWS_ACCESS_KEY_ID:
            raise HTTPException(status_code=400, detail="AWS credentials not configured")
        
        client = boto3.client(
            'securityhub',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION
        )
        
        filters = {}
        if severity_filter:
            filters['SeverityLabel'] = [{'Value': severity_filter, 'Comparison': 'EQUALS'}]
        
        response = client.get_findings(Filters=filters, MaxResults=100)
        findings = response.get('Findings', [])
        
        imported_count = 0
        for finding in findings:
            severity = finding.get('Severity', {}).get('Label', 'MEDIUM')
            
            # Map severity to likelihood and impact
            severity_map = {
                'CRITICAL': (RiskLikelihood.ALMOST_CERTAIN, RiskImpact.CATASTROPHIC),
                'HIGH': (RiskLikelihood.LIKELY, RiskImpact.MAJOR),
                'MEDIUM': (RiskLikelihood.POSSIBLE, RiskImpact.MODERATE),
                'LOW': (RiskLikelihood.UNLIKELY, RiskImpact.MINOR)
            }
            
            likelihood, impact = severity_map.get(severity, (RiskLikelihood.POSSIBLE, RiskImpact.MODERATE))
            
            # Check if risk already exists
            aws_id = finding.get('Id')
            existing_risk = db.query(Risk).filter(Risk.custom_fields.contains({"aws_finding_id": aws_id})).first()
            
            if not existing_risk:
                count = db.query(Risk).count()
                risk = Risk(
                    risk_id=f"AWS-{count + 1:05d}",
                    title=finding.get('Title', 'AWS Security Finding'),
                    description=finding.get('Description'),
                    category=RiskCategory.TECHNOLOGY,
                    likelihood=likelihood,
                    impact=impact,
                    threat_source="AWS Security Hub",
                    custom_fields={"aws_finding_id": aws_id, "aws_severity": severity}
                )
                risk.calculate_inherent_risk()
                risk.residual_risk_score = risk.inherent_risk_score
                
                db.add(risk)
                imported_count += 1
        
        db.commit()
        
        return {
            "success": True,
            "findings_processed": len(findings),
            "risks_imported": imported_count
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to import AWS findings: {str(e)}")


@router.get("/jira/issues")
async def get_jira_issues(project: Optional[str] = None):
    """Fetch issues from Jira"""
    try:
        if not settings.JIRA_URL or not settings.JIRA_API_TOKEN:
            raise HTTPException(status_code=400, detail="Jira credentials not configured")
        
        jira = JIRA(
            server=settings.JIRA_URL,
            basic_auth=(settings.JIRA_USERNAME, settings.JIRA_API_TOKEN)
        )
        
        jql = f"project = {project}" if project else "labels = 'grc' OR labels = 'compliance' OR labels = 'security'"
        issues = jira.search_issues(jql, maxResults=100)
        
        return {
            "success": True,
            "count": len(issues),
            "issues": [
                {
                    "key": issue.key,
                    "summary": issue.fields.summary,
                    "status": issue.fields.status.name,
                    "priority": issue.fields.priority.name if issue.fields.priority else None,
                    "created": issue.fields.created,
                    "assignee": issue.fields.assignee.displayName if issue.fields.assignee else None
                }
                for issue in issues
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch Jira issues: {str(e)}")


@router.post("/jira/create-issue")
async def create_jira_issue(
    project: str,
    summary: str,
    description: str,
    issue_type: str = "Task",
    labels: List[str] = ["grc"]
):
    """Create a Jira issue"""
    try:
        if not settings.JIRA_URL or not settings.JIRA_API_TOKEN:
            raise HTTPException(status_code=400, detail="Jira credentials not configured")
        
        jira = JIRA(
            server=settings.JIRA_URL,
            basic_auth=(settings.JIRA_USERNAME, settings.JIRA_API_TOKEN)
        )
        
        issue_dict = {
            'project': {'key': project},
            'summary': summary,
            'description': description,
            'issuetype': {'name': issue_type},
            'labels': labels
        }
        
        new_issue = jira.create_issue(fields=issue_dict)
        
        return {
            "success": True,
            "issue_key": new_issue.key,
            "issue_url": f"{settings.JIRA_URL}/browse/{new_issue.key}"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create Jira issue: {str(e)}")


@router.get("/servicenow/incidents")
async def get_servicenow_incidents():
    """Fetch incidents from ServiceNow"""
    try:
        if not settings.SERVICENOW_INSTANCE:
            raise HTTPException(status_code=400, detail="ServiceNow credentials not configured")
        
        url = f"https://{settings.SERVICENOW_INSTANCE}.service-now.com/api/now/table/incident"
        params = {
            'sysparm_limit': 100,
            'sysparm_query': 'active=true^category=security'
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                params=params,
                auth=(settings.SERVICENOW_USERNAME, settings.SERVICENOW_PASSWORD),
                headers={'Accept': 'application/json'}
            )
            
            if response.status_code != 200:
                raise HTTPException(status_code=response.status_code, detail="ServiceNow API error")
            
            data = response.json()
            incidents = data.get('result', [])
            
            return {
                "success": True,
                "count": len(incidents),
                "incidents": [
                    {
                        "number": inc.get('number'),
                        "short_description": inc.get('short_description'),
                        "state": inc.get('state'),
                        "priority": inc.get('priority'),
                        "category": inc.get('category'),
                        "opened_at": inc.get('opened_at')
                    }
                    for inc in incidents
                ]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ServiceNow incidents: {str(e)}")


@router.post("/servicenow/create-incident")
async def create_servicenow_incident(
    short_description: str,
    description: str,
    category: str = "security",
    priority: str = "3"
):
    """Create a ServiceNow incident"""
    try:
        if not settings.SERVICENOW_INSTANCE:
            raise HTTPException(status_code=400, detail="ServiceNow credentials not configured")
        
        url = f"https://{settings.SERVICENOW_INSTANCE}.service-now.com/api/now/table/incident"
        
        payload = {
            'short_description': short_description,
            'description': description,
            'category': category,
            'priority': priority
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                url,
                json=payload,
                auth=(settings.SERVICENOW_USERNAME, settings.SERVICENOW_PASSWORD),
                headers={'Content-Type': 'application/json', 'Accept': 'application/json'}
            )
            
            if response.status_code != 201:
                raise HTTPException(status_code=response.status_code, detail="ServiceNow API error")
            
            data = response.json()
            incident = data.get('result', {})
            
            return {
                "success": True,
                "incident_number": incident.get('number'),
                "sys_id": incident.get('sys_id')
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ServiceNow incident: {str(e)}")


@router.get("/health")
async def check_integrations_health():
    """Check health of all integrations"""
    health_status = {
        "aws": {"configured": bool(settings.AWS_ACCESS_KEY_ID), "status": "unknown"},
        "jira": {"configured": bool(settings.JIRA_URL and settings.JIRA_API_TOKEN), "status": "unknown"},
        "servicenow": {"configured": bool(settings.SERVICENOW_INSTANCE), "status": "unknown"}
    }
    
    # Test AWS
    if health_status["aws"]["configured"]:
        try:
            client = boto3.client(
                'sts',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_REGION
            )
            client.get_caller_identity()
            health_status["aws"]["status"] = "healthy"
        except:
            health_status["aws"]["status"] = "error"
    
    # Test Jira
    if health_status["jira"]["configured"]:
        try:
            jira = JIRA(
                server=settings.JIRA_URL,
                basic_auth=(settings.JIRA_USERNAME, settings.JIRA_API_TOKEN)
            )
            jira.myself()
            health_status["jira"]["status"] = "healthy"
        except:
            health_status["jira"]["status"] = "error"
    
    return health_status