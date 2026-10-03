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
        ├── postgres-pvc.yaml
        ├── postgres-storage-patch.yaml
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
- A 10 GiB `postgresql-data` PVC using `ebs-gp3`.
- A patch replacing PostgreSQL `emptyDir` with the PVC, setting `PGDATA`
  to a subdirectory, and using the `Recreate` update strategy.

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
CRD supplied by Prometheus Operator. The EBS CSI driver and `ebs-gp3`
StorageClass are also required to provision the PostgreSQL volume.

## Persistent Storage and Limitations

The base uses `emptyDir`; the active AWS overlay replaces it with an EBS gp3
PVC. Database Pod recreation retains data when the same PVC and volume are reused.

The StorageClass uses `Retain`: deleting the PVC does not automatically delete
its EBS volume. Retained volumes need deliberate recovery or cleanup.
PostgreSQL remains a single instance, with downtime during updates and EBS
attachment limited to the volume's Availability Zone. Backups are not configured.

## Archived Overlays

The former dev and prod overlays are preserved under
`archive/accounts-kustomize-overlays/`.

They are historical examples, not active deployment environments.
