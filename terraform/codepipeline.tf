resource "aws_codepipeline" "video-to-text-pipeline" {
  name     = "video-to-text-pipeline"
  role_arn = aws_iam_role.codepipeline_role.arn

  artifact_store {
    location = aws_s3_bucket.codepipeline_bucket.bucket
    type     = "S3"

    # encryption_key {
    #   id   = data.aws_kms_alias.s3kmskey.arn
    #   type = "KMS"
    # }
  }

  stage {
    name = "Source"

    action {
      name             = "Source"
      category         = "Source"
      owner            = "AWS"
      provider         = "ECR"
      version          = "1"
      output_artifacts = ["source_output"]

      configuration = {
        RepositoryName = aws_ecr_repository.video-to-text.name
        ImageTag       = "latest"
      }
    }
    action {
      name             = "GitHubSource"
      category         = "Source"
      owner            = "AWS"
      provider         = "CodeStarSourceConnection"
      version          = "1"
      output_artifacts = ["github_output"]

      configuration = {
        ConnectionArn    = aws_codestarconnections_connection.VideoToText.arn
        FullRepositoryId = "stwins60/VideoToText"
        BranchName       = "master"
      }
    }
  }


  stage {
    name = "Build"

    action {
      name             = "Build"
      category         = "Build"
      owner            = "AWS"
      provider         = "CodeBuild"
      input_artifacts  = ["source_output"]
      output_artifacts = ["build_output"]
      version          = "1"

      configuration = {
        ProjectName = "${aws_codebuild_project.video-to-text.name}"
      }
    }
  }
  depends_on = [
    aws_eks_cluster.video-to-text-cluster
  ]
}
#   stage {
#     name = "Deploy"

#     action {
#       name            = "Deploy"
#       category        = "Deploy"
#       owner           = "AWS"
#       provider        = "CloudFormation"
#       input_artifacts = ["build_output"]
#       version         = "1"

#       configuration = {
#         ActionMode     = "REPLACE_ON_FAILURE"
#         Capabilities   = "CAPABILITY_AUTO_EXPAND,CAPABILITY_IAM"
#         OutputFileName = "CreateStackOutput.json"
#         StackName      = "MyStack"
#         TemplatePath   = "build_output::sam-templated.yaml"
#       }
#     }
#   }


resource "aws_codestarconnections_connection" "VideoToText" {
  name          = "video-to-text-connection"
  provider_type = "GitHub"
}

resource "aws_s3_bucket" "codepipeline_bucket" {
  bucket = "video-to-text-bucket"
}

resource "aws_s3_bucket_acl" "codepipeline_bucket_acl" {
  bucket = aws_s3_bucket.codepipeline_bucket.id
  acl    = "private"
}

resource "aws_iam_role" "codepipeline_role" {
  name = "video-to-text-codepipeline-role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "codepipeline.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "codepipeline_policy" {
  name = "codepipeline_policy"
  role = aws_iam_role.codepipeline_role.id

  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "s3:GetObject",
          "s3:GetObjectVersion",
          "s3:GetBucketVersioning",
          "s3:PutObjectAcl",
          "s3:PutObject"
        ],
        "Resource" : [
          "${aws_s3_bucket.codepipeline_bucket.arn}",
          "${aws_s3_bucket.codepipeline_bucket.arn}/*"
        ]
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "codestar-connections:UseConnection"
        ],
        "Resource" : "${aws_codestarconnections_connection.VideoToText.arn}"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "codebuild:BatchGetBuilds",
          "codebuild:StartBuild"
        ],
        "Resource" : "*"
      }
    ]
  })
}

# data "aws_kms_alias" "s3kmskey" {
#   name = "alias/myKmsKey"
# }