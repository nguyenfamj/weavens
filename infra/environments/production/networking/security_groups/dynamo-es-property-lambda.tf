resource "aws_security_group" "dynamo_es_property_lambda_sg" {
  name        = "dynamo-es-property-sync-sg"
  description = "Security group for DynamoDB to OpenSearch Lambda sync"
  vpc_id      = var.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = var.tags
}

output "dynamo_es_property_lambda_sg_id" {
  value = aws_security_group.dynamo_es_property_lambda_sg.id
}
