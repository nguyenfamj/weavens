variable "environment" {
  type        = string
  description = "The environment to deploy the IAM role in"
}

variable "tags" {
  type        = map(string)
  description = "The tags to apply to the IAM role"
}

variable "opensearch_domain_arn" {
  type        = string
  description = "The ARN of the OpenSearch domain"
}
