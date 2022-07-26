variable "region" {
  type    = string
  default = "us-east-2"
}
variable "availability_zone" {
  type    = string
  default = "us-east-2a"
}
variable "aws_account_id" {
  type = string
}

variable "aws_image_tag" {
  type    = string
  default = "latest"
}
variable "aws_subnet_id_1" {
  type    = string
  default = ""

}

variable "aws_subnet_id_2" {
  type    = string
  default = ""
}

variable "aws_subnet_id_3" {
  type    = string
  default = ""
}

variable "aws_eks_cluster" {
  type    = string
  default = "video-to-text"
}

variable "aws_code_build" {
  type    = string
  default = "video-to-text_codebuild"
}

variable "secondary_sources" {
  type = list(object(
    {
      git_clone_depth     = number
      location            = string
      source_identifier   = string
      type                = string
      fetch_submodules    = bool
      insecure_ssl        = bool
      report_build_status = bool
  }))
  default     = []
  description = "(Optional) secondary source for the codebuild project in addition to the primary location"
}

variable "private_repository" {
  type        = bool
  default     = true
  description = "Set to true to login into private repository with credentials supplied in source_credential variable."
}

variable "source_location" {
  type    = string
  default = "https://github.com/stwins60/VideoToText.git"
}

variable "github_token" {
  type = string
}

variable "source_credential_user_name" {
  type    = string
  default = "stwins60"
}

variable "aws_code_pipeline" {
  type    = string
  default = "video-to-text_codepipeline"
}

variable "managed_policies" {
  default = [
    "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
    "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
  ]
}