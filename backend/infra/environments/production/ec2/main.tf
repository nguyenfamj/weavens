module "key_pair" {
  source = "terraform-aws-modules/key-pair/aws"

  key_name   = "crux-key-pair"
  public_key = file("~/.ssh/id_rsa.pub")

  tags = {
    Environment = "production"
    Terraform   = true
  }
}


module "ec2-instance" {
  source = "terraform-aws-modules/ec2-instance/aws"

  name = "crux-ec2-instance"

  associate_public_ip_address = true
  key_name                    = module.key_pair.key_pair_name

  instance_type          = "t3.micro"
  vpc_security_group_ids = [var.default_security_group_id]
  subnet_id              = var.public_subnet_ids[0]

  tags = {
    Environment = "production"
    Terraform   = true
  }
}
