resource "aws_ecr_repository" "featurestoreengine" {
  name = "featurestore"
  image_tag_mutability = "MUTABLE"
  image_scanning_configuration {
    scan_on_push = true
  }
  tags = {
    Environment = "Development"
  }
}