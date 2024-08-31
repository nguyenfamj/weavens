output "lambda_role_arn" {
  value = aws_iam_role.lambda.arn
}

output "iam_role_policy_attachment" {
  value = aws_iam_role_policy_attachment.lambda_basic_execution
}
