resource "aws_cloudwatch_event_target" "ecs_run_task_target" {
  rule      = aws_cloudwatch_event_rule.s3_object_created_rule.name
  target_id = "featstore-fargate-run"
  arn       = aws_ecs_cluster.this.arn

  role_arn = aws_iam_role.eventbridge_invoke_ecs.arn

  ecs_target {
    launch_type     = "FARGATE"
    task_definition_arn = aws_ecs_task_definition.featstore_task.arn

    network_configuration {
      subnets          = [aws_subnet.private_subnet.id]
      assign_public_ip = true
    }

    platform_version = "1.4.0"
  }
}
