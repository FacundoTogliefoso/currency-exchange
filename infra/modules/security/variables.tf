variable "name" {
  type        = string
  description = "Base name for security resources"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "rate_limit" {
  type        = number
  description = "WAF rate limit per 5 minutes"
  default     = 2000
}

variable "allowed_ssh_cidrs" {
  type        = list(string)
  description = "CIDRs allowed for SSH access"
  default     = []
}

variable "tags" {
  type        = map(string)
  default     = {}
}
