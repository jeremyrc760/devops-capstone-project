# Accounts Helm Chart

This chart is a Helm-based packaging alternative to the Accounts Kustomize manifests. It renders
the Accounts API, PostgreSQL, networking, ingress, and optional SealedSecret
resources from reusable templates and environment-specific values files.

## Validate locally

Run these commands from the repository root:

```bash
helm lint deploy/applications/accounts/helm
helm template accounts deploy/applications/accounts/helm \
  --namespace accounts \
  -f deploy/applications/accounts/helm/values-aws-kubeadm.yaml
```

Environment examples:

- `values-dev.yaml`: one Accounts replica, NodePort service, no Ingress.
- `values-aws-kubeadm.yaml`: two replicas, ClusterIP service, NGINX Ingress and TLS.
- `values-prod.yaml`: three replicas, ClusterIP service, NGINX Ingress and TLS.

## Prometheus monitoring

Set `monitoring.enabled: true` to render a `ServiceMonitor` that scrapes the
Accounts API `/metrics` endpoint every 30 seconds. The AWS kubeadm values file
enables it because that cluster already runs the Prometheus Operator through
`kube-prometheus-stack`.

```yaml
monitoring:
  enabled: true
  interval: 30s
  scrapeTimeout: 10s
```

The Prometheus Operator CRDs must exist before installing a release with this
option enabled.

## SealedSecret input

The chart intentionally does not duplicate cluster-bound encrypted values in its
default values file. To render the SealedSecret, provide a private local values
file containing the existing encrypted strings:

```yaml
postgresql:
  sealedSecret:
    enabled: true
    encryptedData:
      database-name: Ag...
      database-user: Ag...
      database-password: Ag...
```

The ciphertext is safe to store in Git, but it remains bound to the Sealed
Secrets controller key and, with strict scope, the Secret name and namespace.

## Ownership warning

The live `accounts` resources are currently managed by Argo CD from the
Kustomize overlay. Do not run `helm install` against the same names and namespace
until the Argo CD Application source is deliberately migrated to this chart.
For now, use `helm lint` and `helm template` only.
