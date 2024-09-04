output "ecr_repo_url" {
  value = local.repo_url
}

output "image" {
  value = null_resource.image
}
