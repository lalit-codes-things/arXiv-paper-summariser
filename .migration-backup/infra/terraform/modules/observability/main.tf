variable "cluster_name" { type = string }
variable "environment" { type = string }
variable "audit_log_retention_days" { type = number }

resource "aws_cloudwatch_log_group" "eks" {
  name              = "/aws/eks/${var.cluster_name}/${var.environment}"
  retention_in_days = 365
}

resource "aws_cloudwatch_log_group" "audit" {
  name              = "/arxiv/${var.cluster_name}/${var.environment}/audit"
  retention_in_days = var.audit_log_retention_days
}

output "audit_log_group" {
  value = aws_cloudwatch_log_group.audit.name
}
