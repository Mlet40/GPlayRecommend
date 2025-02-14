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

resource "aws_ecr_repository" "trainningmodel" {
  name                 = "trainningmodel"
  image_tag_mutability = "MUTABLE"
  lifecycle {
    prevent_destroy = false
  }
}
