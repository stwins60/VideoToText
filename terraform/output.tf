output "endpoint" {
  value = aws_eks_cluster.video-to-text-cluster.endpoint
}
output "kubeconfig-certificate" {
  value = aws_eks_cluster.video-to-text-cluster.certificate_authority[0].data
}