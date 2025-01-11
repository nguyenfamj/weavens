locals {
  name             = "${var.environment}-backend-autoscaling"
  ecs_cluster_name = "${var.environment}-backend-ecs"
}

data "aws_ssm_parameter" "ecs_optimized_ami" {
  name = "/aws/service/ecs/optimized-ami/amazon-linux-2/recommended"
}

module "autoscaling" {
  source  = "terraform-aws-modules/autoscaling/aws"
  version = "8.0.1"

  name          = local.name
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

  security_groups = [var.backend_ecs_autoscaling_sg_id]
  user_data = base64encode(<<-EOT
    #!/bin/bash
    set -e

    echo "ECS_CLUSTER=${local.ecs_cluster_name}" >> /etc/ecs/ecs.config
    echo "ECS_LOGLEVEL=debug" >> /etc/ecs/ecs.config
    echo 'ECS_CONTAINER_INSTANCE_TAGS=${jsonencode(var.tags)}' >> /etc/ecs/ecs.config
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

  tags = var.tags
}

# Outputs
output "backend_ecs_autoscaling_group_arn" {
  value = module.autoscaling.autoscaling_group_arn
}
