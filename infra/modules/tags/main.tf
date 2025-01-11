variable "environment" {
  type        = string
  description = "The environment to tag the resources with"
}

variable "additional_tags" {
  type        = map(string)
  description = "Additional tags to apply to the resources"
  default     = {}
}

locals {
  default_tags = {
    Environment = var.environment
    ManagedBy   = "Terraform"
    Project     = "Weavens"
  }
}

output "tags" {
  value = merge(local.default_tags, var.additional_tags)
}
