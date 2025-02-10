variable "aws_region" {
  description = "Região AWS para provisionamento dos recursos"
  default     = "us-east-1"
}

variable "bucket_name" {
  description = "Nome do bucket S3"
  default     = "globoplayDatalake"
}
