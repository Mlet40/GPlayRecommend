resource "aws_ecs_task_definition" "featstore_task" {
  family                   = "featstore-task-2"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "2048"    # 0.5 vCPU
  memory                   = "16384"   # 4GB de memória
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

resource "aws_ecs_task_definition" "trainningmodel_task" {
  family                   = "trainning-task"
  container_definitions    = jsonencode([
    {
      name      = "trainningmodel-container"
      image     = "${var.trainning_docker_image}"
      cpu       = 256
      memory    = 512
      essential = true
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/trainningmodel"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  memory                   = "512"
  cpu                      = "256"
  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  task_role_arn       = aws_iam_role.ecs_task_role.arn
}


resource "aws_ecs_task_definition" "recommend-api-task" {
  family                   = "recommend-api-task"
  container_definitions    = jsonencode([
    {
      name      = "recommend-api-container"
      image     = "${var.recommend_api_docker_image}"
      cpu       = 256
      memory    = 512
      essential = true
	  portMappings = [
        {
          containerPort = 5000  # Essa linha é ESSENCIAL!
          hostPort      = 5000
          protocol      = "tcp"
        }
      ]
      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = "/ecs/recommend_api"
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "ecs"
        }
      }
    }
  ])
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  memory                   = "512"
  cpu                      = "256"
  execution_role_arn = aws_iam_role.ecs_execution_role.arn
  task_role_arn       = aws_iam_role.ecs_task_role.arn
}

