resource "aws_ecs_cluster" "this" {
  name = "featstore-ecs-cluster"
}

resource "aws_ecs_cluster" "trainning" {
  name = "trainning-ecs-cluster"
}
