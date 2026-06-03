provider "aws" {
  region = var.region

  default_tags {
    tags = {
      Project     = "arxiv-paper-summariser"
      Platform    = "v17-enterprise"
      Environment = var.environment
      ManagedBy   = "terraform"
    }
  }
}

module "networking" {
  source       = "./modules/networking"
  cluster_name = var.cluster_name
  environment  = var.environment
}

module "eks" {
  source             = "./modules/eks"
  cluster_name       = var.cluster_name
  environment        = var.environment
  private_subnet_ids = module.networking.private_subnet_ids
  vpc_id             = module.networking.vpc_id
}

module "postgres" {
  source       = "./modules/postgres"
  cluster_name = var.cluster_name
  environment  = var.environment
  subnet_ids   = module.networking.private_subnet_ids
  vpc_id       = module.networking.vpc_id
}

module "redis" {
  source       = "./modules/redis"
  cluster_name = var.cluster_name
  environment  = var.environment
  subnet_ids   = module.networking.private_subnet_ids
  vpc_id       = module.networking.vpc_id
}

module "observability" {
  source                   = "./modules/observability"
  cluster_name             = var.cluster_name
  environment              = var.environment
  audit_log_retention_days = var.audit_log_retention_days
}

resource "aws_s3_bucket" "papers" {
  bucket_prefix = "${var.cluster_name}-${var.environment}-papers-"
}

resource "aws_s3_bucket_server_side_encryption_configuration" "papers" {
  bucket = aws_s3_bucket.papers.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

resource "aws_s3_bucket_versioning" "papers" {
  bucket = aws_s3_bucket.papers.id

  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket" "audit" {
  bucket_prefix = "${var.cluster_name}-${var.environment}-audit-"
}

resource "aws_s3_bucket_object_lock_configuration" "audit" {
  bucket = aws_s3_bucket.audit.id

  rule {
    default_retention {
      mode = "GOVERNANCE"
      days = var.audit_log_retention_days
    }
  }
}
