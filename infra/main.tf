# infra/main.tf

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = local.common_tags
  }
}

# VPC Module
module "vpc" {
  source = "./modules/vpc"

  name     = local.name_prefix
  vpc_cidr = var.vpc_cidr
  az_count = var.az_count

  tags = local.common_tags
}

# Security Module
module "security" {
  source = "./modules/security"

  name               = local.name_prefix
  vpc_id             = module.vpc.vpc_id
  rate_limit         = var.waf_rate_limit
  allowed_ssh_cidrs  = var.allowed_ssh_cidrs

  tags = local.common_tags
}

# Secrets Module
module "secrets" {
  source = "./modules/secrets"

  name             = local.name_prefix
  db_username      = var.db_username
  db_password      = var.db_password
  banxico_token    = var.banxico_token
  redis_auth_token = var.redis_auth_token

  tags = local.common_tags
}

# IAM Module
module "iam" {
  source = "./modules/iam"

  name        = local.name_prefix
  aws_region  = var.aws_region
  secrets_arns = [
    module.secrets.db_credentials_arn,
    module.secrets.banxico_token_arn
  ]

  tags = local.common_tags
}

# Cache Module (Redis)
module "cache" {
  source = "./modules/cache"

  name           = local.name_prefix
  vpc_id         = module.vpc.vpc_id
  subnet_ids     = module.vpc.private_subnet_ids
  allowed_cidrs  = [var.vpc_cidr]

  tags = local.common_tags
}

# Database Module (Aurora)
module "database" {
  source = "./modules/database"

  name            = local.name_prefix
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.database_subnet_ids
  allowed_cidrs   = [var.vpc_cidr]
  database_name   = var.database_name
  master_username = var.db_username
  master_password = var.db_password

  tags = local.common_tags
}

# Compute Module (EC2 + ALB)
module "compute" {
  source = "./modules/compute"

  name                = local.name_prefix
  vpc_id              = module.vpc.vpc_id
  public_subnet_ids   = module.vpc.public_subnet_ids
  private_subnet_ids  = module.vpc.private_subnet_ids
  instance_type       = var.instance_type
  min_size           = var.asg_min_size
  max_size           = var.asg_max_size
  desired_capacity   = var.asg_desired_capacity
  user_data          = local.user_data
  instance_profile_name  = module.iam.ec2_instance_profile_name

  tags = local.common_tags
}

# Monitoring Module
module "monitoring" {
  source = "./modules/monitoring"

  name               = local.name_prefix
  aws_region         = var.aws_region
  alb_name           = module.compute.alb_dns_name
  redis_cluster_id   = "${local.name_prefix}-rg"
  log_retention_days = var.log_retention_days

  tags = local.common_tags
}
