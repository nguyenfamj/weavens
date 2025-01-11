variable "environment" {
  description = "The environment to deploy to"
  type        = string
}

variable "tags" {
  description = "Tags to apply to the resources"
  type        = map(string)
  default     = {}
}

variable "properties_table_config" {
  description = "Configuration for Properties table"
  type = object({
    billing_mode   = string
    read_capacity  = optional(number)
    write_capacity = optional(number)
    crawled_url_gsi_config = optional(object({
      read_capacity  = number
      write_capacity = number
    }))
    indexed_opensearch_gsi_config = optional(object({
      read_capacity  = number
      write_capacity = number
    }))
    point_in_time_recovery_enabled = optional(bool)
    server_side_encryption_enabled = optional(bool)
  })

  validation {
    condition = (
      var.properties_table_config.billing_mode == "PAY_PER_REQUEST" ||
      (var.properties_table_config.billing_mode == "PROVISIONED" &&
        var.properties_table_config.read_capacity != null &&
      var.properties_table_config.write_capacity != null)
    )
    error_message = "read_capacity and write_capacity must be set when billing_mode is PROVISIONED"
  }
}


variable "checkpoints_table_config" {
  description = "Configuration for Checkpoints table"
  type = object({
    billing_mode                   = string
    read_capacity                  = optional(number)
    write_capacity                 = optional(number)
    point_in_time_recovery_enabled = optional(bool)
    server_side_encryption_enabled = optional(bool)
  })

  validation {
    condition = (
      var.checkpoints_table_config.billing_mode == "PAY_PER_REQUEST" ||
      (var.checkpoints_table_config.billing_mode == "PROVISIONED" &&
        var.checkpoints_table_config.read_capacity != null &&
      var.checkpoints_table_config.write_capacity != null)
    )
    error_message = "read_capacity and write_capacity must be set when billing_mode is PROVISIONED"
  }
}

variable "scrape_jobs_table_config" {
  description = "Configuration for ScrapeJobs table"
  type = object({
    billing_mode                   = string
    read_capacity                  = optional(number)
    write_capacity                 = optional(number)
    point_in_time_recovery_enabled = optional(bool)
    server_side_encryption_enabled = optional(bool)

    type_by_status_gsi_config = optional(object({
      read_capacity  = number
      write_capacity = number
    }))
  })

  validation {
    condition = (
      var.scrape_jobs_table_config.billing_mode == "PAY_PER_REQUEST" ||
      (var.scrape_jobs_table_config.billing_mode == "PROVISIONED" &&
        var.scrape_jobs_table_config.read_capacity != null &&
      var.scrape_jobs_table_config.write_capacity != null)
    )
    error_message = "read_capacity and write_capacity must be set when billing_mode is PROVISIONED"
  }
}

variable "scraped_content_table_config" {
  description = "Configuration for ScrapedContent table"
  type = object({
    billing_mode                   = string
    read_capacity                  = optional(number)
    write_capacity                 = optional(number)
    point_in_time_recovery_enabled = optional(bool)
    server_side_encryption_enabled = optional(bool)

    status_by_type_gsi_config = optional(object({
      read_capacity  = number
      write_capacity = number
    }))
  })

  validation {
    condition = (
      var.scraped_content_table_config.billing_mode == "PAY_PER_REQUEST" ||
      (var.scraped_content_table_config.billing_mode == "PROVISIONED" &&
        var.scraped_content_table_config.read_capacity != null &&
      var.scraped_content_table_config.write_capacity != null)
    )
    error_message = "read_capacity and write_capacity must be set when billing_mode is PROVISIONED"
  }
}


variable "user_message_logs_table_config" {
  description = "Configuration for UserMessageLogs table"
  type = object({
    billing_mode                   = string
    read_capacity                  = optional(number)
    write_capacity                 = optional(number)
    point_in_time_recovery_enabled = optional(bool)
    server_side_encryption_enabled = optional(bool)
  })
}
