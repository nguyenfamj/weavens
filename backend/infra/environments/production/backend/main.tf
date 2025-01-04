locals {
  region = "eu-north-1"
  name   = "production-crux-backend"

  container_name = "ecs-crux-backend"
  container_port = 8386

  tags = {
    Terraform   = "true"
    Environment = "production"
    Service     = local.name
  }
}

################################################################################
# Cluster
################################################################################
module "ecs" {
  source = "terraform-aws-modules/ecs/aws"

  cluster_name = local.name

  create_task_exec_iam_role = true
  task_exec_iam_role_policies = {
    AWSSecretsManagerReadWrite = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
    ParameterAccess            = aws_iam_policy.parameter_access.arn
  }

  cluster_configuration = {
    execute_command_configuration = {
      logging = "OVERRIDE"
      log_configuration = {
        cloud_watch_log_group_name = local.name
      }
    }
  }

  fargate_capacity_providers = {
    FARGATE_SPOT = {
      default_capacity_provider_strategy = {
        weight = 100
      }
    }
  }

  services = {
    (local.name) = {
      cpu    = 512
      memory = 2048

      enable_execute_command = true
      assign_public_ip       = true

      deployment_circuit_breaker = {
        enable   = true
        rollback = true
      }

      # Keeping 0% minimum healthy during MVP
      deployment_minimum_healthy_percent = 0
      deployment_maximum_percent         = 100

      container_definitions = {
        (local.container_name) = {
          image = "${var.backend_ecr_repository_url}:${data.aws_ssm_parameter.production_backend_image_tag.value}"

          port_mappings = [
            {
              name          = local.container_name
              containerPort = local.container_port
              hostPort      = local.container_port
              protocol      = "tcp"
            }
          ]

          readonly_root_filesystem  = false
          enable_cloudwatch_logging = false

          memory_reservation = 1024
          memory             = 2048

          environment = [
            {
              name  = "HOST"
              value = "0.0.0.0"
            },
            {
              name  = "PORT"
              value = "8386"
            },
            {
              name  = "WORKERS"
              value = "1"
            },
            {
              name  = "ENVIRONMENT"
              value = "PRODUCTION"
            },
            {
              name  = "AWS_REGION_NAME"
              value = local.region
            },
            {
              name  = "OPENSEARCH_DOMAIN",
              value = var.opensearch_domain
            }
          ]

          secrets = [
            {
              name      = "OPENAI_API_KEY"
              valueFrom = data.aws_ssm_parameter.production_openai_api_key.arn
            },
            {
              name      = "FIRECRAWL_API_KEY"
              valueFrom = data.aws_ssm_parameter.production_firecrawl_api_key.arn
            }
          ]

          log_configuration = {
            logDriver = "awslogs"
            options = {
              "awslogs-group"         = aws_cloudwatch_log_group.backend_task_log_group.name
              "awslogs-region"        = local.region
              "awslogs-stream-prefix" = "ecs"
            }
          }
        }
      }

      task_iam_role_name         = "${local.name}-tasks"
      tasks_iam_role_description = "Tasks IAM role for ${local.name}"
      tasks_iam_role_policies = {
        DynamoDBTablesAccess = aws_iam_policy.dynamodb_tables_access.arn
        OpenSearchAccess     = aws_iam_policy.opensearch_access.arn
      }

      service_connect_configuration = {
        namespace = aws_service_discovery_http_namespace.this.arn
        service = {
          client_alias = {
            port     = local.container_port
            dns_name = local.container_name
          }
          port_name      = local.container_name
          discovery_name = local.container_name
        }
      }

      load_balancer = {
        service = {
          target_group_arn = module.alb.target_groups["ex_ecs"].arn
          container_name   = local.container_name
          container_port   = local.container_port
        }
      }

      subnet_ids = var.vpc_public_subnets

      security_group_rules = {
        alb_ingress_3000 = {
          type                     = "ingress"
          from_port                = local.container_port
          to_port                  = local.container_port
          protocol                 = "tcp"
          description              = "Service port"
          source_security_group_id = module.alb.security_group_id
        }
        egress_all = {
          type        = "egress"
          from_port   = 0
          to_port     = 0
          protocol    = "-1"
          cidr_blocks = ["0.0.0.0/0"]
        }
      }
    }
  }

  depends_on = [aws_iam_policy.parameter_access]

  tags = {
    Environment = "production"
  }
}


# SUPPORTING RESOURCES


# ALB
module "alb" {
  source  = "terraform-aws-modules/alb/aws"
  version = "~> 9.0"

  name = local.name

  load_balancer_type = "application"

  vpc_id  = var.vpc_id
  subnets = var.vpc_public_subnets

  enable_deletion_protection = true

  # Security Group
  security_group_ingress_rules = {
    all_http = {
      from_port   = 80
      to_port     = 80
      ip_protocol = "tcp"
      cidr_ipv4   = "0.0.0.0/0"
    }
  }
  security_group_egress_rules = {
    all = {
      ip_protocol = "-1"
      cidr_ipv4   = var.vpc_cidr
    }
  }

  listeners = {
    ex_http = {
      port     = 80
      protocol = "HTTP"

      forward = {
        target_group_key = "ex_ecs"
      }
    }
  }

  target_groups = {
    ex_ecs = {
      backend_protocol                  = "HTTP"
      backend_port                      = local.container_port
      target_type                       = "ip"
      deregistration_delay              = 5
      load_balancing_cross_zone_enabled = true

      health_check = {
        enabled             = true
        healthy_threshold   = 2
        interval            = 300
        matcher             = "200"
        path                = "/healthcheck"
        port                = "traffic-port"
        protocol            = "HTTP"
        timeout             = 5
        unhealthy_threshold = 2
      }

      # There's nothing to attach here in this definition. Instead,
      # ECS will attach the IPs of the tasks to this target group
      create_attachment = false
    }
  }

  tags = local.tags
}

# Service Discovery
resource "aws_service_discovery_http_namespace" "this" {
  name        = local.name
  description = "CloudMap namespace for ${local.name}"
  tags        = local.tags
}

# Create the custom policy first
resource "aws_iam_policy" "parameter_access" {
  name = "${local.name}-ssm-parameter-access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ssm:GetParameter",
          "ssm:GetParameters",
        ]
        Resource = [
          data.aws_ssm_parameter.production_openai_api_key.arn,
          data.aws_ssm_parameter.production_firecrawl_api_key.arn,
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "dynamodb_tables_access" {
  name = "${local.name}-dynamodb-tables-access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "dynamodb:GetItem",
          "dynamodb:Query",
          "dynamodb:PutItem",
          "dynamodb:BatchGetItem"
        ]
        Resource = [
          data.aws_dynamodb_table.properties.arn,
          data.aws_dynamodb_table.chat_checkpoints.arn,
          data.aws_dynamodb_table.user_message_logs.arn,
          "${data.aws_dynamodb_table.properties.arn}/index/*",
        ]
      }
    ]
  })
}

resource "aws_iam_policy" "opensearch_access" {
  name = "${local.name}-opensearch-access"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "es:ESHttp*"
        ]
        Resource = [
          "${var.opensearch_domain_arn}/*"
        ]
      }
    ]
  })
}

# CloudWatch Log Group
resource "aws_cloudwatch_log_group" "backend_task_log_group" {
  name              = "/ecs-task/${local.container_name}"
  retention_in_days = 30

  tags = local.tags
}
