# Monitoring

This directory deliberately keeps the current deployment and the intended
GitOps deployment separate.

| Path | State | Purpose |
| --- | --- | --- |
| `manual/` | Active | Prometheus, Grafana, node-exporter, and kube-state-metrics in `monitoring-manual` |
| `helm/` | Migration target | `kube-prometheus-stack` wrapper intended for Argo CD in `monitoring` |

The active Grafana PVC uses a local `hostPath` on `k8s-monitoring-1` at
`/var/lib/grafana-data`. It currently stores the dashboards, contact point, and
Grafana-managed alert rules. Prometheus data still uses `emptyDir` and is not
persistent.

The dashboards and Grafana alert rules are not yet exported as code. Do not
delete the `monitoring-manual` namespace or its Grafana PVC during the Helm
migration until those resources have been exported and restored successfully.

Apply the current manual manifests with:

```bash
kubectl apply -f deploy/platform/monitoring/manual/
```

Validate the Helm migration target with:

```bash
helm lint deploy/platform/monitoring/helm
helm template monitoring deploy/platform/monitoring/helm --namespace monitoring
```
