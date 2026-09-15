# Kubernetes Monitoring Helm Chart

This wrapper chart pins the Prometheus Community `kube-prometheus-stack` chart
and stores the complete GitOps monitoring configuration for the AWS kubeadm lab
cluster.

## Included components

- Prometheus Operator and monitoring CRDs
- Prometheus with 48-hour retention and a 20 GiB retained local volume
- Alertmanager with 24-hour local retention
- Grafana with a 5 GiB retained local volume
- kube-state-metrics
- node-exporter on every node
- A SealedSecret for Grafana administrator credentials
- SealedSecrets for Grafana SMTP and Prometheus ingress authentication
- Three exported dashboards and seven Grafana-managed alert rules

The static local volumes use `hostPath` on `k8s-monitoring-1`. Their reclaim
policy is `Retain`, but they are tied to that EC2 node. A future production
deployment should replace them with dynamically provisioned EBS volumes.

Prometheus, Alertmanager, Grafana, Prometheus Operator, and kube-state-metrics
are scheduled on the node labeled `workload=monitoring`. node-exporter still
runs on every node.

The kubeadm control-plane component metrics for etcd, kube-scheduler,
kube-controller-manager, and kube-proxy are initially disabled because their
metrics endpoints bind to localhost by default. They can be enabled after those
endpoints are deliberately exposed on the private cluster network.

## Local validation

```bash
helm dependency build deploy/platform/monitoring/helm
helm lint deploy/platform/monitoring/helm
helm template monitoring deploy/platform/monitoring/helm --namespace monitoring
```

The generated dependency archive under `charts/` is ignored by Git. Argo CD
downloads the pinned dependency from the official repository while rendering.

Prometheus accepts `ServiceMonitor` resources from every namespace. The
Accounts deployment uses this to register its `/metrics` endpoint from the
`accounts` namespace without adding static scrape configuration here.

## Provisioned Grafana resources

Dashboard JSON files are stored under `dashboards/`. Alert rules and the email
contact point are stored under `provisioning/`. Helm packages them into labeled
ConfigMaps consumed by Grafana sidecars.

The SMTP application password and Prometheus basic-auth value are never stored
in plaintext. They are encrypted for this cluster in SealedSecret manifests.

Public ingresses are controlled by `migrationIngress.enabled`. Keep it `false`
while validating the Helm stack in parallel, then enable it for the final
cutover from `monitoring-manual`.
