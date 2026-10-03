# Archived Kustomize Overlays

These dev and prod overlays are historical examples that only changed
the Accounts replica count. They did not provide isolated environments.

They are not deployment entry points. Their original ../../base references
are no longer valid after archival. Do not apply them directly.

The active deployment entry point is:
deploy/applications/accounts/kustomize/overlays/aws-kubeadm/
