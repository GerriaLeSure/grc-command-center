# GRC Command Center - Deployment Guide

## Quick Start with Docker Compose

### 1. Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- 4GB RAM minimum
- 10GB disk space

### 2. Initial Setup

```bash
# Clone the repository
git clone <repository-url>
cd grc-command-center

# Create environment file
cp backend/.env.example backend/.env

# Edit the .env file with your settings
nano backend/.env
```

### 3. Start the Application

```bash
# Build and start all services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

### 4. Initialize Data

```bash
# Initialize compliance frameworks
curl -X POST http://localhost:8000/api/compliance/frameworks/initialize

# Initialize control frameworks
curl -X POST http://localhost:8000/api/controls/frameworks/initialize
```

### 5. Access the Application

- **Frontend Dashboard**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **PostgreSQL**: localhost:5432 (user: grc_user, password: grc_password)

## Production Deployment

### Option 1: AWS Deployment

#### Using AWS ECS + RDS

```bash
# 1. Set up RDS PostgreSQL instance
aws rds create-db-instance \
  --db-instance-identifier grc-postgres \
  --db-instance-class db.t3.medium \
  --engine postgres \
  --master-username grcadmin \
  --master-user-password <your-password> \
  --allocated-storage 100

# 2. Create ECR repositories
aws ecr create-repository --repository-name grc-backend
aws ecr create-repository --repository-name grc-frontend

# 3. Build and push images
$(aws ecr get-login --no-include-email)
docker build -t grc-backend ./backend
docker tag grc-backend:latest <account-id>.dkr.ecr.<region>.amazonaws.com/grc-backend:latest
docker push <account-id>.dkr.ecr.<region>.amazonaws.com/grc-backend:latest

# 4. Create ECS cluster and task definitions
# Use the provided ecs-task-definition.json
aws ecs create-cluster --cluster-name grc-cluster

# 5. Deploy services
aws ecs create-service \
  --cluster grc-cluster \
  --service-name grc-backend \
  --task-definition grc-backend \
  --desired-count 2 \
  --load-balancer targetGroupArn=<tg-arn>,containerName=backend,containerPort=8000
```

#### Using AWS App Runner (Simpler)

```bash
# 1. Push to ECR (as above)

# 2. Create App Runner service via console or CLI
aws apprunner create-service \
  --service-name grc-backend \
  --source-configuration '{
    "ImageRepository": {
      "ImageIdentifier": "<ecr-image-uri>",
      "ImageRepositoryType": "ECR"
    },
    "AutoDeploymentsEnabled": true
  }'
```

### Option 2: Azure Deployment

```bash
# 1. Create Azure Container Registry
az acr create --resource-group grc-rg --name grcregistry --sku Basic

# 2. Build and push
az acr build --registry grcregistry --image grc-backend:latest ./backend

# 3. Create Azure Database for PostgreSQL
az postgres server create \
  --resource-group grc-rg \
  --name grc-postgres \
  --admin-user grcadmin \
  --admin-password <password> \
  --sku-name B_Gen5_2

# 4. Deploy to Azure Container Instances or App Service
az container create \
  --resource-group grc-rg \
  --name grc-backend \
  --image grcregistry.azurecr.io/grc-backend:latest \
  --dns-name-label grc-backend \
  --ports 8000
```

### Option 3: Google Cloud Platform

```bash
# 1. Build and push to GCR
gcloud builds submit --tag gcr.io/<project-id>/grc-backend ./backend

# 2. Create Cloud SQL PostgreSQL instance
gcloud sql instances create grc-postgres \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=us-central1

# 3. Deploy to Cloud Run
gcloud run deploy grc-backend \
  --image gcr.io/<project-id>/grc-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 4: Kubernetes Deployment

```yaml
# kubernetes/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: grc-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: grc-backend
  template:
    metadata:
      labels:
        app: grc-backend
    spec:
      containers:
      - name: backend
        image: <your-registry>/grc-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: POSTGRES_HOST
          value: postgres-service
        - name: POSTGRES_PASSWORD
          valueFrom:
            secretKeyRef:
              name: grc-secrets
              key: postgres-password
---
apiVersion: v1
kind: Service
metadata:
  name: grc-backend-service
spec:
  type: LoadBalancer
  ports:
  - port: 80
    targetPort: 8000
  selector:
    app: grc-backend
```

```bash
# Deploy to Kubernetes
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/postgres.yaml
kubectl apply -f kubernetes/frontend.yaml
```

## Environment Variables for Production

### Backend (.env)

```env
# Application
APP_NAME=GRC Command Center
DEBUG=False

# Database
DATABASE_TYPE=postgresql
POSTGRES_USER=grcadmin
POSTGRES_PASSWORD=<strong-password>
POSTGRES_HOST=<rds-endpoint or cloud-sql-proxy>
POSTGRES_PORT=5432
POSTGRES_DB=grc_production

# Security - IMPORTANT: Generate strong secrets
SECRET_KEY=<generate-with: openssl rand -hex 32>
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS - Update with your domain
ALLOWED_ORIGINS=https://grc.yourdomain.com,https://app.yourdomain.com

# AWS (if using AWS integrations)
AWS_ACCESS_KEY_ID=<your-key>
AWS_SECRET_ACCESS_KEY=<your-secret>
AWS_REGION=us-east-1

# ServiceNow
SERVICENOW_INSTANCE=<your-instance>
SERVICENOW_USERNAME=<username>
SERVICENOW_PASSWORD=<password>

# Jira
JIRA_URL=https://your-domain.atlassian.net
JIRA_USERNAME=<email>
JIRA_API_TOKEN=<token>

# Redis (use managed Redis in production)
REDIS_URL=redis://<elasticache-endpoint>:6379/0
```

## SSL/TLS Configuration

### Using Let's Encrypt with Nginx

```nginx
# Add to docker-compose.yml
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - /etc/letsencrypt:/etc/letsencrypt
    depends_on:
      - frontend
      - backend

  certbot:
    image: certbot/certbot
    volumes:
      - /etc/letsencrypt:/etc/letsencrypt
      - /var/www/certbot:/var/www/certbot
    entrypoint: "/bin/sh -c 'trap exit TERM; while :; do certbot renew; sleep 12h & wait $${!}; done;'"
```

```bash
# Obtain certificate
docker-compose run --rm certbot certonly --webroot -w /var/www/certbot -d grc.yourdomain.com
```

## Database Backup

### Automated PostgreSQL Backups

```bash
# Create backup script
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)
docker-compose exec -T postgres pg_dump -U grc_user grc_db | gzip > $BACKUP_DIR/grc_backup_$DATE.sql.gz
find $BACKUP_DIR -name "grc_backup_*.sql.gz" -mtime +7 -delete
EOF

chmod +x backup.sh

# Add to crontab (daily at 2 AM)
0 2 * * * /path/to/backup.sh
```

### Restore from Backup

```bash
# Restore database
gunzip -c grc_backup_20240101_020000.sql.gz | docker-compose exec -T postgres psql -U grc_user grc_db
```

## Monitoring Setup

### Using Prometheus + Grafana

```yaml
# Add to docker-compose.yml
  prometheus:
    image: prom/prometheus
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
    ports:
      - "9090:9090"

  grafana:
    image: grafana/grafana
    ports:
      - "3001:3000"
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=admin
    depends_on:
      - prometheus
```

## Health Checks

```bash
# Backend health
curl http://localhost:8000/health

# Expected response:
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "version": "1.0.0"
}
```

## Performance Tuning

### PostgreSQL Configuration

```sql
-- In postgresql.conf
max_connections = 200
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
work_mem = 2621kB
min_wal_size = 1GB
max_wal_size = 4GB
```

### Backend Optimization

```python
# Update in main.py
uvicorn.run(
    "main:app",
    host="0.0.0.0",
    port=8000,
    workers=4,  # Number of worker processes
    loop="uvloop",  # Faster event loop
    limit_concurrency=1000,
    limit_max_requests=10000
)
```

## Scaling Strategies

### Horizontal Scaling
- Run multiple backend instances behind a load balancer
- Use session affinity or stateless authentication
- Share Redis cache across instances

### Vertical Scaling
- Increase container resources (CPU/Memory)
- Optimize database queries
- Use connection pooling

### Database Scaling
- Enable read replicas for reporting
- Implement caching (Redis)
- Use partitioning for large tables

## Security Checklist

- [ ] Change all default passwords
- [ ] Use strong SECRET_KEY
- [ ] Enable HTTPS/TLS
- [ ] Implement rate limiting
- [ ] Set up WAF (Web Application Firewall)
- [ ] Enable database encryption at rest
- [ ] Use secrets management (AWS Secrets Manager, Azure Key Vault)
- [ ] Implement proper CORS policies
- [ ] Enable audit logging
- [ ] Set up automated security scanning
- [ ] Implement IP whitelisting for admin endpoints
- [ ] Use multi-factor authentication

## Troubleshooting

### Backend won't start
```bash
# Check logs
docker-compose logs backend

# Common issues:
# - Database connection failed: Check POSTGRES_HOST and credentials
# - Port already in use: Change port in docker-compose.yml
# - Missing dependencies: Rebuild image
```

### Frontend can't connect to backend
```bash
# Check CORS settings in backend/.env
# Verify nginx proxy configuration
# Check network connectivity
docker-compose exec frontend ping backend
```

### Database migration issues
```bash
# Reset database (CAUTION: destroys data)
docker-compose down -v
docker-compose up -d postgres
docker-compose up -d backend
```

## Maintenance

### Update Application
```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose down
docker-compose build
docker-compose up -d

# Run migrations if needed
docker-compose exec backend alembic upgrade head
```

### Monitor Disk Space
```bash
# Check Docker disk usage
docker system df

# Clean up
docker system prune -a
```

## Support

For deployment issues:
1. Check logs: `docker-compose logs -f`
2. Verify environment variables
3. Check database connectivity
4. Review documentation
5. Contact support team

---

**Remember**: Always test deployments in a staging environment first!