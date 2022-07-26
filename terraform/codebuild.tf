resource "aws_codebuild_source_credential" "authorization" {
  auth_type   = "PERSONAL_ACCESS_TOKEN"
  server_type = "GITHUB"
  token       = var.github_token
  user_name   = var.source_credential_user_name
}

resource "aws_codebuild_project" "video-to-text" {
  name         = var.aws_code_build
  service_role = aws_iam_role.video-to-text-role.arn

  environment {
    type                        = "LINUX_CONTAINER"
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/amazonlinux2-x86_64-standard:2.0"
    privileged_mode             = true
    image_pull_credentials_type = "CODEBUILD"
    environment_variable {
      name  = "AWS_DEFAULT_REGION"
      value = var.region
    }
    environment_variable {
      name  = "ACCOUNT_ID"
      value = var.aws_account_id
    }
    environment_variable {
      name  = "REPOSITORY_URI"
      value = aws_ecr_repository.video-to-text.name
    }
    environment_variable {
      name  = "CLUSTER_NAME"
      value = var.aws_eks_cluster
    }


    # variables = {
    #   "AWS_DEFAULT_REGION" = var.region
    #   "ACCOUNT_ID" = var.aws_account_id
    #   "REPOSITORY_URI" = aws_ecr_repository.video-to-text.name
    #   "CLUSTER_NAME" = var.aws_eks
    # }
  }
  source {
    buildspec       = "./buildspec.yml"
    type            = "CODEPIPELINE"
    location        = var.source_location
    git_clone_depth = 1
    dynamic "auth" {
      for_each = var.private_repository ? [""] : []
      content {
        type     = "OAUTH"
        resource = join("", aws_codebuild_source_credential.authorization.*.id)
      }
    }
    git_submodules_config {
      fetch_submodules = true
    }
  }
  dynamic "secondary_sources" {
    for_each = var.secondary_sources
    content {
      type              = "ECR"
      location          = aws_ecr_repository.video-to-text.name
      git_clone_depth   = 1
      source_identifier = aws_ecr_repository.video-to-text.name
      git_submodules_config {
        fetch_submodules = true
      }
    }
  }
  artifacts {
    type = "CODEPIPELINE"
    name = "video-to-text-artifacts"
  }
  #   {
  #     type              = "GITHUB"
  #     location = "https://github.com/stwins60/VideoToText.git"
  #     git_clone_depth = 1
  #     source_identifier = "video-to-text"
  #   }
  # ]

  # codebuild_source_version = "master"
  # tags = {
  #   Name = "VideoToText"
  #   Environment = "Production"
  # }
  depends_on = [
    aws_eks_cluster.video-to-text-cluster,
    aws_codebuild_source_credential.authorization,
  ]
}