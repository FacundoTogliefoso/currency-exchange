variable "name" {
  type        = string
  description = "Base name for Aurora resources"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID for Aurora"
}

variable "subnet_ids" {
  type        = list(string)
  description = "Subnet IDs for Aurora subnet group"
}

variable "allowed_cidrs" {
  type        = list(string)
  description = "List of CIDRs allowed to access Aurora"
}

variable "database_name" {
  type        = string
  description = "Initial database name"
  default     = "currency_exchange"
}

variable "master_username" {
  type        = string
  description = "Master username for Aurora"
  default     = "admin"
}

variable "master_password" {
  type        = string
  description = "Master password for Aurora"
  sensitive   = true
}

variable "tags" {
  type        = map(string)
  default     = {}
}
