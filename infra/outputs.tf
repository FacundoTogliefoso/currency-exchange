# Application Access
output "application_url" {
  description = "URL to access the application"
  value       = "http://${module.compute.alb_dns_name}"
}

output "application_health_check" {
  description = "Health check endpoint"
  value       = "http://${module.compute.alb_dns_name}/api/v1/health"
}

# Network Information
output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "vpc_cidr" {
  description = "VPC CIDR block"
  value       = module.vpc.vpc_cidr
}

output "public_subnet_ids" {
  description = "Public subnet IDs"
  value       = module.vpc.public_subnet_ids
}

output "private_subnet_ids" {
  description = "Private subnet IDs"
  value       = module.vpc.private_subnet_ids
}

# Compute Information
output "alb_dns_name" {
  description = "Application Load Balancer DNS name"
  value       = module.compute.alb_dns_name
}

output "alb_zone_id" {
  description = "Application Load Balancer Zone ID"
  value       = module.compute.alb_zone_id
}

output "autoscaling_group_name" {
  description = "Auto Scaling Group name"
  value       = module.compute.asg_name
}

# Database Information
output "database_endpoint" {
  description = "Aurora cluster endpoint"
  value       = module.database.aurora_cluster_endpoint
  sensitive   = true
}

output "database_reader_endpoint" {
  description = "Aurora reader endpoint"
  value       = module.database.aurora_reader_endpoint
  sensitive   = true
}

# Cache Information
output "redis_endpoint" {
  description = "Redis cluster endpoint"
  value       = module.cache.redis_primary_endpoint
  sensitive   = true
}

output "redis_port" {
  description = "Redis port"
  value       = module.cache.redis_port
}

# Security Information
output "waf_arn" {
  description = "WAF ARN"
  value       = module.security.waf_arn
}

# Secrets Information
output "secrets_arns" {
  description = "ARNs of created secrets"
  value = {
    database_credentials = module.secrets.db_credentials_arn
    banxico_token       = module.secrets.banxico_token_arn
    redis_auth          = module.secrets.redis_auth_arn
  }
  sensitive = true
}

# Monitoring Information
output "cloudwatch_dashboard_url" {
  description = "CloudWatch dashboard URL"
  value       = module.monitoring.dashboard_url
}

output "sns_topic_arn" {
  description = "SNS topic ARN for alerts"
  value       = module.monitoring.sns_topic_arn
}

# Cost Information
output "estimated_monthly_cost" {
  description = "Estimated monthly cost breakdown (USD)"
  value       = local.estimated_monthly_cost
}

# Environment Configuration
output "environment_info" {
  description = "Environment configuration details"
  value = {
    project_name = var.project_name
    environment  = var.environment
    aws_region   = var.aws_region
    az_count     = var.az_count
    instance_type = var.instance_type
    created_at   = local.common_tags.CreatedAt
  }
}

# Connection Information for Application
output "application_config" {
  description = "Configuration for application deployment"
  value = {
    redis_host        = module.cache.redis_primary_endpoint
    redis_port        = module.cache.redis_port
    database_host     = module.database.aurora_cluster_endpoint
    database_port     = module.database.aurora_port
    database_name     = var.database_name
    secrets_region    = var.aws_region
    log_group         = module.monitoring.log_group_name
  }
  sensitive = true
}
