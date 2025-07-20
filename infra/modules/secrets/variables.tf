variable "name" {
  type        = string
  description = "Base name for secrets"
}

variable "db_username" {
  type        = string
  description = "Database username"
  default     = "admin"
}

variable "db_password" {
  type        = string
  description = "Database password"
  sensitive   = true
}

variable "banxico_token" {
  type        = string
  description = "Banxico API token"
  sensitive   = true
  default     = ""
}

variable "redis_auth_token" {
  type        = string
  description = "Redis authentication token (optional)"
  sensitive   = true
  default     = ""
}

variable "tags" {
  type        = map(string)
  default     = {}
}
