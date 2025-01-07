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
    ParameterAccess = aws_iam_policy.parameter_access.arn
  }

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
    "production-crux-backend" = {
      auto_scaling_group_arn         = module.autoscaling.autoscaling_group_arn
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
        "production-crux-backend" = {
          capacity_provider = "production-crux-backend"
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
          image = "${var.backend_ecr_repository_url}:${data.aws_ssm_parameter.production_backend_image_tag.value}"

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
              value = "PRODUCTION"
            },
            {
              name  = "AWS_REGION_NAME"
              value = local.region
            },
            # TODO: These two are duplicates, remove one later
            {
              name  = "AWS_REGION",
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
        DynamoDBTablesAccess = aws_iam_policy.dynamodb_tables_access.arn
        OpenSearchAccess     = aws_iam_policy.opensearch_access.arn
      }

      load_balancer = {
        service = {
          target_group_arn = module.alb.target_groups["ex_ecs"].arn
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

  tags = local.tags
}


# SUPPORTING RESOURCES

# Autoscaling
module "autoscaling" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "8.0.1"

  name          = "${local.name}-autoscaling"
  instance_type = "t3.micro"
  image_id      = jsondecode(data.aws_ssm_parameter.ecs_optimized_ami.value)["image_id"]

  ignore_desired_capacity_changes = true

  # use_mixed_instances_policy = true
  # mixed_instances_policy = {
  #   instances_distribution = {
  #     on_demand_base_capacity                  = 0
  #     on_demand_percentage_above_base_capacity = 0
  #     spot_allocation_strategy                 = "price-capacity-optimized"
  #   }

  #   override = [
  #     { instance_type = "t3.micro" },
  #     { instance_type = "t2.micro" },
  #   ]
  # }

  # tag_specifications = [
  #   {
  #     resource_type = "spot-instances-request"
  #     tags          = local.tags
  #   }
  # ]

  security_groups = [module.autoscaling_sg.security_group_id]
  user_data = base64encode(<<-EOT
    #!/bin/bash
    set -e

    echo "ECS_CLUSTER=${local.name}" >> /etc/ecs/ecs.config
    echo "ECS_LOGLEVEL=debug" >> /etc/ecs/ecs.config
    echo 'ECS_CONTAINER_INSTANCE_TAGS=${jsonencode(local.tags)}' >> /etc/ecs/ecs.config
    echo "ECS_ENABLE_TASK_IAM_ROLE=true" >> /etc/ecs/ecs.config
  EOT
  )


  create_iam_instance_profile = true
  iam_role_name               = local.name
  iam_role_description        = "ECS role for ${local.name}"
  iam_role_policies = {
    AmazonEC2ContainerServiceforEC2Role = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
    AmazonSSMManagedInstanceCore        = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
    AmazonEC2RoleforSSM                 = "arn:aws:iam::aws:policy/service-role/AmazonEC2RoleforSSM"
  }

  vpc_zone_identifier = var.vpc_private_subnets
  health_check_type   = "EC2"
  min_size            = 1
  max_size            = 1
  desired_capacity    = 1

  autoscaling_group_tags = {
    AmazonECSManaged = true
  }

  protect_from_scale_in = true

  tags = local.tags
}


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

    all_https = {
      from_port   = 443
      to_port     = 443
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

    ex_https = {
      port     = 443
      protocol = "HTTPS"

      ssl_policy      = "ELBSecurityPolicy-2016-08"
      certificate_arn = aws_acm_certificate.self_signed_cert.arn
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

# Autoscaling Security Group
module "autoscaling_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "5.2.0"

  name        = local.name
  description = "Autoscaling group security group"
  vpc_id      = var.vpc_id

  computed_ingress_with_source_security_group_id = [
    {
      rule                     = "http-80-tcp"
      source_security_group_id = module.alb.security_group_id
    }
  ]
  number_of_computed_ingress_with_source_security_group_id = 1

  egress_rules = ["all-all"]

  tags = local.tags
}

# Self-signed certificate for HTTPS
resource "tls_private_key" "self_signed_cert" {
  algorithm = "RSA"
}

resource "tls_self_signed_cert" "self_signed_cert" {
  private_key_pem = tls_private_key.self_signed_cert.private_key_pem

  subject {
    common_name  = "titan.co"
    organization = "Titan OY"
  }

  validity_period_hours = 8760

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth"
  ]
}

resource "aws_acm_certificate" "self_signed_cert" {
  private_key      = tls_private_key.self_signed_cert.private_key_pem
  certificate_body = tls_self_signed_cert.self_signed_cert.cert_pem
  tags             = local.tags
}
