output "api_url" {
  value = aws_lambda_function_url.api.function_url
}

output "lambda_invoke_arn" {
  value = aws_lambda_function.api.invoke_arn
}
