module "iam_nova_developer" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-user"
  version = "5.44.0"

  name = "nova.developer"

  create_iam_access_key         = false
  create_iam_user_login_profile = true
  create_user                   = true

  policy_arns = [
    "arn:aws:iam::aws:policy/IAMUserChangePassword",
    "arn:aws:iam::aws:policy/IAMSelfManageServiceSpecificCredentials",
    "arn:aws:iam::aws:policy/IAMFullAccess",
    module.iam_policy_assume_infrastructure_admin_role.arn
  ]

  tags = {
    Environment = "production"
    Terraform   = true
    User        = "nova.developer"
  }
}

module "iam_infrastructure_admin_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-assumable-role"
  version = "5.44.0"

  role_name = "InfrastructureAdmin"

  create_role = true
  trusted_role_arns = [
    "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root",
    # TODO: This role should be here just temporarily until we have a proper CI/CD setup
    module.iam_nova_developer.iam_user_arn
  ]

  custom_role_policy_arns = [
    "arn:aws:iam::aws:policy/AmazonS3FullAccess",
    "arn:aws:iam::aws:policy/AWSLambda_FullAccess",
    "arn:aws:iam::aws:policy/AmazonVPCFullAccess",
    "arn:aws:iam::aws:policy/AmazonAPIGatewayAdministrator",
    "arn:aws:iam::aws:policy/AWSBillingReadOnlyAccess",
    "arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess",
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

  name = "AssumeInfrastructureAdminRole"

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
