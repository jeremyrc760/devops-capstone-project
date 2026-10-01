# Argo CD Configuration

This directory contains Argo CD access configuration and Application
definitions for the Accounts service and monitoring platform.

Argo CD installation is handled separately by Ansible.

## Directory Responsibilities

- `bootstrap/`: Argo CD server parameters and HTTPS ingress.
- `applications/`: Git sources, deployment destinations, and sync policies
  for workloads managed by Argo CD.

## Bootstrap Configuration

| File | Purpose |
| --- | --- |
| `argocd-ingress.yaml` | Routes argocd.jeremycloudlabs.com to the Argo CD server |
| `argocd-server-config.yaml` | Configures the Argo CD server to serve HTTP behind NGINX |
| `kustomization.yaml` | Includes both configuration files |

NGINX terminates external HTTPS and forwards HTTP to the Argo CD server.
The `server.insecure` setting disables server-side TLS, not authentication.

These files configure an existing Argo CD installation; they do not install
the Argo CD controllers.

Render from the repository root:

```bash
kubectl kustomize deploy/platform/argocd/bootstrap
```

To apply the access configuration to an existing installation:

```bash
kubectl apply -k deploy/platform/argocd/bootstrap
```

Changes to server startup parameters may require restarting the Argo CD
server workload. Ingress TLS requires NGINX, cert-manager, and the
`letsencrypt-http01` ClusterIssuer.

## Applications

| Application | Source path | Namespace | Role |
| --- | --- | --- | --- |
| `accounts` | `deploy/applications/accounts/kustomize/overlays/aws-kubeadm` | `accounts` | Main Accounts deployment |
| `monitoring` | `deploy/platform/monitoring/helm` | `monitoring` | Monitoring platform |

Both Application definitions track the `aws-kubeadm-gitops` branch.

Accounts uses Kustomize. Monitoring uses Helm to render its resources.
Argo CD manages synchronization of both.

## Sync Policies

- `accounts`: automated synchronization and self-healing; automatic pruning
  is not enabled.
- `monitoring`: automated synchronization, self-healing, and pruning.

Pruning can delete managed cluster resources that are removed from the
rendered Git configuration.

Both definitions include a resource deletion finalizer. Deleting an
Application can cascade to its managed resources; review the intended
deletion behavior before retiring an application.

## Applying Changes

Argo CD reads workload configuration from Git, not from local uncommitted
files. Changes must reach the tracked branch before Argo CD can sync them.

Application definitions are themselves Kubernetes resources. Committing
changes under `applications/` does not automatically update live Application
objects unless another controller is configured to manage those files.

For manually managed Application definitions, apply the specific changed
file after review. Avoid applying the entire directory when changing only
one Application.

The monitoring stack must provide the ServiceMonitor CRD before a fresh
Accounts deployment containing a ServiceMonitor can succeed.

## Check Application Status

```bash
kubectl get applications -n argocd
```

`Synced` indicates configuration synchronization. `Healthy` reflects Argo CD
resource health assessment. Neither replaces functional API, database, or
monitoring checks.