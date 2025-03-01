# Data source para obter a AMI ECS Otimizada para GPU
data "aws_ami" "ecs_optimized_gpu" {
  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-hvm-*-x86_64-ebs"]
  }
  owners      = ["amazon"]
  most_recent = true
}

resource "aws_launch_template" "ecs_gpu" {
  name_prefix   = "ecs-r5-"
  image_id      = data.aws_ami.ecs_optimized.id
  instance_type = "r5.2xlarge"  # Instância com 8 vCPUs e 64GB de RAM

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


# Auto Scaling Group para gerenciar as instâncias EC2 GPU
resource "aws_autoscaling_group" "ecs_gpu_asg" {
  desired_capacity     = 1
  max_size             = 1
  min_size             = 1

  launch_template {
    id      = aws_launch_template.ecs_gpu.id
    version = "$Latest"
  }

  vpc_zone_identifier = [aws_subnet.private_subnet.id]

  tag {
    key                 = "Name"
    value               = "ecs-gpu-instance"
    propagate_at_launch = true
  }
}
