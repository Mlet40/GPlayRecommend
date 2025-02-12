resource "aws_ecs_task_definition" "featstore_task" {
  family                   = "featstore-task"
  requires_compatibilities = ["FARGATE"]
  cpu                      = 256
  memory                   = 512
  network_mode             = "awsvpc"

  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  task_role_arn       = aws_iam_role.ecs_task_role.arn

  container_definitions = <<DEFS
[
  {
    "name": "featstore-container",
    "image": "${var.my_docker_image}",
    "essential": true,
    "logConfiguration": {
      "logDriver": "awslogs",
      "options": {
        "awslogs-region": "${var.aws_region}",
        "awslogs-group": "/ecs/featstore",
        "awslogs-stream-prefix": "ecs"
      }
    }
  }
]
DEFS
}
