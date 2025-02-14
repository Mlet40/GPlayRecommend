resource "aws_cloudwatch_log_group" "featstore_lg" {
  name              = "/ecs/featstore"
  retention_in_days = 7
}

resource "aws_cloudwatch_log_group" "trainningmodel_lg" {
  name              = "/ecs/trainningmodel"
  retention_in_days = 7
}


