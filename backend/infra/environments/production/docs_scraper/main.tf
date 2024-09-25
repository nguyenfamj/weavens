provider "aws" {
  region = local.aws_region

  skip_metadata_api_check = true
  skip_region_validation  = true
}

locals {
  s3_bucket_name = "docs-scraper-lake"
  aws_region     = "eu-north-1"
}

module "s3_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "4.1.2"

  bucket        = local.s3_bucket_name
  request_payer = "BucketOwner"

  force_destroy = true

  versioning = {
    enabled = true
  }

  tags = {
    Environment = "production"
    Project     = "docs-scraper"
  }
}
