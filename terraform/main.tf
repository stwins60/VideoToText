
resource "aws_ecr_repository" "video-to-text" {
  name = "video-to-text"
  image_scanning_configuration {
    scan_on_push = true

  }
}

resource "aws_ecr_repository_policy" "video-to-text-policy" {
  repository = aws_ecr_repository.video-to-text.name
  policy     = <<EOF
    {
    "Version": "2008-10-17",
    "Statement": [
        {
            "Sid": "Adds the Docker repository policy to the repository",
            "Effect": "Allow",
            "Principal": "*",
            "Action": [
                "ecr:GetDownloadUrlForLayer",
                "ecr:BatchGetImage",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetLayers",
                "ecr:DescribeImages",
                "ecr:DescribeRepositories",
                "ecr:ListImages",
                "ecr:PutImage",
                "ecr:InspectImage",
                "ecr:GetLifecyclePolicy",
                "ecr:CompleteLayerUpload",
                "ecr:InitiateLayerUpload",
                "ecr:GetDownloadAuthorization",
                "ecr:BatchGetImage"
                ]
        }
    ]
    
    }
    EOF
}

resource "aws_default_subnet" "aws_default_subnet" {
  availability_zone = var.availability_zone

  tags = {
    Name = "Default subnet for ${var.region}"
  }
}
