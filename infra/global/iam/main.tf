data "aws_caller_identity" "current" {}

locals {
  region = "eu-north-1"
}

provider "aws" {
  region = local.region
}

# Github Actions user
module "github_actions_user" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-user"
  version = "~> 5.0"

  name = "github-actions-ci"

  create_iam_access_key = true
  create_user           = true

  tags = {
    Environment = "production"
    Terraform   = true
    Purpose     = "Github Actions CI/CD user"
  }
}

resource "aws_iam_policy" "github_actions_ecr_policy" {
  name        = "ECRPushAccess"
  description = "Policy for GitHub Actions to push to ECR"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecr:BatchCheckLayerAvailability",
          "ecr:GetDownloadUrlForLayer",
          "ecr:GetRepositoryPolicy",
          "ecr:DescribeRepositories",
          "ecr:ListImages",
          "ecr:DescribeImages",
          "ecr:BatchGetImage",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ]
        Resource = data.aws_ecr_repository.backend.arn
      }
    ]
  })
}

resource "aws_iam_policy" "github_actions_terraform_policy" {
  name        = "TerraformApplyAccess"
  description = "Policy for GitHub Actions to apply Terraform changes"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket",
          "s3:GetObject",
          "s3:PutObject",
          "dynamodb:GetItem",
          "dynamodb:PutItem",
          "dynamodb:DeleteItem",
          "dynamodb:DescribeContinuousBackups",
          "dynamodb:DescribeTable",
          "dynamodb:DescribeTimeToLive",
          "dynamodb:ListTagsOfResource",
          "ssm:GetParameter",
          "ssm:GetParameters",
          "ssm:PutParameter",
          "ssm:ListTagsForResource",
          "ecs:*",
          "iam:PassRole",
          "iam:GetPolicy",
          "iam:GetPolicyVersion",
          "iam:GetRole",
          "iam:GetRolePolicy",
          "iam:GetInstanceProfile",
          "iam:ListRolePolicies",
          "iam:ListAttachedRolePolicies",
          "acm:DescribeCertificate",
          "acm:ListTagsForCertificate",
          "logs:DescribeLogGroups",
          "logs:CreateLogGroup",
          "logs:DeleteLogGroup",
          "logs:ListTagsLogGroup",
          "logs:ListTagsForResource",
          "logs:PutRetentionPolicy",
          "logs:TagLogGroup",
          "logs:UntagLogGroup",
          "es:DescribeDomain",
          "es:DescribeElasticsearchDomain",
          "es:DescribeElasticsearchDomainConfig",
          "es:ListDomainNames",
          "es:ListTags"
        ]
        Resource = [
          data.aws_s3_bucket.terraform_state.arn,
          "${data.aws_s3_bucket.terraform_state.arn}/*",
          data.aws_dynamodb_table.terraform_state_locks.arn,
          "arn:aws:ssm:${local.region}:${data.aws_caller_identity.current.account_id}:parameter/weavens/production/*",
          "arn:aws:ssm:${local.region}::parameter/*",
          "arn:aws:ecs:${local.region}:${data.aws_caller_identity.current.account_id}:*",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:role/*",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:policy/*",
          "arn:aws:iam::${data.aws_caller_identity.current.account_id}:instance-profile/*",
          "arn:aws:acm:${local.region}:${data.aws_caller_identity.current.account_id}:certificate/*",
          "arn:aws:logs:${local.region}:${data.aws_caller_identity.current.account_id}:log-group:*",
          "arn:aws:es:${local.region}:${data.aws_caller_identity.current.account_id}:domain/*",
          "arn:aws:dynamodb:${local.region}:${data.aws_caller_identity.current.account_id}:table/*"
        ]
      },
      {
        Effect = "Allow"
        Action = [
          "ssm:DescribeParameters",
          "ec2:DescribeAvailabilityZones",
          "ec2:DescribeVpcs",
          "ec2:DescribeVpcAttribute",
          "ec2:DescribeSubnets",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeSecurityGroupRules",
          "ec2:DescribeLaunchTemplates",
          "ec2:DescribeLaunchTemplateVersions",
          "elasticloadbalancing:DescribeLoadBalancers",
          "elasticloadbalancing:DescribeTargetGroups",
          "elasticloadbalancing:DescribeTargetGroupAttributes",
          "elasticloadbalancing:DescribeTags",
          "elasticloadbalancing:DescribeLoadBalancerAttributes",
          "elasticloadbalancing:DescribeListeners",
          "elasticloadbalancing:DescribeListenerAttributes",
          "autoscaling:DescribeScalableTargets",
          "autoscaling:DescribeAutoScalingGroups",
          "autoscaling:DescribeLaunchConfigurations",
          "autoscaling:DescribeLaunchTemplates",
          "autoscaling:DescribeLaunchTemplateVersions",
          "autoscaling:DescribeTags",
          "application-autoscaling:DescribeScalableTargets",
          "application-autoscaling:ListTagsForResource",
          "application-autoscaling:DescribeScalingPolicies",
          "application-autoscaling:DescribeScheduledActions",
          "application-autoscaling:DescribeMetricCollectionTypes",
          "application-autoscaling:DescribeScalingActivities"
        ]
        Resource = "*"
      },
      {
        Effect = "Allow"
        Action = [
          "ecs:RegisterTaskDefinition",
          "ecs:DeregisterTaskDefinition",
          "ecs:DescribeTaskDefinition",
          "ecs:ListTaskDefinitions",
          "ecs:ListTaskDefinitionFamilies",
          "ecs:GetTaskDefinition",
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:CreateService",
          "ecs:DeleteService"
        ]
        Resource = [
          "arn:aws:ecs:${local.region}:${data.aws_caller_identity.current.account_id}:*"
        ]
      }
    ]
  })
}

resource "aws_iam_user_policy_attachment" "github_actions_ecr" {
  user       = module.github_actions_user.iam_user_name
  policy_arn = aws_iam_policy.github_actions_ecr_policy.arn
}

resource "aws_iam_user_policy_attachment" "github_actions_terraform" {
  user       = module.github_actions_user.iam_user_name
  policy_arn = aws_iam_policy.github_actions_terraform_policy.arn
}

# Output the access key (only shown once during creation)
output "github_actions_access_key_id" {
  value = module.github_actions_user.iam_access_key_id
}

output "github_actions_secret_access_key" {
  value     = module.github_actions_user.iam_access_key_secret
  sensitive = true
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
