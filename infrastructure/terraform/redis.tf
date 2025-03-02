
# Grupo de Subnets para o Redis (utilizando a mesma subnet pública que a API)
resource "aws_elasticache_subnet_group" "redis_subnet_group" {
  name       = "redis-subnet-group"
  subnet_ids = [aws_subnet.public_subnet.id]

  tags = {
    Name = "redis-subnet-group"
  }
}


# Cluster ElastiCache Redis
resource "aws_elasticache_cluster" "redis_cluster" {
  cluster_id           = "my-redis-cache"
  engine               = "redis"
  engine_version       = "6.x"
  node_type            = "cache.m6g.2xlarge"  # Essa instância oferece cerca de 16GB de memória
  num_cache_nodes      = 1                  # Cluster com um único nó
  port                 = 6379
  subnet_group_name    = aws_elasticache_subnet_group.redis_subnet_group.name
  security_group_ids   = [aws_security_group.redis_sg.id]

  tags = {
    Name = "my-redis-cache"
  }
}