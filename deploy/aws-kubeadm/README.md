# AWS kubeadm Deployment

This directory contains standard Kubernetes manifests for deploying the Account API to a self-managed AWS kubeadm cluster.

It intentionally does not commit a real Kubernetes Secret. Create the database Secret directly in the cluster, or replace this with Sealed Secrets / External Secrets later.

## Image

The app Deployment expects this image tag by default:

```text
ghcr.io/jeremyrc760/devops-capstone-project:aws-kubeadm-gitops
```

The `.github/workflows/docker-ghcr.yaml` workflow builds and pushes the image to GHCR on pushes to `main` and `aws-kubeadm-gitops`.

If the GHCR package is private, either make the package public for this lab or configure an `imagePullSecret`.

## Deploy

Run these commands from a machine with `kubectl` configured for the AWS kubeadm cluster.

```bash
kubectl apply -f deploy/aws-kubeadm/namespace.yaml
```

```text
Create the accounts namespace before creating namespaced resources.
```

```bash
kubectl create secret generic postgresql \
  --namespace accounts \
  --from-literal=database-name=accounts \
  --from-literal=database-user=postgres \
  --from-literal=database-password='<choose-a-password>'
```

```text
Create the PostgreSQL credentials Secret in the cluster without committing the password to Git.
```

```bash
kubectl apply -k deploy/aws-kubeadm
```

```text
Apply the ConfigMap, PostgreSQL Deployment/Service, and accounts API Deployment/Service.
```

```bash
kubectl get pods -n accounts -o wide
```

```text
Check whether PostgreSQL and accounts API Pods are Running and Ready.
```

```bash
kubectl get svc -n accounts
```

```text
Find the accounts NodePort Service. This lab pins it to port 32080.
```

```bash
curl http://<worker-public-ip>:32080/health
```

```text
Access the accounts API through a worker node public IP and the NodePort.
```

## Notes

PostgreSQL uses `emptyDir` in this first lab version, so database data is ephemeral. If the Pod is recreated, the data can be lost. A later version should use a StatefulSet and PVC, or AWS RDS PostgreSQL.
