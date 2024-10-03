module "s3_bucket" {
  source  = "terraform-aws-modules/s3-bucket/aws"
  version = "4.1.2"

  bucket        = "docs-scraper-lake"
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
