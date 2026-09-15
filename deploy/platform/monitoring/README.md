# Monitoring

This directory deliberately keeps the current deployment and the intended
GitOps deployment separate.

| Path | State | Purpose |
| --- | --- | --- |
| `manual/` | Active | Prometheus, Grafana, node-exporter, and kube-state-metrics in `monitoring-manual` |
| `helm/` | GitOps candidate | `kube-prometheus-stack` wrapper managed by Argo CD in `monitoring` |

The active Grafana PVC uses a local `hostPath` on `k8s-monitoring-1` at
`/var/lib/grafana-data`. It currently stores the dashboards, contact point, and
Grafana-managed alert rules. Prometheus data still uses `emptyDir` and is not
persistent.

The three dashboards, seven Grafana alert rules, and email contact point are
exported under `helm/`. Do not delete the `monitoring-manual` namespace or its
Grafana PVC until the Helm deployment and public cutover have been verified.

Apply the current manual manifests with:

```bash
kubectl apply -f deploy/platform/monitoring/manual/
```

Validate the Helm migration target with:

```bash
helm lint deploy/platform/monitoring/helm
helm template monitoring deploy/platform/monitoring/helm --namespace monitoring
```
