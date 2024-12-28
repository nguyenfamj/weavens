terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "eu-north-1"
}

module "static_website" {
  source  = "terraform-aws-modules/s3-bucket/aws//modules/object"
  version = "~> 3.0"

  bucket = module.s3_bucket.s3_bucket_id

  content_type = "text/html"

  key = "index.html"
  acl = "private"
}

module "s3_bucket" {
  source = "terraform-aws-modules/s3-bucket/aws"

  bucket = "titan-frontend"

  force_destroy = true

  block_public_acls = false
  block_public_policy = false
  ignore_public_acls = false
  restrict_public_buckets = false

  website = {
    index_document = "index.html"
    error_document = "index.html"
  }

  cors_rule = [
    {
      allowed_headers = ["*"]
      allowed_methods = ["GET", "HEAD"]
      allowed_origins = ["*"]
      expose_headers  = ["ETag"]
      max_age_seconds = 3000
    }
  ]

  control_object_ownership = true
  object_ownership         = "ObjectWriter"

  versioning = {
    enabled = false
  }
}


# S3 bucket policy
resource "aws_s3_bucket_policy" "bucket_policy" {
  bucket = module.s3_bucket.s3_bucket_id
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "PublicReadGetObject"
        Effect    = "Allow"
        Principal = "*"
        Action    = "s3:GetObject"
        Resource  = "${module.s3_bucket.s3_bucket_arn}/*"
      }
    ]
  })
}
