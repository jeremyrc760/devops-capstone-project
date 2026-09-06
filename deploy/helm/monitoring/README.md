# Kubernetes Monitoring Helm Chart

This wrapper chart pins the Prometheus Community `kube-prometheus-stack` chart
and stores the settings for the three-node AWS kubeadm lab cluster.

## Included components

- Prometheus Operator and monitoring CRDs
- Prometheus with 48-hour local retention
- Alertmanager with 24-hour local retention
- Grafana with built-in Kubernetes dashboards
- kube-state-metrics
- node-exporter on every node
- A SealedSecret for Grafana administrator credentials

Persistent storage is intentionally disabled because the cluster does not yet
have a Kubernetes StorageClass. Metrics and Grafana runtime data can be lost
when their Pods are recreated. Add the AWS EBS CSI driver before enabling PVCs.

Prometheus, Alertmanager, and Grafana are scheduled on the control-plane node,
which has more memory than the two lab workers. Their tolerations apply only to
the control-plane `NoSchedule` taint; node-exporter still runs on every node and
the remaining monitoring components can run on workers.

The kubeadm control-plane component metrics for etcd, kube-scheduler,
kube-controller-manager, and kube-proxy are initially disabled because their
metrics endpoints bind to localhost by default. They can be enabled after those
endpoints are deliberately exposed on the private cluster network.

## Local validation

```bash
helm dependency build deploy/helm/monitoring
helm lint deploy/helm/monitoring
helm template monitoring deploy/helm/monitoring --namespace monitoring
```

The generated dependency archive under `charts/` is ignored by Git. Argo CD
downloads the pinned dependency from the official repository while rendering.
