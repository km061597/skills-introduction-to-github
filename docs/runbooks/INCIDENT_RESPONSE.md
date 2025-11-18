# SmartAmazon Incident Response Runbook

## Overview

This runbook provides step-by-step procedures for responding to common incidents in the SmartAmazon platform.

## Incident Severity Levels

| Level | Description | Response Time | Example |
|-------|-------------|---------------|---------|
| **P1 - Critical** | Complete service outage | < 15 minutes | API down, database unavailable |
| **P2 - High** | Major degradation | < 1 hour | High latency, partial outage |
| **P3 - Medium** | Minor degradation | < 4 hours | Single feature broken |
| **P4 - Low** | Cosmetic issues | < 24 hours | UI glitch, typo |

## General Incident Response Process

1. **Detect** - Alert triggered or issue reported
2. **Assess** - Determine severity and impact
3. **Communicate** - Notify stakeholders
4. **Investigate** - Find root cause
5. **Mitigate** - Implement temporary fix if needed
6. **Resolve** - Implement permanent fix
7. **Document** - Post-mortem and lessons learned

---

## Common Incidents

### 1. API Service Down (P1)

**Symptoms:**
- API health check failing
- 503 Service Unavailable errors
- No response from backend

**Investigation Steps:**
```bash
# Check if container is running
docker ps | grep smartamazon-api

# Check container logs
docker logs smartamazon-api-prod --tail 100

# Check health endpoint
curl -v http://localhost:8000/health

# Check resource usage
docker stats smartamazon-api-prod
```

**Common Causes & Solutions:**

#### A. Container Crashed
```bash
# Restart container
docker-compose restart backend

# Or if using Kubernetes
kubectl rollout restart deployment/smartamazon-backend
```

#### B. Database Connection Lost
```bash
# Check database connectivity
docker exec smartamazon-api-prod pg_isready -h postgres -p 5432

# Restart database if needed
docker-compose restart postgres
```

#### C. Out of Memory
```bash
# Check memory usage
docker stats --no-stream smartamazon-api-prod

# Increase memory limits in docker-compose.yml
# Or scale horizontally in Kubernetes
kubectl scale deployment smartamazon-backend --replicas=3
```

**Escalation:**
- If not resolved in 15 minutes → Page senior engineer
- If not resolved in 30 minutes → Engage CTO

---

### 2. High API Latency (P2)

**Symptoms:**
- Response times > 2 seconds
- Slow queries in logs
- User complaints about slowness

**Investigation Steps:**
```bash
# Check API performance metrics
curl http://localhost:8000/metrics | grep http_request_duration

# Check database queries
docker exec smartamazon-db psql -U postgres -d smartamazon -c "
SELECT pid, now() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active'
ORDER BY duration DESC
LIMIT 10;"

# Check Redis latency
redis-cli --latency-history
```

**Common Causes & Solutions:**

#### A. Database Slow Queries
```bash
# Identify slow queries
docker logs smartamazon-api-prod | grep "slow query"

# Add missing indexes
docker exec smartamazon-db psql -U postgres -d smartamazon -c "
CREATE INDEX IF NOT EXISTS idx_products_category_rating ON products(category, rating);"
```

#### B. Redis Cache Miss
```bash
# Check cache hit rate
redis-cli INFO stats | grep keyspace

# Warm up cache
curl http://localhost:8000/api/search?q=protein
curl http://localhost:8000/api/categories
```

#### C. High Load
```bash
# Scale horizontally
docker-compose up -d --scale backend=3

# Or in Kubernetes
kubectl scale deployment smartamazon-backend --replicas=5
```

---

### 3. Database Connection Pool Exhausted (P1)

**Symptoms:**
- "connection pool exhausted" errors
- API timeouts
- Database refusing connections

**Investigation Steps:**
```bash
# Check active connections
docker exec smartamazon-db psql -U postgres -d smartamazon -c "
SELECT count(*) FROM pg_stat_activity WHERE datname='smartamazon';"

# Check max connections
docker exec smartamazon-db psql -U postgres -c "SHOW max_connections;"
```

**Solutions:**
```bash
# Kill idle connections
docker exec smartamazon-db psql -U postgres -d smartamazon -c "
SELECT pg_terminate_backend(pid)
FROM pg_stat_activity
WHERE datname='smartamazon'
AND state='idle'
AND query_start < now() - interval '5 minutes';"

# Increase max connections (requires restart)
# Edit postgresql.conf: max_connections = 200
docker-compose restart postgres

# Restart API to clear connection pool
docker-compose restart backend
```

---

### 4. Disk Space Full (P1)

**Symptoms:**
- "No space left on device" errors
- Services failing to start
- Unable to write logs

**Investigation Steps:**
```bash
# Check disk usage
df -h

# Find large files
du -sh /* | sort -hr | head -20

# Check Docker volumes
docker system df
```

**Solutions:**
```bash
# Clean up Docker
docker system prune -af --volumes  # CAREFUL: removes unused data

# Remove old logs
find /var/log -name "*.log" -mtime +30 -delete

# Remove old backups
find /var/backups/smartamazon -name "*.sql.gz" -mtime +30 -delete

# Add more disk space (cloud provider specific)
# AWS: Increase EBS volume size
# Azure: Increase disk size
# Then resize filesystem: resize2fs /dev/xvda1
```

---

### 5. Redis Memory Full (P2)

**Symptoms:**
- "OOM command not allowed" errors
- Cache misses increasing
- API performance degradation

**Investigation Steps:**
```bash
# Check Redis memory usage
redis-cli INFO memory

# Check eviction stats
redis-cli INFO stats | grep evicted
```

**Solutions:**
```bash
# Flush old cache data
redis-cli FLUSHDB

# Increase Redis memory limit
# Edit docker-compose.yml: --maxmemory 1024mb
docker-compose restart redis

# Review cache strategy (TTL, eviction policy)
```

---

### 6. Failed Deployment (P2)

**Symptoms:**
- New version not starting
- Health checks failing after deployment
- Rollback needed

**Investigation Steps:**
```bash
# Check deployment logs
docker logs smartamazon-api-prod --tail 200

# Check image version
docker inspect smartamazon-api-prod | grep Image

# Check environment variables
docker inspect smartamazon-api-prod | grep -A 20 Env
```

**Solutions:**
```bash
# Rollback to previous version
docker-compose down
docker-compose up -d

# Or in Kubernetes
kubectl rollout undo deployment/smartamazon-backend

# Check rollback status
kubectl rollout status deployment/smartamazon-backend
```

---

## Emergency Contacts

| Role | Name | Contact | Escalation |
|------|------|---------|------------|
| On-Call Engineer | Rotation | PagerDuty | Primary |
| Senior Engineer | TBD | TBD | 15 min |
| DevOps Lead | TBD | TBD | 30 min |
| CTO | TBD | TBD | 1 hour |

## Post-Incident Checklist

After resolving an incident:

- [ ] Update status page
- [ ] Notify stakeholders of resolution
- [ ] Document timeline in incident tracker
- [ ] Schedule post-mortem meeting (within 48 hours for P1/P2)
- [ ] Create tickets for permanent fixes
- [ ] Update runbook with learnings

## Post-Mortem Template

```markdown
# Incident Post-Mortem

**Date:** YYYY-MM-DD
**Severity:** P1/P2/P3/P4
**Duration:** X hours
**Impact:** X users affected

## Timeline
- HH:MM - Incident detected
- HH:MM - Investigation started
- HH:MM - Root cause identified
- HH:MM - Mitigation applied
- HH:MM - Incident resolved

## Root Cause
[Detailed explanation]

## Resolution
[What was done to fix it]

## Action Items
1. [ ] Action item 1 - Owner - Due date
2. [ ] Action item 2 - Owner - Due date

## Lessons Learned
- What went well
- What didn't go well
- What we'll do differently next time
```

---

**Last Updated:** 2025-01-18
**Version:** 1.0
**Maintained By:** DevOps Team
