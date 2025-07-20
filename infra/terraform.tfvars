# General Configuration
aws_region = "us-west-1"
environment = "dev"
project_name = "currency-exchange"

# Network Configuration
vpc_cidr = "10.0.0.0/16"
az_count = 3

# Database Configuration
database_name = "exchange_rates_db"
db_username = "currency_admin"
db_password = "CurrencyExch@nge2025!Secure"

# API Configuration
banxico_token = "60779e9a83e7133cc298c8d7f2b3e8750e9851887f7ad2f07e6c872445feb672"
redis_auth_token = ""

# Security Configuration
allowed_ssh_cidrs = ["0.0.0.0/0"]
waf_rate_limit = 2000

# Compute Configuration
instance_type = "t3.medium"
asg_min_size = 2
asg_max_size = 10
asg_desired_capacity = 2

# Monitoring Configuration
log_retention_days = 30

# Additional Tags
additional_tags = {
  Owner       = "SRE-Team"
  CostCenter  = "Engineering"
  Backup      = "Required"
}
