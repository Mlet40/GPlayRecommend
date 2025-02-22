resource "aws_ecs_service" "recommend_api_service" {
  name            = "recommend-api-service"
  cluster         = aws_ecs_cluster.this.id
  task_definition = aws_ecs_task_definition.recommend-api-task.arn
  launch_type     = "FARGATE"

  desired_count   = 1 # Mantém pelo menos 1 Task rodando sempre!
  enable_execute_command = true
  network_configuration {
    subnets         = [aws_subnet.public_subnet.id]
    security_groups = [aws_security_group.ecs_sg.id]
    assign_public_ip = true
  }

  load_balancer {
    target_group_arn = aws_lb_target_group.recommend_api_tg.arn
    container_name   = "recommend-api-container" #  O mesmo nome definido na Task Definition
    container_port   = 5000
  }

  depends_on = [aws_lb_listener.http]
}
