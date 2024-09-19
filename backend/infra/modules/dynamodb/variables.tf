variable "property_table_name" {
  description = "The name of the DynamoDB table for storing property data"
  type        = string
}

variable "checkpoint_table_name" {
  description = "The name of the DynamoDB table for storing checkpoints"
  type        = string
}
