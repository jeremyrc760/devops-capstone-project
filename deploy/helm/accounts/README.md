# Accounts Helm Chart

This chart is a Helm-based packaging alternative to `deploy/kustomize`. It renders
the Accounts API, PostgreSQL, networking, ingress, and optional SealedSecret
resources from reusable templates and environment-specific values files.

## Validate locally

Run these commands from the repository root:

```bash
helm lint deploy/helm/accounts
helm template accounts deploy/helm/accounts \
  --namespace accounts \
  -f deploy/helm/accounts/values-aws-kubeadm.yaml
```

Environment examples:

- `values-dev.yaml`: one Accounts replica, NodePort service, no Ingress.
- `values-aws-kubeadm.yaml`: two replicas, ClusterIP service, NGINX Ingress and TLS.
- `values-prod.yaml`: three replicas, ClusterIP service, NGINX Ingress and TLS.

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
