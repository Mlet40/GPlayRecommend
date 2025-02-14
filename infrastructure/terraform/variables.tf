variable "aws_region" {
  type    = string
  default = "us-east-1"
}

variable "bucket_name" {
  type        = string
  description = "Nome do bucket S3 do datalake"
  default     = "globoplay-datalak"
}

variable "vpc_cidr" {
  type    = string
  default = "10.0.0.0/16"
}

variable "my_docker_image" {
  type        = string
  description = "Imagem Docker para a Task de Feature Store (ex.: ECR repo)"
  default     = "353061803834.dkr.ecr.us-east-1.amazonaws.com/featurestoreengine:latest"
}

