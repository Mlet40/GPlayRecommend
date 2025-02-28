# Data source para obter a AMI ECS Otimizada para GPU
data "aws_ami" "ecs_gpu" {
  filter {
    name   = "name"
    values = ["amzn2-ami-ecs-gpu-*"]
  }
  owners      = ["amazon"]
  most_recent = true
}

resource "aws_launch_template" "ecs_gpu" {
  name_prefix   = "ecs-gpu-"
  image_id      = data.aws_ami.ecs_gpu.id
  instance_type = "g4dn.xlarge"

  iam_instance_profile {
    name = aws_iam_instance_profile.ecs_instance_profile.name
  }

  #instance_market_options {
  #  market_type = "spot"
   
  #  spot_options {
  #    instance_interruption_behavior = "terminate"
      #max_price                    = "0.50"  # opcional: define o preço máximo que você está disposto a pagar
  #  }
  #}

  user_data = base64encode(<<EOF
#!/bin/bash
echo ECS_CLUSTER=${aws_ecs_cluster.this.name} >> /etc/ecs/ecs.config
EOF
  )

   vpc_security_group_ids = [aws_security_group.ecs_task_sg.id]
}


# Auto Scaling Group para gerenciar as instâncias EC2 com GPU
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
