output "cluster_name" {
  value = module.eks.cluster_name
}

output "vpc_id" {
  value = module.networking.vpc_id
}

output "papers_bucket" {
  value = aws_s3_bucket.papers.bucket
}

output "audit_bucket" {
  value = aws_s3_bucket.audit.bucket
}

output "postgres_endpoint" {
  value     = module.postgres.endpoint
  sensitive = true
}

output "redis_endpoint" {
  value     = module.redis.endpoint
  sensitive = true
}
