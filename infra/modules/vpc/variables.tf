variable "name" {
  type        = string
  description = "Base name for VPC resources"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for VPC"
  default     = "10.0.0.0/16"
}

variable "az_count" {
  type        = number
  description = "Number of availability zones"
  default     = 3
}

variable "tags" {
  type        = map(string)
  default     = {}
}
