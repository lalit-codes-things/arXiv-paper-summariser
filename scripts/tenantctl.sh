#!/usr/bin/env bash
set -euo pipefail

TENANT="${1:?tenant slug is required}"
NAMESPACE="tenant-${TENANT}"
CPU_QUOTA="${CPU_QUOTA:-8}"
MEMORY_QUOTA="${MEMORY_QUOTA:-32Gi}"

kubectl create namespace "$NAMESPACE" --dry-run=client -o yaml | kubectl apply -f -
kubectl label namespace "$NAMESPACE" "tenant.arxiv.ai/name=$TENANT" "platform.arxiv.ai/tier=data-plane" --overwrite
cat <<YAML | kubectl apply -f -
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-quota
  namespace: $NAMESPACE
spec:
  hard:
    requests.cpu: "$CPU_QUOTA"
    requests.memory: "$MEMORY_QUOTA"
    limits.cpu: "$CPU_QUOTA"
    limits.memory: "$MEMORY_QUOTA"
YAML
