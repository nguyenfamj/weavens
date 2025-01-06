locals {
  tags = {
    Terraform   = "true"
    Environment = "production"
  }
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

module "search_instance" {
  source  = "terraform-aws-modules/opensearch/aws"
  version = "1.5.0"

  domain_name = "titan-production-search"

  cluster_config = {
    instance_count = 1
    instance_type  = "t3.small.search"

    zone_awareness_enabled   = false
    dedicated_master_enabled = false
  }

  ebs_options = {
    ebs_enabled = true
    volume_type = "gp3"
    volume_size = 10
  }

  encrypt_at_rest = {
    enabled = true
  }

  software_update_options = {
    auto_software_update_enabled = true
  }

  vpc_options = {
    subnet_ids = [var.private_subnet_ids[0]]
    vpc_id     = var.vpc_id
  }

  security_group_rules = {
    ingress = {
      from_port   = 443
      to_port     = 443
      ip_protocol = "tcp"
      cidr_ipv4   = var.vpc_cidr
    }
  }

  access_policy_statements = [
    {
      effect  = "Allow"
      actions = ["es:*"]
      principals = [
        {
          type        = "AWS"
          identifiers = ["*"]
        }
      ]
    }
  ]

  advanced_security_options = {
    enabled = false
  }

  auto_tune_options = {
    desired_state = "DISABLED"
  }

  tags = local.tags
}


output "search_instance_endpoint" {
  value = module.search_instance.domain_endpoint
}

output "search_domain_arn" {
  value = module.search_instance.domain_arn
}
