# arXiv Paper Summariser — V17 Enterprise Platform

V17 upgrades the project from a single research utility into an enterprise-grade AI research infrastructure blueprint for regulated, multi-tenant deployments.

## V17 capabilities

- **Multi-tenant architecture** with namespace isolation, per-tenant network policies, quotas, and database tenancy guidance.
- **Audit logging** for authentication, authorization, paper ingestion, summarisation requests, model access, data export, and administrative changes.
- **Observability** using OpenTelemetry, Prometheus, Grafana, Loki, Alertmanager, and SLO-oriented alerts.
- **Monitoring** for API latency, error budgets, model-provider failures, queue health, cost controls, and Kubernetes saturation.
- **Kubernetes deployment** manifests and a Helm chart for API, worker, web, ingress, policies, and secrets integration.
- **CI/CD** with lint, security scanning, container build, IaC validation, and deployment gates.
- **Autoscaling** with HPA and KEDA examples for HTTP and queue-driven workloads.
- **SSO** via OIDC/SAML-ready configuration and group-to-role mapping.
- **Compliance features** covering retention, encryption, data classification, access reviews, evidence collection, and policy-as-code.

## Repository layout

```text
.github/workflows/         CI/CD pipeline definitions
compliance/                Compliance controls, evidence, and audit event schema
deploy/helm/               Enterprise Helm deployment stack
deploy/kubernetes/         Kustomize-ready Kubernetes manifests
infra/terraform/           Infrastructure-as-code for AWS EKS reference deployment
monitoring/                Prometheus, Alertmanager, Grafana, Loki, and OTel config
policies/                  OPA Gatekeeper policies and constraint examples
scripts/                   Production operations tooling
```

## Quick start

1. Review the target architecture in [`docs/enterprise/V17_ARCHITECTURE.md`](docs/enterprise/V17_ARCHITECTURE.md).
2. Configure infrastructure variables in [`infra/terraform/variables.tf`](infra/terraform/variables.tf).
3. Plan the reference deployment:

   ```bash
   cd infra/terraform
   terraform init
   terraform plan -var='cluster_name=arxiv-v17-prod'
   ```

4. Deploy application resources with Helm:

   ```bash
   helm upgrade --install arxiv-summariser deploy/helm/arxiv-summariser \
     --namespace arxiv-prod --create-namespace \
     --values deploy/helm/arxiv-summariser/values.yaml
   ```

5. Enable monitoring by applying the monitoring stack in [`monitoring/`](monitoring/).

## Operational model

V17 assumes production operation by a platform team with separation of duties:

- **Platform admins** manage clusters, IaC, ingress, secrets, observability, and policies.
- **Tenant admins** manage users, groups, quotas, and data retention inside assigned tenants.
- **Researchers** access papers, run summarisation workflows, and export approved outputs.
- **Auditors** receive read-only access to evidence bundles, audit logs, and compliance reports.

