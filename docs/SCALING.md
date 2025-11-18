# SmartAmazon Scaling Guide

## Overview

This guide covers horizontal and vertical scaling strategies for the SmartAmazon platform.

## Table of Contents

- [Horizontal Pod Autoscaling (HPA)](#horizontal-pod-autoscaling)
- [Vertical Pod Autoscaling (VPA)](#vertical-pod-autoscaling)
- [Manual Scaling](#manual-scaling)
- [Load Testing](#load-testing)
- [Monitoring Scaling](#monitoring-scaling)

---

## Horizontal Pod Autoscaling (HPA)

HPA automatically scales the number of pod replicas based on observed metrics.

### Backend API Scaling

The backend API scales based on:
- **CPU**: Target 70% utilization
- **Memory**: Target 80% utilization
- **Request Rate**: Target 1000 req/s per pod

**Configuration:** `k8s/hpa-backend.yaml`

**Scaling Behavior:**
- **Min Replicas:** 2 (always at least 2 for high availability)
- **Max Replicas:** 10
- **Scale Up:** Immediate, can add up to 4 pods at once
- **Scale Down:** 5-minute stabilization, max 2 pods at once

**Apply HPA:**
```bash
kubectl apply -f k8s/hpa-backend.yaml
```

**Monitor Scaling:**
```bash
# Watch HPA status
kubectl get hpa smartamazon-backend-hpa -n smartamazon -w

# View detailed metrics
kubectl describe hpa smartamazon-backend-hpa -n smartamazon
```

### Frontend Scaling

The frontend scales based on:
- **CPU**: Target 70% utilization
- **Memory**: Target 80% utilization

**Configuration:** `k8s/hpa-frontend.yaml`

**Scaling Behavior:**
- **Min Replicas:** 2
- **Max Replicas:** 8
- Similar scale-up/scale-down policies as backend

**Apply HPA:**
```bash
kubectl apply -f k8s/hpa-frontend.yaml
```

---

## Vertical Pod Autoscaling (VPA)

VPA automatically adjusts CPU and memory requests/limits based on usage.

### When to Use VPA

- **Right-sizing:** Automatically adjust resource allocations
- **New Applications:** Don't know optimal resource requirements
- **Variable Workloads:** Resource needs change over time

**Configuration:** `k8s/vpa-backend.yaml`

**Resource Limits:**
- **Min:** 100m CPU, 128Mi memory
- **Max:** 2000m CPU (2 cores), 2Gi memory

**Apply VPA:**
```bash
kubectl apply -f k8s/vpa-backend.yaml
```

**Check Recommendations:**
```bash
kubectl get vpa smartamazon-backend-vpa -n smartamazon -o yaml
```

### VPA vs HPA

| Feature | HPA | VPA |
|---------|-----|-----|
| Scales | Pod count | Pod resources |
| Best For | Stateless apps | Stateful apps |
| Response Time | Fast (seconds) | Slow (requires pod restart) |
| Use With | High traffic variance | Resource optimization |

**Note:** VPA and HPA can be used together, but avoid HPA on CPU/memory if using VPA.

---

## Manual Scaling

### Docker Compose

**Scale Backend:**
```bash
docker-compose up -d --scale backend=3
```

**Scale Frontend:**
```bash
docker-compose up -d --scale frontend=2
```

**Check Status:**
```bash
docker-compose ps
```

### Kubernetes

**Scale Backend:**
```bash
kubectl scale deployment smartamazon-backend --replicas=5 -n smartamazon
```

**Scale Frontend:**
```bash
kubectl scale deployment smartamazon-frontend --replicas=3 -n smartamazon
```

**Check Status:**
```bash
kubectl get pods -n smartamazon -l app=smartamazon-backend
```

---

## Load Testing for Scaling Validation

### Test Scaling Behavior

1. **Baseline Load Test:**
```bash
k6 run --vus 10 --duration 2m scripts/load-test/load-test.js
```

2. **Trigger Scale-Up:**
```bash
# Gradually increase load
k6 run --stage 2m:50,5m:100,5m:200,2m:50 scripts/load-test/load-test.js
```

3. **Watch Pods Scale:**
```bash
watch kubectl get pods -n smartamazon
watch kubectl get hpa -n smartamazon
```

4. **Monitor Metrics:**
```bash
# Open Grafana
open http://localhost:3001

# Or check Prometheus
open http://localhost:9090/graph
```

### Validate Scale-Down

1. **Stop Load Test**

2. **Wait for Stabilization (5 minutes)**

3. **Watch Pods Scale Down:**
```bash
watch kubectl get pods -n smartamazon
```

### Performance Benchmarks

Expected performance per pod:
- **Backend Pod:**
  - 1000 req/s sustained
  - 95th percentile latency < 200ms
  - CPU: ~50-70% at 1000 req/s

- **Frontend Pod:**
  - 500 req/s sustained
  - CPU: ~40-60% at 500 req/s

---

## Monitoring Scaling

### Key Metrics to Watch

1. **Pod Count:**
```bash
kubectl get hpa -n smartamazon
```

2. **Resource Utilization:**
```bash
kubectl top pods -n smartamazon
kubectl top nodes
```

3. **Request Rate:**
```bash
# Prometheus query
rate(http_requests_total[1m])
```

4. **Latency:**
```bash
# Prometheus query
histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m]))
```

### Grafana Dashboards

Import dashboards for:
- **Kubernetes Cluster Monitoring:** Dashboard ID 6417
- **Pod Monitoring:** Dashboard ID 6879
- **HPA Monitoring:** Dashboard ID 12114

**Import Command:**
```bash
# Using grafana-cli
grafana-cli plugins install grafana-kubernetes-app
```

### Alerting Rules

Scaling-related alerts (configured in `config/prometheus/alerts.yml`):

1. **HPA at Max Replicas:**
```yaml
- alert: HPAMaxedOut
  expr: kube_hpa_status_current_replicas >= kube_hpa_spec_max_replicas
  for: 15m
  labels:
    severity: warning
  annotations:
    summary: "HPA has reached maximum replicas"
```

2. **Frequent Scaling:**
```yaml
- alert: FrequentScaling
  expr: changes(kube_hpa_status_current_replicas[30m]) > 10
  labels:
    severity: info
  annotations:
    summary: "HPA is scaling frequently (> 10 changes in 30m)"
```

---

## Capacity Planning

### Calculate Max Capacity

**With Current Settings:**
- **Backend:** 10 pods × 1000 req/s = 10,000 req/s
- **Frontend:** 8 pods × 500 req/s = 4,000 req/s
- **Database:** Single instance (bottleneck)

**Recommendations:**
1. **For 20,000 req/s:** Increase backend maxReplicas to 20
2. **For 50,000 req/s:** Consider database read replicas
3. **For 100,000+ req/s:** Multi-region deployment

### Cost Optimization

**Current Monthly Cost (AWS EKS example):**
- **Min:** 2 backend + 2 frontend = 4 pods × $0.10/hour = $288/month
- **Peak:** 10 backend + 8 frontend = 18 pods × $0.10/hour = $1,296/month

**Optimization Strategies:**
1. **Spot Instances:** Save 60-90% on pod costs
2. **Reserved Instances:** Save 30-40% for baseline pods
3. **Off-Peak Scaling:** Reduce min replicas during low traffic

---

## Troubleshooting Scaling Issues

### Pod Won't Scale Up

**Check:**
```bash
# HPA status
kubectl describe hpa smartamazon-backend-hpa -n smartamazon

# Metrics availability
kubectl get --raw /apis/metrics.k8s.io/v1beta1/pods

# Resource limits
kubectl describe deployment smartamazon-backend -n smartamazon
```

**Common Issues:**
1. **Metrics Server Not Running:** `kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml`
2. **Resource Limits Too Low:** Increase limits in deployment
3. **Cluster Capacity:** Check node capacity

### Pod Won't Scale Down

**Check:**
```bash
# Current utilization
kubectl top pods -n smartamazon

# HPA configuration
kubectl get hpa smartamazon-backend-hpa -n smartamazon -o yaml
```

**Common Issues:**
1. **Stabilization Window:** Wait 5 minutes
2. **Min Replicas:** Can't scale below minReplicas
3. **High Utilization:** Pods still under load

### Pods Thrashing (Rapid Scale Up/Down)

**Solutions:**
1. **Increase stabilization window**
2. **Adjust target utilization thresholds**
3. **Review workload patterns**

---

## Best Practices

1. ✅ **Always Set Resource Requests/Limits** - HPA needs these to work
2. ✅ **Start Conservative** - Begin with higher targets (70-80%)
3. ✅ **Test Thoroughly** - Load test before production
4. ✅ **Monitor Closely** - Watch for thrashing or maxed-out HPAs
5. ✅ **Plan for Peak** - Know your max capacity
6. ✅ **Use PodDisruptionBudgets** - Ensure availability during scaling
7. ✅ **Set Appropriate Stabilization** - Prevent rapid scaling
8. ✅ **Have Min 2 Replicas** - For high availability

---

## Additional Resources

- [Kubernetes HPA Documentation](https://kubernetes.io/docs/tasks/run-application/horizontal-pod-autoscale/)
- [VPA Documentation](https://github.com/kubernetes/autoscaler/tree/master/vertical-pod-autoscaler)
- [k6 Load Testing](https://k6.io/docs/)
- [Prometheus Monitoring](https://prometheus.io/docs/)

---

**Last Updated:** 2025-01-18
**Maintained By:** DevOps Team
