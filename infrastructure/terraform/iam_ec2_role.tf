# Definindo a política de confiança para a instância EC2
data "aws_iam_policy_document" "ecs_instance_assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

# Criando o Role para as instâncias ECS
resource "aws_iam_role" "ecs_instance_role" {
  name               = "ecsInstanceRole"
  assume_role_policy = data.aws_iam_policy_document.ecs_instance_assume_role_policy.json
}

# Anexando a política necessária para as instâncias ECS
resource "aws_iam_role_policy_attachment" "ecs_instance_role_policy" {
  role       = aws_iam_role.ecs_instance_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonEC2ContainerServiceforEC2Role"
}

# Criando o Instance Profile para as instâncias ECS
resource "aws_iam_instance_profile" "ecs_instance_profile" {
  name = "ecsInstanceProfile"
  role = aws_iam_role.ecs_instance_role.name
}

resource "aws_iam_policy" "sagemaker_ec2_describe_subnets" {
  name        = "SageMakerEC2DescribeSubnets"
  description = "Permite que o role do SageMaker execute ec2:DescribeSubnets"
  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Allow",
        "Action": "ec2:DescribeSubnets",
        "Resource": "*"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sagemaker_subnets_attachment" {
  role       = "AmazonSageMakerServiceCatalogProductsUseRole"
  policy_arn = aws_iam_policy.sagemaker_ec2_describe_subnets.arn
}
