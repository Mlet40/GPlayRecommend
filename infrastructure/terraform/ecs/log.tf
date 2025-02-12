resource "aws_logs_log_group" "featstore_lg" {
  name              = "/ecs/featstore"
  retention_in_days = 7
}
