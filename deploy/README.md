# Deployment Layout

Deployment assets are grouped by ownership rather than packaging tool.

```text
deploy/
├── applications/
│   └── accounts/
│       ├── kustomize/       # active Accounts production manifests
│       └── helm/            # Helm learning/dev deployment
└── platform/
    ├── argocd/
    │   ├── applications/    # Argo CD Application resources
    │   └── bootstrap/       # Argo CD ingress and server settings
    ├── monitoring/
    │   ├── manual/          # active monitoring-manual stack
    │   └── helm/            # target kube-prometheus-stack deployment
    └── sealed-secrets/      # public sealing certificate
```

`applications/` contains business workloads. `platform/` contains shared
cluster services used to deploy, secure, and observe those workloads.

The active Accounts deployment is managed by the `accounts` Argo CD
Application. The active monitoring stack is currently the manually applied
`monitoring-manual` namespace; the Helm chart is a separate migration target.
