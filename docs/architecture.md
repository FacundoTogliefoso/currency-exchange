# Architecture Documentation

## System Overview

Production-ready USD/MXN exchange rate platform with 99.95% availability, sub-200ms latency, and intelligent caching.

```
Internet → CloudFront → WAF → ALB → EC2 (FastAPI) → Redis → Aurora → Banxico API
                                 ↓
                            CloudWatch (Monitoring)
```

## Core Components

### API Layer
- **FastAPI 0.111.0** with async/await throughout
- **EC2 t3.medium** instances in Auto Scaling Group (2-10)
- **Endpoints**: `/rates/current`, `/rates/historical`, `/rates/average`, `/health`

### Caching Strategy
- **ElastiCache Redis r6g.large** with Multi-AZ failover
- **TTL Strategy**: Current (5min), Historical (1h), Average (30min)
- **Cache hit ratio target**: >90%

### Database
- **Aurora Serverless v2** MySQL-compatible (0.5-16 ACUs)
- **Multi-AZ** with 2 read replicas for HA
- **Backup**: Continuous with 35-day retention

### External Integration
- **Banxico API**: Official Banco de México rates (SF43718 series)
- **Circuit Breaker**: 3 failures → OPEN, 30s timeout, graceful fallback
- **Rate Limits**: 200 req/5min, 10,000/day

## Architecture Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | FastAPI | Native async, 3x I/O performance, auto docs |
| Database | Aurora Serverless v2 | Auto-scaling, 90% cost savings, Multi-AZ |
| Cache | ElastiCache Redis | Sub-ms latency, TTL management, cost-effective |
| Region | us-west-1 | Customer requirement, closer to Mexico |
| Fault Tolerance | Circuit Breaker | Financial data reliability, graceful degradation |

## Data Flow

### Normal Operation
1. **Request** → Check Redis cache
2. **Cache Hit** → Return data (5ms)
3. **Cache Miss** → Fetch from Banxico API
4. **Store** → Redis (with TTL) + Aurora (persistence)
5. **Response** → Return to user

### Fault Tolerance
1. **Banxico API fails** → Circuit breaker opens → Serve cached data
2. **Redis fails** → Serve from Aurora database
3. **All fail** → Return 503 with retry-after header

## Scalability & Performance

### Auto Scaling
- **Horizontal**: EC2 ASG scales 2-10 instances based on 50 req/instance
- **Vertical**: Aurora scales 0.5-16 ACUs automatically
- **Geographic**: CloudFront CDN with global edge locations

### SLO Targets
- **Availability**: 99.95% (22 min downtime/month)
- **Latency**: P95 < 200ms, P99 < 500ms
- **Throughput**: 5,000 RPS sustained
- **Data Freshness**: <5 minutes during market hours

## Security

### Network
- **VPC**: Multi-AZ with public/private/database subnets
- **WAF**: DDoS protection, rate limiting, geo-blocking
- **TLS 1.3**: End-to-end encryption

### Application
- **Secrets Manager**: API tokens and database credentials
- **IAM Roles**: Least-privilege access
- **VPC Flow Logs**: Network monitoring

## Monitoring

### Key Metrics
```
Application: Request latency, error rate, cache hit ratio
Infrastructure: CPU, memory, network I/O
Business: API availability, data freshness, external dependency health
```

### Alerting
- **Critical**: Availability <99.9%, Error rate >1% → PagerDuty
- **Warning**: Cache hit <90%, Latency P95 >200ms → Slack

## Deployment

### Infrastructure
- **Terraform**: Infrastructure as Code
- **Multi-AZ**: us-west-1a/b/c for high availability
- **Auto-destroy**: Post-evaluation cleanup ready

### Application
- **Docker**: Containerized FastAPI application
- **Health Checks**: `/health` endpoint for load balancer
- **Graceful Shutdown**: Proper signal handling

## Disaster Recovery

- **RTO**: 15 minutes (automated Multi-AZ failover)
- **RPO**: 5 minutes (Aurora continuous backup)
- **Backup Strategy**: Automated daily snapshots, 35-day retention
- **Failover**: Cross-AZ automatic, cross-region manual (if needed)

## Future Roadmap

### Phase 2 Enhancements
- **Additional Currencies**: EUR, GBP, CAD support
- **Real-time Updates**: WebSocket notifications
- **Analytics API**: Historical trend analysis
- **Rate Alerts**: Threshold-based notifications

### Technical Evolution
- **Kubernetes**: Migration from EC2 for better orchestration
- **gRPC**: High-performance service-to-service communication
- **Multi-Region**: Active-active deployment for global scale
