resource "aws_vpc" "video-to-text-vpc" {
  cidr_block = "10.0.0.0/24"
  tags = {
    Name = "video-to-text-vpc"
  }
  instance_tenancy = "default"

}