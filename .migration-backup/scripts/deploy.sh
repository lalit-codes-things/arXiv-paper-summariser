#!/usr/bin/env bash
set -euo pipefail

COMMAND="${1:-plan}"
RELEASE="${RELEASE:-arxiv-summariser}"
NAMESPACE="${NAMESPACE:-arxiv-prod}"
CHART="${CHART:-deploy/helm/arxiv-summariser}"
VALUES="${VALUES:-deploy/helm/arxiv-summariser/values.yaml}"

case "$COMMAND" in
  plan)
    helm template "$RELEASE" "$CHART" --namespace "$NAMESPACE" --values "$VALUES"
    ;;
  deploy)
    helm upgrade --install "$RELEASE" "$CHART" --namespace "$NAMESPACE" --create-namespace --values "$VALUES" --atomic --timeout 10m
    ;;
  rollback)
    helm rollback "$RELEASE" --namespace "$NAMESPACE"
    ;;
  *)
    echo "Usage: $0 [plan|deploy|rollback]" >&2
    exit 2
    ;;
esac
