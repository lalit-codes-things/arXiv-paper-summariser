variable "cluster_name" { type = string }
variable "environment" { type = string }
variable "subnet_ids" { type = list(string) }
variable "vpc_id" { type = string }

resource "aws_elasticache_subnet_group" "this" {
  name       = "${var.cluster_name}-${var.environment}"
  subnet_ids = var.subnet_ids
}

resource "aws_security_group" "redis" {
  name   = "${var.cluster_name}-${var.environment}-redis"
  vpc_id = var.vpc_id
}

resource "aws_elasticache_replication_group" "this" {
  replication_group_id       = "${var.cluster_name}-${var.environment}"
  description                = "V17 queue and cache tier"
  engine                     = "redis"
  node_type                  = "cache.m6g.large"
  num_cache_clusters         = 2
  automatic_failover_enabled = true
  at_rest_encryption_enabled = true
  transit_encryption_enabled = true
  subnet_group_name          = aws_elasticache_subnet_group.this.name
  security_group_ids         = [aws_security_group.redis.id]
}

output "endpoint" {
  value = aws_elasticache_replication_group.this.primary_endpoint_address
}
