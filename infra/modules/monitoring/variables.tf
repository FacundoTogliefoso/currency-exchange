variable "name" {
  type        = string
  description = "Base name for monitoring resources"
}

variable "aws_region" {
  type        = string
  description = "AWS region"
}

variable "alb_name" {
  type        = string
  description = "ALB name for monitoring"
  default     = ""
}

variable "redis_cluster_id" {
  type        = string
  description = "Redis cluster ID for monitoring"
  default     = ""
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention in days"
  default     = 30
}

variable "tags" {
  type        = map(string)
  default     = {}
}
