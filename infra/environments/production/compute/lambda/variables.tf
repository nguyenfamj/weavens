variable "environment" {
  type        = string
  description = "The environment to deploy to"
}

variable "tags" {
  type        = map(string)
  description = "The tags to apply to the resources"
}
