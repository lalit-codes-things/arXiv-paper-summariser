variable "region" {
  description = "AWS region for the V17 reference stack."
  type        = string
  default     = "us-east-1"
}

variable "cluster_name" {
  description = "EKS cluster name."
  type        = string
  default     = "arxiv-v17"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "prod"
}

variable "tenant_namespaces" {
  description = "Initial tenant namespaces to create."
  type        = list(string)
  default     = ["tenant-research", "tenant-audit"]
}

variable "audit_log_retention_days" {
  description = "Immutable audit log retention period."
  type        = number
  default     = 2555
}

variable "allowed_model_provider_cidrs" {
  description = "Approved egress CIDRs for model providers. Restrict before production use."
  type        = list(string)
  default     = []
}
