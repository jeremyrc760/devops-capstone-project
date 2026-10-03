# Ansible Bootstrap Layer

This directory is for practicing configuration management against the self-managed Kubernetes cluster on AWS EC2.

Ansible currently verifies SSH access, inspects node state, enforces common kubeadm prerequisites, initializes the control plane, joins worker nodes, installs Calico CNI, installs Argo CD, installs Sealed Secrets, installs cert-manager, and installs the NGINX Ingress Controller.

## Directory Layout

| Path | Purpose |
| --- | --- |
| `ansible.cfg` | Local Ansible defaults for this lab |
| `inventories/aws-kubeadm/hosts.example.ini` | Example inventory for the control plane and worker nodes |
| `inventories/aws-kubeadm/hosts.ini` | Real local inventory, ignored by Git |
| `inventories/aws-kubeadm/group_vars/` | Inventory-specific variable overrides |
| `playbooks/00-ping.yml` | Simple connectivity playbook |
| `playbooks/01-inspect-nodes.yml` | Read-only node inspection playbook |
| `playbooks/10-bootstrap-common.yml` | Applies common kubeadm node prerequisites |
| `playbooks/20-init-control-plane.yml` | Initializes only the Kubernetes control plane with kubeadm |
| `playbooks/30-join-workers.yml` | Joins worker nodes to the initialized Kubernetes control plane |
| `playbooks/40-install-calico.yml` | Installs Calico CNI from the control plane |
| `playbooks/50-install-argocd.yml` | Installs Argo CD from the control plane |
| `playbooks/60-install-sealed-secrets.yml` | Installs the Sealed Secrets controller from the control plane |
| `playbooks/70-install-cert-manager.yml` | Installs cert-manager and optionally creates the HTTP-01 ClusterIssuer |
| `playbooks/80-install-nginx-ingress.yml` | Installs the NGINX Ingress Controller from the control plane |
| `roles/` | Reusable task logic called by the playbooks |

Run commands from this directory so `ansible.cfg` is automatically used:

```bash
cd ansible
```

## Inventory Setup

Copy the example inventory:

```bash
cp inventories/aws-kubeadm/hosts.example.ini inventories/aws-kubeadm/hosts.ini
```

Edit `inventories/aws-kubeadm/hosts.ini` with the current EC2 public IPs, private IPs, SSH user, and SSH key path. This file should stay local because it contains environment-specific connection details.

## Execution Order

### 00 - Ping

```bash
ansible-playbook playbooks/00-ping.yml
```

Confirms Ansible can SSH into all inventory hosts.

### 01 - Inspect Nodes

```bash
ansible-playbook playbooks/01-inspect-nodes.yml
```

Checks each node's hostname, private IP, OS version, containerd version, kubeadm version, kubectl client version, service state, and swap state.

This playbook is read-only.

### 10 - Common Node Bootstrap

```bash
ansible-playbook playbooks/10-bootstrap-common.yml
```

Installs base packages, loads Kubernetes kernel modules, configures sysctl networking values, and disables swap.

Because the current cluster was already configured manually, this playbook should mostly confirm or standardize the existing state.

### 20 - Control Plane Initialization

```bash
ansible-playbook playbooks/20-init-control-plane.yml
```

Targets only the `control_plane` inventory group. It checks for `/etc/kubernetes/admin.conf` before running `kubeadm init`; if the control plane is already initialized, it reports that state and skips initialization.

Default kubeadm settings:

| Variable | Default | Purpose |
| --- | --- | --- |
| `kubeadm_apiserver_advertise_address` | `{{ ansible_default_ipv4.address }}` | Private node IP used by workers to reach the API server |
| `kubeadm_pod_network_cidr` | `192.168.0.0/16` | Pod CIDR expected by the Calico configuration used in this lab |
| `control_plane_join_command_path` | `/root/kubeadm/join-workers.sh` | Root-only location for the worker join command |

The worker join command contains a bootstrap token, so it is not printed in normal output or committed to the repository.

### 30 - Worker Join

```bash
ansible-playbook playbooks/30-join-workers.yml
```

Targets only the `workers` inventory group. It checks worker prerequisites, reads the root-only join script from the control plane, copies it to each worker as `/root/kubeadm/join-workers.sh`, and runs it only when `/etc/kubernetes/kubelet.conf` does not already exist.

This playbook does not reset or rejoin an existing worker. If a node needs to be rebuilt, reset it deliberately outside this playbook before running the join phase again.

### 40 - Calico CNI Installation

```bash
ansible-playbook playbooks/40-install-calico.yml
```

Targets only the `control_plane` inventory group. It uses the admin kubeconfig at `/etc/kubernetes/admin.conf` to apply the Tigera operator manifest and Calico custom resources. The Calico node agent then runs across the cluster as a DaemonSet.

Default Calico settings:

| Variable | Default | Purpose |
| --- | --- | --- |
| `calico_version` | `v3.30.3` | Calico release used for the Tigera operator manifest |
| `calico_pod_network_cidr` | `192.168.0.0/16` | Pod network CIDR matching `kubeadm init --pod-network-cidr` |
| `calico_encapsulation` | `VXLAN` | Encapsulation mode for cross-node pod traffic in this EC2 lab |
| `calico_enable_api_server` | `true` | Also creates the Calico APIServer custom resource |

### 50 - Argo CD Installation

```bash
ansible-playbook playbooks/50-install-argocd.yml
```

Targets only the `control_plane` inventory group. It creates the Argo CD namespace, applies the Argo CD install manifest, and waits for the core Argo CD workloads to finish rolling out.

This playbook installs Argo CD itself. It does not create application-specific `Application` resources, expose the Argo CD UI, or print the initial admin password.

### 60 - Sealed Secrets Installation

```bash
ansible-playbook playbooks/60-install-sealed-secrets.yml
```

Targets only the `control_plane` inventory group. It applies the Sealed Secrets controller manifest, waits for the controller deployment, and verifies that the `sealedsecrets.bitnami.com` CRD exists.

This playbook installs the Sealed Secrets controller only. Application `SealedSecret` resources should stay in the GitOps manifests.

### 70 - cert-manager Installation

```bash
ansible-playbook playbooks/70-install-cert-manager.yml -e cert_manager_acme_email=you@example.com
```

Targets only the `control_plane` inventory group. It applies the cert-manager manifest, waits for the cert-manager CRDs, waits for the cert-manager workloads, and creates a Let's Encrypt HTTP-01 `ClusterIssuer`.

The ACME email is intentionally not stored in this repository by default. Pass it with `-e cert_manager_acme_email=...` or move it into a private inventory variable file that is not committed.

### 80 - NGINX Ingress Controller Installation

```bash
ansible-playbook playbooks/80-install-nginx-ingress.yml
```

Targets only the `control_plane` inventory group. It applies the NGINX Ingress Controller bare-metal manifest, waits for the controller deployment, and keeps the controller `Service` exposed as `NodePort`.

Default NGINX Ingress settings:

| Variable | Default | Purpose |
| --- | --- | --- |
| `nginx_ingress_controller_version` | `v1.15.1` | NGINX Ingress Controller release used for the install manifest |
| `nginx_ingress_namespace` | `ingress-nginx` | Namespace where the controller runs |
| `nginx_ingress_controller_name` | `ingress-nginx-controller` | Controller deployment and service name |
| `nginx_ingress_patch_nodeports` | `true` | Whether Ansible should pin the controller service NodePorts |
| `nginx_ingress_http_node_port` | `31732` | NodePort expected by the current AWS NLB HTTP target group |
| `nginx_ingress_https_node_port` | `32086` | NodePort expected by the current AWS NLB HTTPS target group |

This playbook does not create or modify the AWS Network Load Balancer, target groups, listeners, Route 53 records, or security groups. Those are infrastructure resources and should be managed separately, preferably with Terraform once the design is stable.

## Current Nodes

| Host | Role |
| --- | --- |
| `k8s-control-plane-1` | Kubernetes control plane |
| `k8s-worker-1` | Kubernetes worker |
| `k8s-worker-2` | Kubernetes worker |
