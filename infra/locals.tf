locals {
  # Naming
  name_prefix = "${var.project_name}-${var.environment}"

  # Common tags applied to all resources
  common_tags = merge(
    {
      Project     = var.project_name
      Environment = var.environment
      ManagedBy   = "terraform"
      Region      = var.aws_region
      CreatedAt   = timestamp()
    },
    var.additional_tags
  )

  # User data script for EC2 instances
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    project_name      = var.project_name
    environment       = var.environment
    aws_region        = var.aws_region
    redis_endpoint    = module.cache.redis_primary_endpoint
    redis_port        = module.cache.redis_port
    db_endpoint       = module.database.aurora_cluster_endpoint
    db_port           = module.database.aurora_port
    db_name           = var.database_name
    secrets_db_arn    = module.secrets.db_credentials_arn
    secrets_banxico_arn = module.secrets.banxico_token_arn
    log_group         = module.monitoring.log_group_name
  }))

  # Cost estimation (monthly USD in us-west-1)
  estimated_monthly_cost = {
    vpc           = 0      # Free tier
    compute = {
      ec2_instances = var.asg_desired_capacity * 45  # t3.medium ~$45/month
      alb          = 25    # ALB ~$25/month
    }
    cache         = 80     # r6g.large ~$80/month
    database      = 65     # Aurora Serverless v2 ~$65/month (avg)
    monitoring    = 30     # CloudWatch + SNS ~$30/month
    secrets       = 2      # Secrets Manager ~$2/month
    total         = 202 + (var.asg_desired_capacity * 45)
  }

  # Environment-specific configurations
  env_config = {
    dev = {
      instance_type    = "t3.small"
      asg_min_size    = 1
      asg_max_size    = 3
      asg_desired     = 1
      log_retention   = 7
    }
    staging = {
      instance_type    = "t3.medium"
      asg_min_size    = 2
      asg_max_size    = 5
      asg_desired     = 2
      log_retention   = 14
    }
    prod = {
      instance_type    = "t3.medium"
      asg_min_size    = 2
      asg_max_size    = 10
      asg_desired     = 2
      log_retention   = 30
    }
  }
}
