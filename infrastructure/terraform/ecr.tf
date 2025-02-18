resource "aws_ecr_repository" "globo_recommend" {
  name = "globo_recommend"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Environment = "Development"
  }
}
