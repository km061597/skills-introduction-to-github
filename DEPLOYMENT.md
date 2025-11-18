# SmartAmazon Production Deployment Guide

Complete guide for deploying SmartAmazon to production environments.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Docker Deployment](#docker-deployment)
- [Kubernetes Deployment](#kubernetes-deployment)
- [CI/CD Deployment](#cicd-deployment)
- [SSL/TLS Configuration](#ssltls-configuration)
- [Monitoring & Logging](#monitoring--logging)
- [Backup & Recovery](#backup--recovery)
- [Scaling](#scaling)
- [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Tools

- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.25+ (for K8s deployment)
- kubectl
- Git

### Optional Tools

- Helm 3+ (for easier K8s deployments)
- cert-manager (for automatic SSL)
- Prometheus & Grafana (for monitoring)
- Sentry (for error tracking)

### Domain & DNS Setup

Ensure you have DNS records configured:

```
smartamazon.com        → A record → Your server IP
www.smartamazon.com    → CNAME → smartamazon.com
api.smartamazon.com    → A record → Your server IP
```

## Docker Deployment

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/smartamazon.git
cd smartamazon
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.production.template .env.production

# Edit with your actual values
nano .env.production
```

**Required Changes:**
- `POSTGRES_PASSWORD` - Strong database password
- `REDIS_PASSWORD` - Strong Redis password
- `SECRET_KEY` - Application secret (generate with `openssl rand -hex 32`)
- `JWT_SECRET_KEY` - JWT secret (generate with `openssl rand -hex 32`)
- `CORS_ORIGINS` - Your actual domain(s)
- `NEXT_PUBLIC_API_URL` - Your API domain
- `NEXT_PUBLIC_URL` - Your frontend domain

### 3. Build Production Images

```bash
# Build backend
cd backend
docker build -f Dockerfile.prod -t smartamazon/backend:latest .

# Build frontend
cd ../frontend
docker build -f Dockerfile.prod -t smartamazon/frontend:latest .
cd ..
```

### 4. Deploy with Docker Compose

```bash
# Load environment variables
export $(cat .env.production | xargs)

# Start services
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### 5. Initialize Database

```bash
# Run migrations
docker-compose -f docker-compose.prod.yml exec backend alembic upgrade head

# Verify
docker-compose -f docker-compose.prod.yml exec backend alembic current
```

### 6. Verify Deployment

```bash
# Health checks
curl http://localhost:8000/health
curl http://localhost:3000/

# API docs
open http://localhost:8000/api/docs
```

## Kubernetes Deployment

### 1. Prerequisites

Ensure you have a Kubernetes cluster:
- AWS EKS
- Google GKE
- Azure AKS
- DigitalOcean Kubernetes
- Self-hosted (kubeadm, k3s)

### 2. Install Required Add-ons

```bash
# Install Nginx Ingress Controller
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.1/deploy/static/provider/cloud/deploy.yaml

# Install cert-manager (for automatic SSL)
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.0/cert-manager.yaml

# Install metrics-server (for HPA)
kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
```

### 3. Create Namespace

```bash
kubectl apply -f k8s/namespace.yaml
```

### 4. Configure Secrets

```bash
# Copy secrets template
cp k8s/secrets.yaml.template k8s/secrets.yaml

# Edit with your actual values
nano k8s/secrets.yaml

# Apply secrets
kubectl apply -f k8s/secrets.yaml
```

### 5. Apply Configuration

```bash
# ConfigMap
kubectl apply -f k8s/configmap.yaml

# Persistent storage
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/redis-deployment.yaml

# Wait for databases to be ready
kubectl wait --for=condition=ready pod -l component=postgres -n smartamazon --timeout=300s
kubectl wait --for=condition=ready pod -l component=redis -n smartamazon --timeout=300s
```

### 6. Deploy Application

```bash
# Backend
kubectl apply -f k8s/backend-deployment.yaml

# Frontend
kubectl apply -f k8s/frontend-deployment.yaml

# Ingress
kubectl apply -f k8s/ingress.yaml

# Wait for deployments
kubectl wait --for=condition=available deployment/smartamazon-backend -n smartamazon --timeout=300s
kubectl wait --for=condition=available deployment/smartamazon-frontend -n smartamazon --timeout=300s
```

### 7. Verify Deployment

```bash
# Check all pods
kubectl get pods -n smartamazon

# Check services
kubectl get services -n smartamazon

# Check ingress
kubectl get ingress -n smartamazon

# View logs
kubectl logs -f deployment/smartamazon-backend -n smartamazon
kubectl logs -f deployment/smartamazon-frontend -n smartamazon
```

### 8. Get External IP

```bash
kubectl get ingress smartamazon-ingress -n smartamazon

# Point your DNS to the EXTERNAL-IP
```

## SSL/TLS Configuration

### Option 1: Let's Encrypt (Automatic)

With cert-manager installed:

```bash
# The ingress.yaml already has cert-manager annotations
# SSL certificates will be automatically provisioned

# Check certificate status
kubectl get certificate -n smartamazon
kubectl describe certificate smartamazon-tls -n smartamazon
```

### Option 2: Manual Certificate

```bash
# Create TLS secret
kubectl create secret tls smartamazon-tls \
  --cert=path/to/fullchain.pem \
  --key=path/to/privkey.pem \
  -n smartamazon
```

### Option 3: Docker Deployment with Certbot

```bash
# Install certbot
sudo apt-get update && sudo apt-get install certbot

# Generate certificate
sudo certbot certonly --standalone -d smartamazon.com -d www.smartamazon.com -d api.smartamazon.com

# Copy certificates to nginx directory
sudo cp /etc/letsencrypt/live/smartamazon.com/fullchain.pem nginx/ssl/
sudo cp /etc/letsencrypt/live/smartamazon.com/privkey.pem nginx/ssl/

# Restart nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

## CI/CD Deployment

### GitHub Actions (Already Configured)

The `.github/workflows/ci-cd.yml` pipeline:

1. **On Push to `main`:**
   - Runs tests
   - Builds Docker images
   - Pushes to registry
   - Deploys to staging

2. **On Tag (v*):**
   - Runs full test suite
   - Builds production images
   - Deploys to production

### Trigger Deployment

```bash
# Create a new release tag
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0

# GitHub Actions will automatically:
# 1. Build and test
# 2. Build Docker images
# 3. Push to registry
# 4. Deploy to production
```

### Manual Deployment

```bash
# Build and push images
docker build -t smartamazon/backend:1.0.0 -f backend/Dockerfile.prod backend/
docker build -t smartamazon/frontend:1.0.0 -f frontend/Dockerfile.prod frontend/

docker push smartamazon/backend:1.0.0
docker push smartamazon/frontend:1.0.0

# Update Kubernetes
kubectl set image deployment/smartamazon-backend backend=smartamazon/backend:1.0.0 -n smartamazon
kubectl set image deployment/smartamazon-frontend frontend=smartamazon/frontend:1.0.0 -n smartamazon

# Monitor rollout
kubectl rollout status deployment/smartamazon-backend -n smartamazon
kubectl rollout status deployment/smartamazon-frontend -n smartamazon
```

## Monitoring & Logging

### Prometheus & Grafana

```bash
# Install kube-prometheus-stack
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false

# Access Grafana
kubectl port-forward -n monitoring svc/prometheus-grafana 3000:80

# Default credentials: admin / prom-operator
```

### Application Metrics

Metrics are exposed at `/metrics` endpoint:

```bash
# Backend metrics
curl http://api.smartamazon.com/metrics

# Prometheus will scrape these automatically
```

### Centralized Logging

```bash
# Install Loki stack for logging
helm repo add grafana https://grafana.github.io/helm-charts
helm install loki grafana/loki-stack \
  --namespace monitoring \
  --set grafana.enabled=true
```

### Error Tracking with Sentry

```bash
# Set SENTRY_DSN in your environment
export SENTRY_DSN=https://xxxxx@sentry.io/xxxxx

# Errors will be automatically reported
```

## Backup & Recovery

### Database Backups

```bash
# Automated backup script
cat > backup-database.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/backups
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="smartamazon_backup_${DATE}.sql"

# Backup
docker-compose -f docker-compose.prod.yml exec -T postgres \
  pg_dump -U postgres smartamazon > "${BACKUP_DIR}/${BACKUP_FILE}"

# Compress
gzip "${BACKUP_DIR}/${BACKUP_FILE}"

# Upload to S3 (optional)
aws s3 cp "${BACKUP_DIR}/${BACKUP_FILE}.gz" s3://smartamazon-backups/

# Clean old backups (keep last 30 days)
find ${BACKUP_DIR} -name "smartamazon_backup_*.sql.gz" -mtime +30 -delete
EOF

chmod +x backup-database.sh
```

### Schedule Backups (Cron)

```bash
# Add to crontab
crontab -e

# Add line: Daily backup at 2 AM
0 2 * * * /path/to/backup-database.sh
```

### Restore from Backup

```bash
# Uncompress backup
gunzip smartamazon_backup_20231215_020000.sql.gz

# Restore
docker-compose -f docker-compose.prod.yml exec -T postgres \
  psql -U postgres smartamazon < smartamazon_backup_20231215_020000.sql
```

## Scaling

### Horizontal Scaling (Kubernetes)

```bash
# Scale backend manually
kubectl scale deployment smartamazon-backend --replicas=5 -n smartamazon

# Scale frontend manually
kubectl scale deployment smartamazon-frontend --replicas=3 -n smartamazon

# HPA is already configured in deployment files
# It will auto-scale based on CPU/memory usage
```

### Vertical Scaling (Resources)

Edit deployment files to increase resources:

```yaml
resources:
  requests:
    memory: "512Mi"
    cpu: "1000m"
  limits:
    memory: "2Gi"
    cpu: "2000m"
```

### Database Scaling

For PostgreSQL:
- Increase `max_connections` in postgres.conf
- Scale vertically (more CPU/RAM)
- Consider read replicas for read-heavy workloads

For Redis:
- Increase `maxmemory` setting
- Use Redis Cluster for horizontal scaling

## Troubleshooting

### Common Issues

**1. Pods Not Starting**

```bash
# Check pod status
kubectl get pods -n smartamazon

# Check pod logs
kubectl logs <pod-name> -n smartamazon

# Describe pod for events
kubectl describe pod <pod-name> -n smartamazon
```

**2. Database Connection Errors**

```bash
# Check database pod
kubectl logs -f deployment/smartamazon-postgres -n smartamazon

# Verify secrets
kubectl get secret smartamazon-secrets -n smartamazon -o yaml

# Test connection manually
kubectl exec -it deployment/smartamazon-backend -n smartamazon -- python -c "from app.database import engine; print(engine.connect())"
```

**3. SSL Certificate Issues**

```bash
# Check certificate status
kubectl describe certificate smartamazon-tls -n smartamazon

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager

# Manual certificate check
openssl s_client -connect smartamazon.com:443 -servername smartamazon.com
```

**4. High Memory Usage**

```bash
# Check resource usage
kubectl top pods -n smartamazon

# Increase pod limits or scale horizontally
```

**5. Slow API Response**

```bash
# Check backend logs
kubectl logs -f deployment/smartamazon-backend -n smartamazon

# Check database performance
kubectl exec -it deployment/smartamazon-postgres -n smartamazon -- psql -U postgres -d smartamazon -c "SELECT * FROM pg_stat_activity;"

# Check Redis cache
kubectl exec -it deployment/smartamazon-redis -n smartamazon -- redis-cli INFO
```

### Health Checks

```bash
# Application health
curl https://smartamazon.com/health
curl https://api.smartamazon.com/health

# Detailed health
curl https://api.smartamazon.com/health/detailed

# Metrics
curl https://api.smartamazon.com/metrics
```

### Rollback Deployment

```bash
# Check rollout history
kubectl rollout history deployment/smartamazon-backend -n smartamazon

# Rollback to previous version
kubectl rollout undo deployment/smartamazon-backend -n smartamazon

# Rollback to specific revision
kubectl rollout undo deployment/smartamazon-backend --to-revision=2 -n smartamazon
```

## Security Checklist

- [ ] All secrets are in environment variables, not code
- [ ] Strong passwords for database and Redis
- [ ] JWT secrets are randomly generated
- [ ] HTTPS/TLS is configured and working
- [ ] CORS is properly configured
- [ ] Rate limiting is enabled
- [ ] Security headers are set (HSTS, CSP, X-Frame-Options)
- [ ] Database backups are automated
- [ ] Error tracking (Sentry) is configured
- [ ] Monitoring (Prometheus/Grafana) is set up
- [ ] Pod Security Policies are configured
- [ ] Network policies are in place
- [ ] Resource limits are set for all pods
- [ ] Non-root users in containers
- [ ] Image vulnerability scanning is enabled

## Post-Deployment

### 1. Verify All Services

```bash
# Frontend
curl -I https://smartamazon.com

# API
curl https://api.smartamazon.com/health

# Database connectivity
curl https://api.smartamazon.com/health/detailed
```

### 2. Set Up Monitoring Alerts

Configure Prometheus alerts for:
- High error rates
- Slow response times
- High resource usage
- Pod restarts
- Certificate expiration

### 3. Load Testing

```bash
# Install k6
curl https://github.com/grafana/k6/releases/download/v0.47.0/k6-v0.47.0-linux-amd64.tar.gz -L | tar xvz

# Run load test
k6 run --vus 100 --duration 5m loadtest.js
```

### 4. Configure CDN (Optional)

For better global performance:
- Cloudflare
- AWS CloudFront
- Fastly

## Support

For issues or questions:
- GitHub Issues: https://github.com/yourusername/smartamazon/issues
- Documentation: https://docs.smartamazon.com
- Email: support@smartamazon.com

---

**Deployment Status:** Production Ready ✅

**Estimated Deployment Time:**
- Docker: ~15 minutes
- Kubernetes: ~30 minutes
- Full CI/CD setup: ~1 hour
