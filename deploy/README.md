# Deployment Layout

Deployment assets are grouped by ownership rather than packaging tool.

```text
deploy/
├── applications/
│   └── accounts/
│       ├── kustomize/       # active Accounts production manifests
│       └── helm/            # Helm learning/dev deployment
└── platform/
    ├── argocd/
    │   ├── applications/    # Argo CD Application resources
    │   └── bootstrap/       # Argo CD ingress and server settings
    ├── monitoring/
    │   ├── manual/          # stopped rollback stack in monitoring-manual
    │   └── helm/            # active kube-prometheus-stack deployment
    └── sealed-secrets/      # public sealing certificate
```

`applications/` contains business workloads. `platform/` contains shared
cluster services used to deploy, secure, and observe those workloads.

## Active delivery flow

Application delivery:

1. GitHub Actions `ci-build.yaml` runs lint and tests for `main` pushes and pull
   requests.
2. `docker-ghcr.yaml` builds and pushes the Accounts image for `main` and
   `aws-kubeadm-gitops`.
3. The Argo CD Application `accounts` tracks branch `aws-kubeadm-gitops` at
   `deploy/applications/accounts/kustomize/overlays/aws-kubeadm` and reconciles
   it into namespace `accounts`.

Platform monitoring delivery:

1. Monitoring configuration, dashboards, alert rules, and encrypted secrets
   are committed under `deploy/platform/monitoring/helm`.
2. The Argo CD Application `monitoring` tracks that path on branch
   `aws-kubeadm-gitops` and renders the wrapper Helm chart.
3. Argo CD deploys and self-heals the stack in namespace `monitoring` with
   pruning and server-side apply enabled.
4. Prometheus discovers the Accounts `ServiceMonitor`, Kubernetes objects,
   kubelets, and node-exporter. Grafana queries Prometheus and sends
   Grafana-managed alert notifications through its provisioned email contact
   point.

The old `monitoring-manual` workloads are stopped. Its Grafana PVC and secrets
remain available only for rollback.
