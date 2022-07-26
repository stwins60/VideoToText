resource "aws_eks_cluster" "video-to-text-cluster" {
  name     = var.aws_eks_cluster
  role_arn = aws_iam_role.video-to-text-role.arn
  vpc_config {
    subnet_ids = [
      "arn:aws:ec2:${var.region}:${var.aws_account_id}:${var.aws_subnet_id_1}",
      "arn:aws:ec2:${var.region}:${var.aws_account_id}:${var.aws_subnet_id_2}",
    ]
  }

  depends_on = [
    aws_iam_role.video-to-text-role,
    aws_iam_role_policy_attachment.eks_cluster_role_policy,
    aws_iam_role_policy_attachment.eks_node_group_policy,
    aws_iam_role_policy_attachment.eks_service_role_eks_node_group_policy,
    aws_iam_role_policy_attachment.eks_service_role_amazon_eks,
  ]
}

resource "aws_eks_node_group" "eks_node_group" {
  cluster_name    = aws_eks_cluster.video-to-text-cluster.name
  node_group_name = "video-to-text-node-group"
  node_role_arn   = aws_iam_role.video-to-text-role.arn
  subnet_ids = [
    "arn:aws:ec2:${var.region}:${var.aws_account_id}:${var.aws_subnet_id_1}",
    "arn:aws:ec2:${var.region}:${var.aws_account_id}:${var.aws_subnet_id_2}",
  ]
  instance_types = [
    "t2.micro",
  ]
  scaling_config {
    desired_size = 1
    max_size     = 1
    min_size     = 1
  }
  update_config {
    max_unavailable = 2
  }
  depends_on = [
    aws_iam_role_policy_attachment.eks_node_group_policy,
    aws_iam_role_policy_attachment.eks_service_role_eks_node_group_policy,
  ]
}
