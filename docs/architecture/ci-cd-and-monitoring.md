# CI/CD and Monitoring Architecture

## Accounts delivery flow

1. A developer pushes application code or deployment YAML to GitHub.
2. `.github/workflows/ci-build.yaml` runs linting and tests for `main` pushes and pull requests.
3. `.github/workflows/docker-ghcr.yaml` builds and publishes the application image for `main` and `aws-kubeadm-gitops` pushes.
4. The `accounts` Argo CD Application watches `aws-kubeadm-gitops` at `deploy/applications/accounts/kustomize/overlays/aws-kubeadm`.
5. Argo CD applies the rendered resources to the `accounts` namespace and self-heals drift.
6. Kubernetes pulls the GHCR image tag declared by the Kustomize overlay.

CI and image publishing are currently separate workflows. A successful image
build is not gated on the test workflow, and the image workflow does not update
the Kustomize image tag automatically.

## Argo CD applications

| Application | Source path | Destination | Role |
| --- | --- | --- | --- |
| `accounts` | `deploy/applications/accounts/kustomize/overlays/aws-kubeadm` | `accounts` | Active Accounts API deployment |
| `accounts-helm-dev` | `deploy/applications/accounts/helm` | `accounts-helm-dev` | Helm learning/dev deployment |
| `monitoring` | `deploy/platform/monitoring/helm` | `monitoring` | Helm monitoring migration target |

The Argo CD Application definitions live in
`deploy/platform/argocd/applications/`. Applying those definitions changes what
Argo CD tracks; committing them alone does not update a manually created
Application resource.

## Active monitoring flow

```text
Accounts /metrics -----+
Node exporters --------+--> Prometheus --> Grafana dashboards
kube-state-metrics ----+         |              |
                                 |              +--> Grafana alert rules
                                 |                       |
                                 +-----------------------+--> email contact point
```

The active stack is `deploy/platform/monitoring/manual/` in the
`monitoring-manual` namespace:

- Prometheus scrapes application, node, and Kubernetes object metrics.
- node-exporter reports host CPU, memory, disk, filesystem, and network data.
- kube-state-metrics reports Kubernetes object state such as desired/ready replicas and pod phases.
- Grafana combines those metrics into the Accounts API, Kubernetes, and Node Exporter dashboards.
- Grafana evaluates the current alert rules and sends email through its configured SMTP settings.

The separate Helm chart packages `kube-prometheus-stack` for a future move to a
fully Argo CD-managed monitoring stack. It should not replace the manual stack
until dashboards, alert rules, contact points, SMTP configuration, and storage
have been migrated and verified.

## Repository path cutover

The live Argo CD Application objects still reference the old repository paths
until this reorganization is committed and pushed. After pushing, update only
their source paths so the existing sync-policy settings are preserved:

```bash
kubectl patch application accounts -n argocd --type merge \
  -p '{"spec":{"source":{"path":"deploy/applications/accounts/kustomize/overlays/aws-kubeadm"}}}'

kubectl patch application accounts-helm-dev -n argocd --type merge \
  -p '{"spec":{"source":{"path":"deploy/applications/accounts/helm"}}}'

kubectl patch application monitoring -n argocd --type merge \
  -p '{"spec":{"source":{"path":"deploy/platform/monitoring/helm"}}}'
```

The monitoring patch changes only the repository path. It does not migrate the
active `monitoring-manual` stack or intentionally enable automated sync for the
Helm deployment.
