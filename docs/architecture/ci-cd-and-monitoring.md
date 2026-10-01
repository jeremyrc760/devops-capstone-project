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
| `monitoring` | `deploy/platform/monitoring/helm` | `monitoring` | Active monitoring stack managed through Helm and Argo CD |

The Argo CD Application definitions live in
`deploy/platform/argocd/applications/`. Applying those definitions changes what
Argo CD tracks; committing them alone does not update a manually created
Application resource.

## Active monitoring flow

```text
Accounts /metrics -----+
Node exporters --------+--> Prometheus --> Grafana dashboards
kube-state-metrics ----+                     |
                                            +--> Grafana alert rules
                                                      |
                                                      +--> email notifications
```

The active stack is deployed from `deploy/platform/monitoring/helm/`
into the `monitoring` namespace by Argo CD.

- Prometheus collects application, node, and Kubernetes object metrics.
- node-exporter exposes host resource metrics.
- kube-state-metrics exposes Kubernetes object state.
- Grafana loads dashboards, alert rules, and contact points from Git.
- Grafana sends email notifications through its configured SMTP settings.

The wrapper chart depends on `kube-prometheus-stack`. Custom templates
provide Ingress resources, SealedSecrets, local storage, and ConfigMaps
for dashboards and alerting.

Grafana uses a 5 GiB PVC. Prometheus requests a 20 GiB PVC.
Both use retained hostPath PVs tied to `k8s-monitoring-1`.

The manifests under `deploy/platform/monitoring/manual/` are retained
for rollback reference.

## Verify tracked repository paths

Run this read-only command to inspect the live Application sources:

```bash
kubectl get applications -n argocd \
  -o custom-columns='NAME:.metadata.name,BRANCH:.spec.source.targetRevision,PATH:.spec.source.path'
```

Compare the output with the Application table above. If a source differs,
review the intended change before updating the live Application.

Renaming an Application YAML file does not rename the Kubernetes
Application object. The object's identity comes from its metadata.
