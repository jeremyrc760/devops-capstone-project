# Archived Project Assets

This directory preserves deployment assets from earlier phases of the project.
Nothing under `archive/` is part of the current AWS GitOps deployment.

## Contents

| Path | Purpose |
| --- | --- |
| `aws-kubeadm-manual/` | Early, manually applied Kubernetes manifests for the AWS kubeadm cluster |
| `ibm-capstone-legacy/` | Original IBM/OpenShift/Tekton deployment assets and development setup script |
| `accounts-kustomize-overlays/` | Historical dev/prod overlays; retained for reference only |
| `accounts-helm-experiment/` | Retired Accounts Helm learning deployment; retained for reference only |

The active deployment paths are:

- `deploy/applications/accounts/kustomize/overlays/aws-kubeadm/` for the Accounts API
- `deploy/platform/monitoring/helm/` for the Helm-managed monitoring stack
- `deploy/platform/argocd/` for Argo CD applications and platform access

The manifests under `deploy/platform/monitoring/manual/` are retained
for rollback reference and are not an active deployment entry point.

Archived commands and manifests may require older tooling and are retained for
reference only. Do not apply them to the current cluster without reviewing and
updating them first.
