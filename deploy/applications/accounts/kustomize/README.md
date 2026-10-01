# Accounts Kustomize Deployment

This directory defines the Accounts API and PostgreSQL deployment.
The active deployment entry point is `overlays/aws-kubeadm/`.

## Structure

```text
kustomize/
├── base/
│   ├── kustomization.yaml
│   ├── accounts-configmap.yaml
│   ├── accounts-deployment.yaml
│   ├── accounts-service.yaml
│   ├── postgres-deployment.yaml
│   └── postgres-service.yaml
└── overlays/
    └── aws-kubeadm/
        ├── kustomization.yaml
        ├── namespace.yaml
        ├── accounts-ingress.yaml
        ├── postgres-sealedsecret.yaml
        ├── accounts-servicemonitor.yaml
        └── networkpolicy.yaml
```

## Base

The base defines the API and database workloads, their internal
ClusterIP Services, and shared application configuration.

It does not create a namespace. The AWS overlay assigns the resources
to the `accounts` namespace.

## AWS Overlay

The AWS overlay includes the base and provides:

- The `accounts` Namespace resource.
- Ingress rules for the API domain and TLS configuration.
- PostgreSQL credentials encrypted with Sealed Secrets.
- A ServiceMonitor for Prometheus to scrape the API metrics.
- The application image tag used for this deployment.

The SealedSecret depends on the corresponding controller private key.
Its Secret name and namespace must remain consistent with its sealing scope.

## Network Policy Status

`networkpolicy.yaml` is a draft and is not listed in `resources`.
It is therefore not included in the rendered deployment.

Review and validate the access rules before enabling it.

## Render Locally

Run from the repository root:

```bash
kubectl kustomize deploy/applications/accounts/kustomize/overlays/aws-kubeadm
```

This command renders the manifests without applying them to a cluster.
Argo CD manages deployment from this overlay.

The target cluster requires an Ingress Controller, cert-manager with
the configured ClusterIssuer, Sealed Secrets, and the ServiceMonitor
CRD supplied by Prometheus Operator.

## Known Limitation

PostgreSQL currently uses `emptyDir` storage. Its data does not survive
Pod replacement. Persistent storage and backup are separate follow-up work.

## Archived Overlays

The former dev and prod overlays are preserved under
`archive/accounts-kustomize-overlays/`.

They are historical examples, not active deployment environments.