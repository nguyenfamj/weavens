module "vpc" {
  source = "terraform-aws-modules/vpc/aws"

  name = "crux-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["eu-north-1a"]
  private_subnets = ["10.0.1.0/24"]
  public_subnets  = ["10.0.101.0/24"]

  default_security_group_ingress = [
    {
      from_port   = 443
      to_port     = 443
      protocol    = "tcp"
      cidr_blocks = "0.0.0.0/0"
    },
    {
      from_port   = 22
      to_port     = 22
      protocol    = "tcp"
      cidr_blocks = "0.0.0.0/0"
    }
  ]

  tags = {
    Environment = "production"
    Terraform   = true
  }
}
