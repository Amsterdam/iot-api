{{/*
Expand the name of the chart.
*/}}
{{- define "helm.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "helm.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- .Release.Name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "helm.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "helm.labels" -}}
helm.sh/chart: {{ include "helm.chart" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "helm.selectorLabels" -}}
app.kubernetes.io/name: {{ .Values.name }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Resource labels
*/}}
{{- define "resource.labels" -}}
{{ include "helm.labels" .root }}
{{ include "resource.selectorLabels" . }}
{{- with .root.Values.labels }}
{{ toYaml . }}
{{- end }}
{{- with .local.labels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
Resource Selector labels
*/}}
{{/* deployedAt: {{ now | unixEpoch | quote }} */}}
{{- define "resource.selectorLabels" -}}
{{ include "helm.selectorLabels" .root }}
{{- with .local.selectorLabels }}
{{ toYaml . }}
{{- end }}
{{- end }}

{{/*
Annotations
*/}}
{{- define "resource.annotations" -}}
{{- with .local.annotations }}
{{- toYaml . }}
{{- end }}
{{- end }}

{{/*
Create the name of the service account to use
*/}}
{{- define "helm.serviceAccountName" -}}
{{- if .Values.serviceAccount.create }}
{{- default (include "helm.fullname" .) .Values.serviceAccount.name }}
{{- else }}
{{- default "default" .Values.serviceAccount.name }}
{{- end }}
{{- end }}

{{/*
Volumes
*/}}
{{- define "pod.volumes" -}}
{{- if or .secrets .volumes }}
volumes:
{{- range .volumes }}
  - name: {{ .name }}
    {{- toYaml .spec | nindent 4}}
{{- end }}
{{- range .secrets }}
  - name: {{ . }}
    csi:
      driver: secrets-store.csi.k8s.io
      readOnly: true
      volumeAttributes:
        secretProviderClass: {{ . }}
{{- end }}
{{- end }}
{{- end }}

{{/*
Volumes
*/}}
{{- define "container.volumeMounts" -}}
{{- if or .secrets .volumes }}
volumeMounts:
{{- range .volumes }}
  - name: {{ .name }}
    mountPath: {{ .mountPath }}
{{- end }}
{{- range .secrets }}
  - name: {{ . }}
    mountPath: /mnt/secrets/{{ . | replace "-" "_" }}
    readOnly: true
{{- end }}
{{- end }}
{{- end }}

{{/*
env
*/}}
{{- define "container.env" -}}
{{- $env := merge (.env | default dict) .root.Values.env }}
{{ with $env }}
env:
  {{- range $name, $value := . }}
  - name: {{ $name | upper | replace "-" "_" }}
    value: {{ $value | quote }}
  {{- end }}
{{- end }}
{{- end }}

{{/*
envFrom
*/}}
{{- define "container.envFrom" -}}
{{- if or .secrets }}
envFrom:
{{- range .secrets }}
  - secretRef: 
      name: {{ . }}
{{- end }}
{{- end }}
{{- end }}

{{/*
tolerations
*/}}
{{- define "pod.tolerations" -}}
{{- if .Values.nodepool }}
tolerations:
  - key: {{ .Values.nodepool }}
    operator: "Equal"
    value: "true"
    effect: "NoSchedule"
{{- end }}
  {{- with .Values.tolerations }}
  {{- . | toYaml | nindent 8 }}
  {{- end }}
{{- end }}

{{/*
pod.securityContext
*/}}
{{- define "pod.securityContext" -}}
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
{{- end }}

{{/*
container.securityContext
*/}}
{{- define "container.securityContext" -}}
securityContext:
  privileged: false
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true
{{- end }}

{{/*
container.resources
*/}}
{{- define "container.resources" -}}
{{- with .resources }}
resources:
  {{- toYaml . | nindent 2 }}
{{- end }}
{{- end }}

{{/*
container.ports
*/}}
{{- define "container.ports" -}}
{{- with .ports }}
ports:
  {{- range . }}
  - containerPort: {{ .port }}
    name: {{ .name }}
  {{- end }}
{{- end }}
{{- end }}

{{/*
container.image
*/}}
{{- define "container.image" -}}
{{- $image := merge (.image | default dict) .root.Values.image }}
{{- $repository := required "A repository configuration is required" $image.repository }}
image: {{ list $image.registry $image.repository | join "/" }}:{{ $image.tag }}
imagePullPolicy: {{ $image.imagePullPolicy | default "IfNotPresent" }}
{{- end }}

{{/*
container.command
*/}}
{{- define "container.command" -}}
{{- with .command }}
command: {{ toYaml . | nindent 2 }}
{{- end }}
{{- end }}
