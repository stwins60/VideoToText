resource "aws_iam_role" "video-to-text-role" {
  name               = "video-to-text-role"
  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "codebuild.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    },
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "AWS": [
        "${aws_iam_role.codepipeline_role.arn}"
        ]
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy" "video-to-text-policy" {
  role = aws_iam_role.video-to-text-role.name
  policy = jsonencode({
    "Version" : "2012-10-17",
    "Statement" : [
      {
        "Effect" : "Allow",
        "Action" : [
          "ec2:CreateNetworkInterface",
          "ec2:DescribeDhcpOptions",
          "ec2:DescribeNetworkInterfaces",
          "ec2:DeleteNetworkInterface",
          "ec2:DescribeSubnets",
          "ec2:DescribeSecurityGroups",
          "ec2:DescribeVpcs"
        ],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "ec2:CreateNetworkInterfacePermission"
        ],
        "Resource" : [
          "arn:aws:ec2:${var.region}:${var.aws_account_id}:network-interface/*"
        ],
        "Condition" : {
          "StringEquals" : {
            "ec2:Subnet" : [
              "arn:aws:ec2:${var.region}:${var.aws_account_id}:${var.aws_subnet_id_1}",
              "arn:aws:ec2:${var.region}:${var.aws_account_id}:${var.aws_subnet_id_2}",
              "arn:aws:ec2:${var.region}:${var.aws_account_id}:${var.aws_subnet_id_3}"
            ],
            "ec2:AuthorizedService" : "codebuild.amazonaws.com"
          }
        }
      },
      # add log stream
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:DescribeLogStreams",
          "logs:DescribeLogGroups"
        ],
        "Resource" : "*"
      },
      {
        "Effect" : "Allow",
        "Action" : [
          "logs:GetLogEvents"
        ],
        "Resource" : [
          "*"
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "eks_cluster_role_policy" {
  role       = "arn:aws:iam::${var.aws_account_id}:role/eksClusterRole"
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSClusterPolicy"
}

resource "aws_iam_role_policy_attachment" "eks_node_group_policy" {
  role       = "arn:aws:iam::${var.aws_account_id}:role/EKSworkerNodePolicy"
  count      = length(var.managed_policies)
  policy_arn = element(var.managed_policies, count.index)
}

resource "aws_iam_role_policy_attachment" "eks_service_role_eks_node_group_policy" {
  role       = "arn:aws:iam::${var.aws_account_id}:role/aws-service-role/eks-nodegroup.amazonaws.com/AWSServiceRoleForAmazonEKSNodegroup"
  policy_arn = "arn:aws:iam::aws:policy/AmazonServiceRoleForAmazonEKSNodeGroup"
}

resource "aws_iam_role_policy_attachment" "eks_service_role_amazon_eks" {
  role       = "arn:aws:iam::${var.aws_account_id}:role/aws-service-role/eks.amazonaws.com/AWSServiceRoleForAmazonEKS"
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSServicePolicy"
}

