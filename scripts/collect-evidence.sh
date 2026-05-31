#!/usr/bin/env bash
set -euo pipefail

OUT_DIR="${1:-evidence/$(date -u +%Y%m%dT%H%M%SZ)}"
mkdir -p "$OUT_DIR"

kubectl get namespaces -L platform.arxiv.ai/tier,tenant.arxiv.ai/name -o wide > "$OUT_DIR/namespaces.txt"
kubectl get deployments --all-namespaces -o wide > "$OUT_DIR/deployments.txt"
kubectl get networkpolicies --all-namespaces -o yaml > "$OUT_DIR/networkpolicies.yaml"
kubectl get resourcequotas --all-namespaces -o yaml > "$OUT_DIR/resourcequotas.yaml"
kubectl auth can-i --list --namespace arxiv-prod > "$OUT_DIR/platform-rbac.txt" || true

echo "Evidence collected in $OUT_DIR"
