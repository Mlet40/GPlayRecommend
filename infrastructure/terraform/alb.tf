resource "aws_lb" "recommend_api_lb" {
  name               = "recommend-api-lb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = [aws_security_group.ecs_sg.id]
  subnets           = [aws_subnet.public_subnet.id, aws_subnet.public_subnet_2.id] # Agora tem 2 subnets!
}

resource "aws_lb_target_group" "recommend_api_tg" {
  name     = "recommend-api-tg"
  port     = 5000
  protocol = "HTTP"
  vpc_id   = aws_vpc.this.id

  health_check {
    path                = "/"
    interval            = 30
    timeout             = 5
    healthy_threshold   = 2
    unhealthy_threshold = 2
  }
}

resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.recommend_api_lb.arn
  port              = 80
  protocol          = "HTTP"

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.recommend_api_tg.arn
  }
}
