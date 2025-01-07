output "s3_bucket_name" {
  value       = module.s3_bucket.s3_bucket_id
  description = "Name of S3 bucket"
}
