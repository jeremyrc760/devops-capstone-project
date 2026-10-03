# Deployment Layout

Deployment assets are grouped by ownership rather than packaging tool.

```text
deploy/
├── applications/
│   └── accounts/
│       └── kustomize/       # active Accounts production manifests
└── platform/
    ├── argocd/
    │   ├── applications/    # Argo CD Application resources
    │   └── bootstrap/       # Argo CD ingress and server settings
    ├── monitoring/
    │   ├── manual/          # stopped rollback stack in monitoring-manual
    │   └── helm/            # active kube-prometheus-stack deployment
    ├── sealed-secrets/      # public sealing certificate
    └── storage/
        └── ebs-csi/helm/    # EBS CSI driver and ebs-gp3 StorageClass
```

`applications/` contains business workloads. `platform/` contains shared
cluster services used to deploy, secure, and observe those workloads.

## Active delivery flow

Application delivery:

1. `ci-build.yaml` runs lint and tests for eligible application, test, build, and workflow changes on `main` and `aws-kubeadm-gitops`, including PRs targeting either branch.
2. After tests pass, pushes and manual runs on these branches publish images to GHCR. PR runs do not publish images.
3. Successful builds on `aws-kubeadm-gitops` create or update a PR changing the Accounts overlay image tag. Builds from `main` do not propose deployment updates.
4. A maintainer reviews and merges the image update PR into `aws-kubeadm-gitops`.
5. Argo CD watches that branch at `deploy/applications/accounts/kustomize/overlays/aws-kubeadm` and deploys the declared image.

Documentation and deployment-only pushes do not rebuild images. Manual runs bypass path filters. Argo CD continues tracking `aws-kubeadm-gitops` after changes merge into `main`.

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
