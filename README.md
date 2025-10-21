# GRC Command Center

An enterprise-grade Governance, Risk, and Compliance (GRC) platform for integrated risk management, control automation, and vendor assessment.

## Overview
The GRC Command Center centralizes enterprise risk registers, control libraries, compliance frameworks, and vendor risk scoring into one unified environment. Designed for operational resilience, audit readiness, and real-time compliance visibility.

## Key Features
- 📊 **Risk Register** – Quantify, track, and visualize inherent and residual risk.
- 🧩 **Control Library** – Manage framework-aligned controls (SOC 2, NIST, ISO 27001).
- ⚙️ **Compliance Automation** – Monitor control effectiveness and generate reports.
- 🔍 **Vendor Risk** – Score supplier exposure and manage third-party assessments.
- 🧾 **Evidence Management** – Upload, hash, and track compliance evidence.
- 📈 **Dashboards** – Real-time analytics and heatmaps for executives and auditors.

## Technology Stack
- **Backend:** FastAPI + PostgreSQL + Redis + Celery  
- **Frontend:** React.js + Plotly  
- **Infrastructure:** Docker Compose  
- **Auth:** JWT-based RBAC  

## Quick Start
```bash
cp .env.example .env
docker compose up --build
```

Then visit:

API Docs → http://localhost:8000/docs

Frontend → http://localhost:3000

## Author

Developed and documented by Gerria LeSure.