variable "name" {
  type        = string
  description = "Base name for compute resources"
}

variable "vpc_id" {
  type        = string
  description = "VPC ID"
}

variable "public_subnet_ids" {
  type        = list(string)
  description = "Public subnet IDs for ALB"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "Private subnet IDs for EC2 instances"
}

variable "instance_type" {
  type        = string
  description = "EC2 instance type"
  default     = "t3.medium"
}

variable "min_size" {
  type        = number
  description = "Minimum number of instances"
  default     = 2
}

variable "max_size" {
  type        = number
  description = "Maximum number of instances"
  default     = 10
}

variable "desired_capacity" {
  type        = number
  description = "Desired number of instances"
  default     = 2
}

variable "user_data" {
  type        = string
  description = "User data script for EC2 instances"
  default     = ""
}

variable "tags" {
  type        = map(string)
  default     = {}
}

variable "instance_profile_name" {
  type        = string
  description = "IAM instance profile name for EC2 instances"
}
