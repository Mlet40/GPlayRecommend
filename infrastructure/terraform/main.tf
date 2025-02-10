resource "aws_s3_bucket" "datalake" {
  bucket = var.bucket_name

  tags = {
    Name = "Datalake Bucket"
    Environment = "Development"
  }
}

resource "aws_s3_bucket_object" "raw_folder" {
  bucket = aws_s3_bucket.datalake.id
  key    = "raw/"
}

resource "aws_s3_bucket_object" "processed_folder" {
  bucket = aws_s3_bucket.datalake.id
  key    = "processed/"
}

resource "aws_s3_bucket_object" "raw_folder" {
  bucket = aws_s3_bucket.datalake.id
  key    = "gold/"
}
