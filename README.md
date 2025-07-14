# Challenge - Currency Exchange Platform

## Overview

Production-ready, scalable USD exchange rate service using Banxico API with **99.95% availability**, sub-200ms latency, and comprehensive fault tolerance. Designed for financial data accuracy with real-time updates and intelligent caching.

---

## API Endpoints

| Endpoint                               | SLA                   | Caching Strategy                           |
| -------------------------------------- | --------------------- | ------------------------------------------ |
| `GET /api/v1/rates/current`            | <100ms, 99.99% uptime | 5min Redis + 1h CDN                        |
| `GET /api/v1/rates/average/{15d,30d}`  | <200ms                | 1h Redis, off-peak calculation             |
| `GET /api/v1/rates/historical?days=10` | <200ms                | 6h Redis (static data)                     |
| `GET /health`                          | <50ms                 | Dependency checks + circuit breaker status |

---

## Infrastructure Architecture

### Core Components

| Component         | Technology            | Specification              | Justification                               |
| ----------------- | --------------------- | -------------------------- | ------------------------------------------- |
| **Compute**       | EC2 Auto Scaling      | t3.medium (2-10 instances) | FastAPI async performance, cost-optimal     |
| **Database**      | Aurora Serverless v2  | 0.5-16 ACUs, MySQL 8.0     | Auto-scaling, 90% cost reduction off-peak   |
| **Cache**         | ElastiCache Redis     | r6g.large Multi-AZ         | Sub-ms latency, 26GB memory                 |
| **Load Balancer** | ALB                   | Cross-zone, health checks  | Layer 7 routing, SSL termination            |
| **CDN**           | CloudFront            | Global edge caching        | 60% origin load reduction                   |

### Architecture Diagram

![Currency Exchange Architecture Diagram](currency_architecture.png)

### Network Layout

```
Internet → CloudFront → WAF → ALB → EC2 (Private) → Aurora/Redis (Isolated)
                                  ↓
                              Lambda (Private) → Banxico API
```

**VPC Design**: 10.0.0.0/16, 3 AZs, public/private/database subnets

---

## SLI / SLO / Error Budget

### Service Level Objectives

| SLO                | Target         | Error Budget          | Business Impact             |
| ------------------ | -------------- | --------------------- | --------------------------- |
| **Availability**   | ≥ 99.95%       | 22 min/month          | \$1,000/min revenue loss    |
| **P95 Latency**    | ≤ 200ms        | 5% slow requests      | User abandonment >300ms     |
| **Data Freshness** | ≤ 5 minutes    | 1% stale events       | Financial accuracy critical |
| **Throughput**     | 5,000 RPS peak | Handle traffic spikes | Market event capacity       |

### Error Budget Policy

* **0-50% consumed**: Normal operations
* **50-75% consumed**: Freeze non-critical changes
* **75-100% consumed**: Emergency fixes only

---

## Fault Tolerance & Resilience

### Circuit Breaker (Banxico API)

* **Failure Threshold**: 3 consecutive failures → OPEN state
* **Recovery**: 60s timeout → HALF\_OPEN test → CLOSED
* **Fallback**: Serve cached data with staleness warning
* **Monitoring**: SNS alerts on state changes

### Graceful Degradation Levels

1. **Healthy**: Real-time data, full features
2. **Degraded**: Cached data with warnings
3. **Limited**: Historical data only
4. **Critical**: Static fallback page

### Redis Fallback

* If Redis becomes unavailable, EC2 falls back to Aurora with increased TTLs.
* Alerts are triggered for degraded cache performance.

---

## Auto Scaling Strategy

### EC2 Auto Scaling

* **Baseline**: 2 instances (1 per AZ minimum)
* **Scale Out**: ALB RequestCountPerTarget >50 → +2 instances
* **Scale In**: CPU <30% for 10min → -1 instance
* **Emergency**: P95 latency >500ms → +3 instances
* **Max Capacity**: 10 instances

### Aurora Serverless v2

* **Cost Mode**: 0.5 ACU (low traffic)
* **Normal Load**: 2-4 ACU (1K-2K RPS)
* **Peak Traffic**: 8-16 ACU (economic events)

---

## FastAPI Performance

### Optimizations

* **Connection Pooling**: 20 connections per instance
* **Async Endpoints**: `asyncio.gather()` for parallel DB/cache calls
* **Response Compression**: Gzip middleware (>1KB)
* **Workers**: 4 Gunicorn + Uvicorn per instance
* **Tracing**: OpenTelemetry with trace propagation via headers

### Health Check Response

```json
{
  "status": "healthy|degraded|unhealthy",
  "dependencies": {
    "database": "healthy",
    "redis": "healthy",
    "banxico_api": "degraded",
    "circuit_breaker": "half_open"
  },
  "performance": {
    "response_time_p95": 145,
    "cache_hit_ratio": 0.94
  }
}
```

---

## Observability

### Key Metrics

* **Response Time**: P95/P99 latency tracking
* **Error Budget**: Real-time burn rate monitoring
* **Cache Performance**: Hit ratio, memory utilization
* **Circuit Breaker**: State changes and failure counts
* **Data Quality**: Banxico sync success rate

### Monitoring Stack

* **CloudWatch**: 15 custom alarms, 7-day log retention
* **X-Ray**: 10% sampling for cost efficiency
* **Dashboards**: Executive (SLO), Operational (health), SRE (detailed)

---

## Incident Response

### Automated Runbooks

**High Latency (P95 >200ms)**:

1. Trigger emergency auto-scaling
2. Check Aurora connection pool utilization
3. Clear Redis cache if hit ratio <80%

**Banxico API Failure**:

1. Circuit breaker → cached data mode
2. Set degraded service status
3. Monitor error budget burn rate

**Database Issues**:

1. Scale Aurora ACUs to maximum
2. Enable read replica routing
3. Increase cache TTL to 30 minutes

---

## Capacity Planning

### Growth Projections

| Timeframe     | Traffic          | Scaling Response                 |
| ------------- | ---------------- | -------------------------------- |
| **Current**   | 2K RPS baseline  | 2 EC2 instances, 2 ACU           |
| **6 months**  | 6K RPS sustained | Auto-scale to 6 instances, 8 ACU |
| **12 months** | 20K RPS peak     | 10 instances, 16 ACU max         |

### Traffic Spike Scenarios

* **Economic Announcements**: 10x traffic → Emergency scaling
* **Market Volatility**: 5x sustained → Gradual scaling
* **Media Coverage**: 20x sudden spike → Circuit breaker protection

---

## Disaster Recovery

### Recovery Targets

* **RTO**: 15 minutes (Multi-AZ auto-failover)
* **RPO**: 5 minutes (Aurora continuous backup)
* **Availability**: 3 AZ deployment, cross-zone load balancing

### DR Testing

* **Monthly**: AZ failure simulation
* **Quarterly**: Complete service failure test

---

## Security

* **Network**: VPC isolation, security groups (least privilege)
* **Encryption**: TLS, Aurora/Redis encryption at rest
* **Secrets**: AWS Secrets Manager for API keys, DB credentials
* **WAF**: DDoS protection, rate limiting (1000 RPS/IP)
* **Auditing**: CloudTrail enabled for sensitive actions
* **Scanning**: Amazon Inspector for EC2 vulnerability detection (optional)

---

## Key Assumptions

* **Banxico API**: 1000 req/day limit, 7AM-5PM Mexico time
* **Traffic Pattern**: 80% Mexico/LATAM, 20% global
* **Data Retention**: 2 years for compliance
* **Peak Multiplier**: 10x during economic events
* **Infra Provisioning**: Terraform or CloudFormation, not AWS CDK

---

## Deliverables

### Phase 1: Documentation

* [x] Architecture design with SLO/SLI definitions
* [x] Fault tolerance and incident response strategy
* [x] Cost optimization and capacity planning

### Phase 2: Infrastructure (Terraform or CloudFormation)

* [ ] VPC, EC2, Aurora, Redis, ALB components
* [ ] Auto-scaling, monitoring, security configurations

### Phase 3: Application (FastAPI)

* [ ] Async API with Redis caching
* [ ] Circuit breaker and health check implementation
* [ ] Comprehensive observability integration

---

> **Production-Ready**: Enterprise-grade architecture following AWS Well-Architected Framework with focus on reliability, performance, and cost optimization for financial data services.
