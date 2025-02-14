resource "aws_ecr_repository" "featurestoreengine" {
  name = "featurestoreengine"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Environment = "Development"
  }
}