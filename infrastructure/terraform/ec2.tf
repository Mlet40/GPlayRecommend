# Data source para obter a AMI ECS Otimizada (padrão, não GPU)
data "aws_ami" "ecs_optimized" {
  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-hvm-*-x86_64-ebs"]
  }
  owners      = ["amazon"]
  most_recent = true
}

resource "aws_launch_template" "ecs_standard" {
  name_prefix   = "ecs-standard-"
  image_id      = data.aws_ami.ecs_optimized.id
  instance_type = "c5.4xlarge"  # Instância rápida e adequada para TF-IDF

  iam_instance_profile {
    name = aws_iam_instance_profile.ecs_instance_profile.name
  }

  user_data = base64encode(<<EOF
#!/bin/bash
echo ECS_CLUSTER=${aws_ecs_cluster.this.name} >> /etc/ecs/ecs.config
EOF
  )

  vpc_security_group_ids = [aws_security_group.ecs_task_sg.id]
}

# Auto Scaling Group para gerenciar as instâncias EC2 padrão
resource "aws_autoscaling_group" "ecs_standard_asg" {
  desired_capacity     = 1
  max_size             = 1
  min_size             = 1

  launch_template {
    id      = aws_launch_template.ecs_standard.id
    version = "$Latest"
  }

  vpc_zone_identifier = [aws_subnet.private_subnet.id]

  tag {
    key                 = "Name"
    value               = "ecs-standard-instance"
    propagate_at_launch = true
  }
}
