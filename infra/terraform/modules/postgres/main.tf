variable "cluster_name" { type = string }
variable "environment" { type = string }
variable "subnet_ids" { type = list(string) }
variable "vpc_id" { type = string }

resource "aws_db_subnet_group" "this" {
  name       = "${var.cluster_name}-${var.environment}"
  subnet_ids = var.subnet_ids
}

resource "aws_security_group" "postgres" {
  name   = "${var.cluster_name}-${var.environment}-postgres"
  vpc_id = var.vpc_id
}

resource "aws_db_instance" "this" {
  identifier                  = "${var.cluster_name}-${var.environment}"
  engine                      = "postgres"
  engine_version              = "16"
  instance_class              = "db.m6i.large"
  allocated_storage           = 100
  max_allocated_storage       = 1000
  storage_encrypted           = true
  backup_retention_period     = 35
  multi_az                    = true
  db_subnet_group_name        = aws_db_subnet_group.this.name
  vpc_security_group_ids      = [aws_security_group.postgres.id]
  username                    = "platform_admin"
  manage_master_user_password = true
  skip_final_snapshot         = false
  deletion_protection         = true
}

output "endpoint" {
  value = aws_db_instance.this.endpoint
}
