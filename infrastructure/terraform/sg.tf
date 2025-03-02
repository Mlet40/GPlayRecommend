# Criando Security Group para ECS Fargate
resource "aws_security_group" "ecs_sg" {
  vpc_id = aws_vpc.this.id  # Associação com a VPC

  # Permitir tráfego de entrada na porta 5000
  ingress {
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Permite acesso público (Ajuste conforme necessário)
  }

  # Permitir tráfego de entrada na porta 80
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Permite acesso público (Ajuste conforme necessário)
  }

  # Permitir tráfego de saída irrestrito (ECS precisa acessar internet)
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "globo-ecs-sg"
  }
}

resource "aws_security_group" "ecs_task_sg" {
  name        = "ecs-task-sg"
  description = "Allow HTTPS outbound to VPC Endpoint"
  vpc_id      = aws_vpc.this.id

   egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Security Group para o Redis
resource "aws_security_group" "redis_sg" {
  name        = "redis-sg"
  description = "Security group for Redis ElastiCache"
  vpc_id      = aws_vpc.this.id

  ingress {
    description = "Allow inbound Redis traffic"
    from_port   = 6379
    to_port     = 6379
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]  # Ajuste conforme necessário (recomenda-se restringir)
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "redis-sg"
  }
}

