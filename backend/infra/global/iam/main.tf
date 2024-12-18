provider "aws" {
  region = "eu-north-1"
}

module "iam_infrastructure_admin_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "5.44.0"

  role_name   = "InfrastructureAdmin"
  create_role = true

  trusted_role_arns = [
    "arn:aws:iam::484907490685:root",
    "arn:aws:iam::484907490685:user/GlobalAdmin"
  ]
  # TODO: Enforce MFA for this role when we have proper SSO setup
  role_requires_mfa = true

  custom_role_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
    "arn:aws:iam::aws:policy/AmazonVPCFullAccess",
    "arn:aws:iam::aws:policy/AmazonSSMReadOnlyAccess",
    "arn:aws:iam::aws:policy/CloudWatchLogsFullAccess",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryFullAccess",
    "arn:aws:iam::aws:policy/AmazonEC2FullAccess",
    "arn:aws:iam::aws:policy/AmazonECS_FullAccess",
    "arn:aws:iam::aws:policy/IAMFullAccess"
  ]

  tags = {
    Environment = "production"
    Terraform   = true
    Role        = "InfrastructureAdmin"
  }
}

module "iam_policy_assume_infrastructure_admin_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-policy"
  version = "5.44.0"

  name          = "AssumeInfrastructureAdminRole"
  create_policy = true

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "sts:AssumeRole"
        Resource = module.iam_infrastructure_admin_role.iam_role_arn
      }
    ]
  })
}

module "developer_policy" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-policy"
  version = "5.44.0"

  name = "DeveloperAccess"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ec2:Describe*",
          "ecs:Describe*",
          "logs:GetLogEvents",
        ]
        Resource = "*"
      }
    ]
  })
}

module "developers_group" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-group-with-policies"
  version = "5.44.0"
  name    = "Developers"

  group_users = []

  custom_group_policy_arns = [
    module.developer_policy.arn
  ]
}
