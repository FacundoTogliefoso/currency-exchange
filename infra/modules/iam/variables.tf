variable "name" {
  type        = string
  description = "Base name for IAM resources"
}

variable "aws_region" {
  type        = string
  description = "AWS region for resource ARNs"
}

variable "secrets_arns" {
  type        = list(string)
  description = "List of Secrets Manager ARNs that EC2 instances need access to"
  default     = []
}

variable "additional_policies" {
  type        = list(string)
  description = "Additional IAM policy ARNs to attach to the EC2 role"
  default     = []
}

variable "tags" {
  type        = map(string)
  description = "Tags to apply to IAM resources"
  default     = {}
}
