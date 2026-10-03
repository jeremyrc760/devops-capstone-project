# CI/CD and Monitoring Architecture

## Accounts delivery flow

1. `ci-build.yaml` runs lint and tests for eligible application, test, build, and workflow changes on `main` and `aws-kubeadm-gitops`, including PRs targeting either branch.
2. After tests pass, pushes and manual runs on these branches publish images to GHCR. PR runs do not publish images.
3. Successful builds on `aws-kubeadm-gitops` create or update a PR changing the Accounts overlay image tag. Builds from `main` do not propose deployment updates.
4. A maintainer reviews and merges the image update PR into `aws-kubeadm-gitops`.
5. Argo CD watches that branch at `deploy/applications/accounts/kustomize/overlays/aws-kubeadm` and deploys the declared image.

Documentation and deployment-only pushes do not rebuild images. Manual runs bypass path filters. Argo CD continues tracking `aws-kubeadm-gitops` after changes merge into `main`.

## Argo CD applications

| Application | Source path | Destination | Role |
| --- | --- | --- | --- |
| `accounts` | `deploy/applications/accounts/kustomize/overlays/aws-kubeadm` | `accounts` | Active Accounts API deployment |
| `monitoring` | `deploy/platform/monitoring/helm` | `monitoring` | Active monitoring stack managed through Helm and Argo CD |
| `ebs-csi` | `deploy/platform/storage/ebs-csi/helm` | `kube-system` | EBS CSI driver and ebs-gp3 StorageClass |

The Argo CD Application definitions live in
`deploy/platform/argocd/applications/`. Applying those definitions changes what
Argo CD tracks; committing them alone does not update a manually created
Application resource.

## Accounts persistent storage

The `ebs-csi` Application installs the driver in `kube-system` and creates the
cluster-scoped `ebs-gp3` StorageClass. The driver provisions a 10 GiB EBS
volume for the Accounts `postgresql-data` PVC when the database Pod is
scheduled. The class uses encryption, `WaitForFirstConsumer`, and `Retain`.
Pod recreation reuses the PVC; this is not a backup or a highly available database.

The controller runs on `k8s-worker-1` and uses its EC2 IAM role. Prepare that
role and EC2 metadata access separately before installing on a new cluster.

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
