variable "property_table_name" {
  description = "The name of the DynamoDB table for storing property data"
  type        = string
}

variable "chat_histories_table_name" {
  description = "The name of the DynamoDB table for storing chat histories"
  type        = string
}
