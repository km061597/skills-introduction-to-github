# Load Testing for SmartAmazon

## Overview

This directory contains load testing scripts for the SmartAmazon platform using [k6](https://k6.io/).

## Installation

### Install k6

**macOS:**
```bash
brew install k6
```

**Linux:**
```bash
sudo gpg -k
sudo gpg --no-default-keyring --keyring /usr/share/keyrings/k6-archive-keyring.gpg --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys C5AD17C747E3415A3642D57D77C6C491D6AC1D69
echo "deb [signed-by=/usr/share/keyrings/k6-archive-keyring.gpg] https://dl.k6.io/deb stable main" | sudo tee /etc/apt/sources.list.d/k6.list
sudo apt-get update
sudo apt-get install k6
```

**Windows:**
```powershell
choco install k6
```

Or download from: https://k6.io/docs/getting-started/installation/

## Running Load Tests

### Basic Test
```bash
k6 run load-test.js
```

### Test Against Specific Environment
```bash
# Local
k6 run load-test.js

# Staging
API_URL=https://api-staging.smartamazon.com k6 run load-test.js

# Production (be careful!)
API_URL=https://api.smartamazon.com k6 run load-test.js
```

### Custom Test Configurations

#### Quick Smoke Test (10 VUs for 1 minute)
```bash
k6 run --vus 10 --duration 1m load-test.js
```

#### Stress Test (Ramp up to 500 users)
```bash
k6 run --stage 5m:100,5m:200,5m:500 load-test.js
```

#### Spike Test (Sudden traffic surge)
```bash
k6 run --stage 1m:10,30s:500,2m:500,1m:10 load-test.js
```

#### Endurance Test (Sustained load)
```bash
k6 run --vus 50 --duration 30m load-test.js
```

## Test Scenarios

The load test includes the following scenarios:

1. **Search Products** - Simulates users searching for products
2. **Product Details** - Simulates viewing individual product pages
3. **Advanced Filtering** - Tests filtering and sorting functionality
4. **Metadata Endpoints** - Tests categories and brands endpoints

## Performance Thresholds

Current thresholds:
- 95th percentile response time < 2 seconds
- Error rate < 5%
- Application error rate < 10%

## Interpreting Results

After the test completes, k6 outputs:

```
✓ status is 200
✓ response has results
✓ response time < 2s

checks.........................: 95.00% ✓ 2850 ✗ 150
data_received..................: 12 MB  200 kB/s
data_sent......................: 2.4 MB 40 kB/s
http_req_duration..............: avg=450ms  min=120ms med=380ms max=2.1s p(95)=1.2s p(99)=1.8s
http_reqs......................: 3000   50/s
vus............................: 100    min=0    max=100
```

### Key Metrics:
- **checks**: Percentage of successful assertions
- **http_req_duration**: Response time statistics
- **http_reqs**: Total requests and requests per second
- **vus**: Number of virtual users

## Analyzing Bottlenecks

If tests reveal performance issues:

1. **High Database Latency**
   - Check slow query logs
   - Add missing indexes
   - Optimize queries

2. **High Memory Usage**
   - Review cache configuration
   - Check for memory leaks
   - Increase container resources

3. **CPU Bottleneck**
   - Scale horizontally (add more replicas)
   - Optimize CPU-intensive operations
   - Enable caching

4. **Connection Pool Exhaustion**
   - Increase database connection limits
   - Optimize connection pooling
   - Check for connection leaks

## Cloud Load Testing

For larger-scale tests, use k6 Cloud:

```bash
# Login to k6 Cloud
k6 login cloud

# Run test in the cloud
k6 cloud load-test.js
```

## Continuous Load Testing

Integrate load tests into CI/CD:

```yaml
# .github/workflows/load-test.yml
name: Load Test

on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

jobs:
  load-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Install k6
        run: |
          wget https://github.com/grafana/k6/releases/download/v0.45.0/k6-v0.45.0-linux-amd64.tar.gz
          tar -xzf k6-v0.45.0-linux-amd64.tar.gz
          sudo mv k6-v0.45.0-linux-amd64/k6 /usr/local/bin/
      - name: Run load test
        run: k6 run scripts/load-test/load-test.js
```

## Best Practices

1. **Start Small** - Begin with low VU counts and gradually increase
2. **Test Realistic Scenarios** - Match production traffic patterns
3. **Monitor During Tests** - Watch system metrics (CPU, memory, DB)
4. **Run Regularly** - Catch performance regressions early
5. **Test Before Major Releases** - Validate performance before deployment

## References

- [k6 Documentation](https://k6.io/docs/)
- [k6 Test Authoring Guide](https://k6.io/docs/using-k6/test-authoring/)
- [k6 Thresholds](https://k6.io/docs/using-k6/thresholds/)
