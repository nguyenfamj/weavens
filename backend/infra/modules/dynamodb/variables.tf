variable "enable_tags" {
  description = "Enable tags for the tables"
  type        = bool
  default     = true
}

variable "tag_environment" {
  description = "Environment tag for the tables"
  type        = string
  default     = "production"
}
