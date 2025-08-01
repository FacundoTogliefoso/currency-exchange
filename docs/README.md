# Technical Documentation

This directory contains comprehensive technical documentation for the Currency Exchange Platform.

## Documentation Index

### Core Architecture
- **[Architecture Overview](./architecture.md)** - System design, components, and technical decisions
- **[API Reference](../README.md#api-endpoints)** - Endpoint specifications and usage examples

### Operations
- **[Deployment Guide](../README.md#deployment)** - Docker Compose and infrastructure setup
- **[Monitoring](./architecture.md#monitoring)** - Metrics, alerting, and observability
- **[Health Checks](./architecture.md#monitoring)** - System health monitoring endpoints

### Development
- **[Local Development](../README.md#development)** - Setting up development environment
- **[Testing Strategy](../README.md#testing)** - Unit tests, integration tests, and coverage
- **[Contributing Guidelines](../README.md#development)** - Code style, pre-commit hooks

## System Overview

```
FastAPI + Redis + Aurora + Banxico API = 99.95% Availability
```

### Key Specifications
- **Framework**: FastAPI 0.111.0 with async/await
- **Database**: Aurora Serverless v2 (MySQL-compatible)
- **Cache**: ElastiCache Redis with intelligent TTL
- **Region**: us-west-1 (N. California)
- **SLO**: 99.95% availability, P95 < 200ms latency

## Quick Navigation

| Need | Document |
|------|----------|
| **Getting Started** | [Main README](../README.md) |
| **System Design** | [Architecture](./architecture.md) |
| **API Usage** | [API Endpoints](../README.md#api-endpoints) |
| **Deployment** | [Docker Setup](../README.md#deployment) |
| **Monitoring** | [Observability](./architecture.md#monitoring) |

## Key Metrics & SLOs

### Service Level Objectives
- **Availability**: 99.95% (22 minutes downtime/month)
- **Latency**: P95 < 200ms, P99 < 500ms
- **Throughput**: 5,000 RPS sustained
- **Error Budget**: 0.05% (22 minutes/month)

### Architecture Highlights
- **Multi-AZ Deployment**: us-west-1a/b/c for high availability
- **Circuit Breaker**: Fault tolerance for external API dependencies
- **Intelligent Caching**: 5min/1h/30min TTL strategy for optimal performance
- **Auto Scaling**: 2-10 EC2 instances based on traffic patterns

## Technical Stack

### Production Infrastructure
- **Compute**: EC2 t3.medium with Auto Scaling (2-10 instances)
- **Database**: Aurora Serverless v2 (0.5-16 ACUs) + 2 read replicas
- **Cache**: ElastiCache Redis r6g.large with Multi-AZ
- **Load Balancer**: Application Load Balancer with health checks
- **CDN**: CloudFront with global edge locations

### Development Tools
- **Language**: Python 3.10+ with type hints
- **Testing**: pytest with async support, 85%+ coverage
- **Code Quality**: black, ruff, pre-commit hooks
- **Infrastructure**: Terraform for Infrastructure as Code
- **Containerization**: Docker + Docker Compose for local development

## Performance Characteristics

### Current Capacity
- **Peak Traffic**: 10,000 requests/minute
- **Daily Volume**: 1M+ API calls
- **Cache Hit Ratio**: >90% (target)
- **Data Storage**: 100GB historical exchange rates

### Scaling Strategy
- **Horizontal**: Auto Scaling Group scales based on CPU/memory
- **Vertical**: Aurora ACUs scale automatically (0.5-16)
- **Geographic**: CloudFront provides global edge caching
- **Database**: Read replicas handle read-heavy workloads

## Security & Compliance

### Security Layers
- **Network**: VPC with public/private subnets, security groups
- **Application**: WAF with DDoS protection, rate limiting
- **Data**: Encryption at rest and in transit (TLS 1.3)
- **Access**: IAM roles with least-privilege principle

### Monitoring & Alerting
- **Real-time Metrics**: CloudWatch dashboards for all components
- **Proactive Alerting**: PagerDuty for critical issues, Slack for warnings
- **Health Checks**: Comprehensive dependency monitoring
- **Audit Trail**: All infrastructure changes tracked

## Next Steps

### For New Team Members
1. **Start Here**: [Main README](../README.md) for project overview
2. **Local Setup**: Follow development setup instructions
3. **Architecture**: Read [architecture.md](./architecture.md) for system design
4. **Run Tests**: Execute test suite to validate environment

### For SRE/Operations
1. **Deployment**: Review infrastructure and deployment procedures
2. **Monitoring**: Understand metrics, alerts, and dashboards
3. **Incident Response**: Familiarize with health checks and troubleshooting
4. **Capacity Planning**: Review scaling policies and resource limits

## Support & Maintenance

### Documentation Updates
- **Architecture changes**: Update architecture.md
- **API changes**: Update main README.md
- **New features**: Add to appropriate documentation section
- **Operational procedures**: Document in architecture.md

### Questions & Issues
- **Technical Questions**: Review architecture documentation
- **Deployment Issues**: Check main README deployment section
- **Performance Issues**: Review monitoring and alerting setup
- **Feature Requests**: Consider impact on architecture and SLOs
