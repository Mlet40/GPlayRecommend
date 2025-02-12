resource "aws_s3_bucket" "datalake" {
  bucket = var.bucket_name
  tags = {
    Name = "Datalake Bucket"
    Environment = "Development"
  }
}

# habilita que eventos do S3 sejam enviados para EventBridge
resource "aws_s3_bucket_notification" "enable_eventbridge" {
  bucket = aws_s3_bucket.datalake.id

  eventbridge = true
}

# opcional: cria a “raw/” folder
resource "aws_s3_object" "raw_folder" {
  bucket = aws_s3_bucket.datalake.id
  key    = "raw/"
}
