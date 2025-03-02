resource "aws_cloudwatch_log_group" "featstore_log" {
  name              = "/ecs/featstore"
  retention_in_days = 7
}


resource "aws_cloudwatch_log_group" "trainning_log" {
  name              = "/ecs/trainningmodel"
  retention_in_days = 7
}


resource "aws_cloudwatch_log_group" "recommend_api_log" {
  name              = "/ecs/recommend_api"
  retention_in_days = 7
}


resource "aws_cloudwatch_log_group" "eventbridge_logs" {
  name = "/aws/events/trainning-s3-featstore-rule"
  retention_in_days = 7
}

