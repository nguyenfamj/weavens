locals {
  name = "${var.environment}-backend-autoscaling"
}

module "autoscaling_sg" {
  source  = "terraform-aws-modules/security-group/aws"
  version = "5.2.0"

  name        = local.name
  description = "Autoscaling group security group"
  vpc_id      = var.vpc_id

  computed_ingress_with_source_security_group_id = [
    {
      rule                     = "http-80-tcp"
      source_security_group_id = var.backend_ecs_alb_security_group_id
    }
  ]
  number_of_computed_ingress_with_source_security_group_id = 1

  egress_rules = ["all-all"]

  tags = var.tags
}

output "backend_ecs_autoscaling_security_group_id" {
  value = module.autoscaling_sg.security_group_id
}
