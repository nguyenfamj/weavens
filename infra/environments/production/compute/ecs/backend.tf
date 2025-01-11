locals {
  name           = "${var.environment}-backend-ecs"
  container_name = "ecs-backend"
  container_port = 8386

  task_environment = {
    AWS_REGION_NAME = "eu-north-1"
  }
}

data "aws_ecr_repository" "backend_ecr_repository" {
  name = var.ecr_backend_repository_name
}

module "backend_ecs" {
  source = "terraform-aws-modules/ecs/aws"

  cluster_name = local.name

  create_task_exec_iam_role   = true
  task_exec_iam_role_policies = {}

  cluster_configuration = {
    execute_command_configuration = {
      logging = "OVERRIDE"
      log_configuration = {
        cloud_watch_log_group_name = local.name
      }
    }
  }

  default_capacity_provider_use_fargate = false
  autoscaling_capacity_providers = {
    "${local.name}-capacity" = {
      auto_scaling_group_arn         = var.backend_ecs_autoscaling_group_arn
      managed_termination_protection = "ENABLED"

      managed_scaling = {
        maximum_scaling_step_size = 1
        minimum_scaling_step_size = 1
        status                    = "ENABLED"
        target_capacity           = 100
      }

      default_capacity_provider_strategy = {
        base   = 1
        weight = 100
      }
    }
  }

  services = {
    (local.name) = {
      cpu    = 256
      memory = 512

      requires_compatibilities = ["EC2"]
      capacity_provider_strategy = {
        "${local.name}-capacity" = {
          capacity_provider = "${local.name}-capacity"
          weight            = 1
          base              = 1
        }
      }

      volume = {
        shared-volume = {}
      }

      enable_execute_command = true

      deployment_circuit_breaker = {
        enable   = true
        rollback = true
      }

      # Keeping 0% minimum healthy during MVP
      deployment_minimum_healthy_percent = 0
      deployment_maximum_percent         = 100

      container_definitions = {
        (local.container_name) = {
          image = "${data.aws_ecr_repository.backend_ecr_repository.repository_url}:${var.backend_image_version_tag}"

          port_mappings = [
            {
              name          = local.container_name
              containerPort = local.container_port
              hostPort      = local.container_port
              protocol      = "tcp"
            }
          ]

          mount_points = [
            {
              sourceVolume  = "shared-volume",
              containerPath = "/var/www/shared-volume"
            }
          ]

          readonly_root_filesystem = false

          environment = [
            {
              name  = "HOST"
              value = "0.0.0.0"
            },
            {
              name  = "PORT"
              value = local.container_port
            },
            {
              name  = "WORKERS"
              value = "1"
            },
            {
              name  = "ENVIRONMENT"
              value = var.environment
            },
            {
              name  = "AWS_REGION_NAME"
              value = local.task_environment.AWS_REGION_NAME
            },
            # TODO: These two are duplicates, remove one later
            {
              name  = "AWS_REGION",
              value = local.task_environment.AWS_REGION_NAME
            },
            {
              name  = "OPENSEARCH_DOMAIN",
              value = var.opensearch_domain
            },
            {
              name  = "OPENAI_API_KEY"
              value = var.production_openai_api_key
            },
            {
              name  = "FIRECRAWL_API_KEY"
              value = var.production_firecrawl_api_key
            }
          ]

          enable_cloudwatch_logging              = true
          create_cloudwatch_log_group            = true
          cloudwatch_log_group_name              = "/aws/ecs/${local.name}/${local.container_name}"
          cloudwatch_log_group_retention_in_days = 7

          log_configuration = {
            logDriver = "awslogs"
          }
        }
      }

      task_iam_role_name         = "${local.name}-tasks"
      tasks_iam_role_description = "Tasks IAM role for ${local.name}"
      tasks_iam_role_policies = {
        DynamoDBTablesAccess = var.backend_dynamodb_tables_access_policy_arn
        OpenSearchAccess     = var.backend_opensearch_access_policy_arn
      }

      load_balancer = {
        service = {
          target_group_arn = var.backend_ecs_alb_target_group_ex_ecs_arn
          container_name   = local.container_name
          container_port   = local.container_port
        }
      }

      subnet_ids = var.vpc_private_subnets

      security_group_rules = {
        alb_ingress_3000 = {
          type                     = "ingress"
          from_port                = local.container_port
          to_port                  = local.container_port
          protocol                 = "tcp"
          description              = "Service port"
          source_security_group_id = var.backend_ecs_alb_security_group_id
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

  tags = var.tags
}
