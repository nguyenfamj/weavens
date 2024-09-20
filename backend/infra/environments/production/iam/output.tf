resource "local_file" "iam_nova_developer_user_credentials" {
  content = templatefile("${path.module}/templates/user_credentials.tmpl", {
    username = module.iam_nova_developer.iam_user_name
    password = module.iam_nova_developer.iam_user_login_profile_password
  })
  filename = "${path.module}/nova_developer_credentials.txt"
}
