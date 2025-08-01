variable "name" {
  type        = string
  description = "Base name for Redis resources"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID for Redis"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for Redis subnet group"
}

variable "allowed_cidrs" {
  type        = list(string)
  description = "List of CIDRs allowed to access Redis"
}

variable "tags" {
  type        = map(string)
  default     = {}
}
