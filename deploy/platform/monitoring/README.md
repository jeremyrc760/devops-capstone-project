# Monitoring

This directory keeps the active GitOps deployment and the stopped manual stack
separate so the manual Grafana data remains available for rollback.

| Path | State | Purpose |
| --- | --- | --- |
| `manual/` | Rollback only | Stopped legacy stack in `monitoring-manual`; Grafana PVC and secrets retained |
| `helm/` | Active | `kube-prometheus-stack` wrapper managed by Argo CD in `monitoring` |

The active Grafana and Prometheus instances run on `k8s-monitoring-1`. Their
retained local data paths are `/var/lib/grafana-gitops-data` and
`/var/lib/prometheus-gitops-data`. They are exposed at
`grafana.jeremycloudlabs.com` and `prometheus.jeremycloudlabs.com`.

The three dashboards, seven Grafana alert rules, and email contact point are
provisioned from `helm/`. SMTP and ingress credentials are stored as
SealedSecrets.

Validate the active chart with:

```bash
helm lint deploy/platform/monitoring/helm
helm template monitoring deploy/platform/monitoring/helm --namespace monitoring
```

## Rollback

First disable `migrationIngress.enabled` in Git and wait for the `monitoring`
Application to become Synced. The NGINX admission webhook rejects duplicate
host and path pairs, so do not restore the legacy ingresses before that step.

Then restore the stopped stack:

```bash
kubectl scale deployment grafana prometheus kube-state-metrics \
  --replicas=1 -n monitoring-manual
kubectl apply -f deploy/platform/monitoring/manual/20-node-exporter.yaml
kubectl apply -f deploy/platform/monitoring/manual/50-prometheus-ingress.yaml
kubectl apply -f deploy/platform/monitoring/manual/62-grafana-ingress.yaml
```

The retained legacy Grafana volume contains the state frozen at cutover time.
