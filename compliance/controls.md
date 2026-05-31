# V17 Compliance Controls

| Control | Implementation evidence | Owner | Cadence |
| --- | --- | --- | --- |
| Access review | SSO group export, RBAC bindings, tenant admin approval | Security | Quarterly |
| Change management | Pull request, CI run, deployment approval, audit event | Platform | Every release |
| Audit logging | Schema validation, SIEM delivery confirmation, retention policy | Security | Continuous |
| Data retention | Tenant retention configuration and deletion reports | Tenant admin | Monthly |
| Vulnerability management | Container scan, dependency scan, remediation ticket | Platform | Every build |
| Backup and recovery | PITR settings, restore test report, object versioning | SRE | Quarterly |
| Incident response | Alertmanager incident, timeline, root cause, corrective actions | SRE | Every incident |
| Encryption | KMS configuration, TLS certificates, secret-store policy | Platform | Continuous |

## Data classes

- **Public**: arXiv metadata and source links.
- **Internal**: generated summaries and team annotations.
- **Confidential**: prompts, embeddings, tenant configuration, and export requests.
- **Restricted**: identity data, tokens, secrets, audit logs, and legal holds.

## Evidence bundle contents

- Deployment revision and image digests.
- Terraform plan and apply logs.
- Kubernetes policy admission results.
- Audit-log delivery report.
- SSO group-to-role mapping export.
- Vulnerability scan output.
- Backup restore test report.
