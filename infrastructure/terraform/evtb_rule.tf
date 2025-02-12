resource "aws_cloudwatch_event_rule" "s3_object_created_rule" {
  name        = "featstore-s3-raw-rule"
  description = "Dispara container featstore quando objeto cair no raw"
  event_pattern = <<PATTERN
{
  "source": ["aws.s3"],
  "detail-type": ["Object Created"],
  "detail": {
    "bucket": {
      "name": ["${var.bucket_name}"]
    },
    "object": {
      "key": [{
        "prefix": "raw/"
      }]
    }
  }
}
PATTERN
}
