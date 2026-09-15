{{- define "accounts.name" -}}
{{- .Chart.Name | trunc 63 | trimSuffix "-" -}}
{{- end }}

{{- define "accounts.namespace" -}}
{{- .Values.namespace.name | default .Release.Namespace -}}
{{- end }}

{{- define "accounts.labels" -}}
app.kubernetes.io/name: {{ include "accounts.name" . }}
app.kubernetes.io/part-of: devops-capstone
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end }}

{{- define "accounts.selectorLabels" -}}
app.kubernetes.io/name: accounts
{{- end }}

{{- define "postgresql.labels" -}}
app.kubernetes.io/name: postgresql
app.kubernetes.io/part-of: devops-capstone
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" }}
{{- end }}

{{- define "postgresql.selectorLabels" -}}
app.kubernetes.io/name: postgresql
{{- end }}
