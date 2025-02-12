output "bucket_datalake_name" {
  description = "Nome do bucket do datalake"
  value       = aws_s3_bucket.datalake.bucket
}


output "ecs_cluster_arn" {
  description = "ARN do ECS Cluster"
  value       = aws_ecs_cluster.this.arn
}

output "eventbridge_rule_name" {
  description = "Nome da Regra do EventBridge"
  value       = aws_cloudwatch_event_rule.s3_object_created_rule.name
}
