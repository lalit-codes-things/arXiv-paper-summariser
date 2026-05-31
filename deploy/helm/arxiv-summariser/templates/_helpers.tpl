{{- define "arxiv.name" -}}
arxiv-summariser
{{- end -}}

{{- define "arxiv.labels" -}}
app.kubernetes.io/name: {{ include "arxiv.name" . }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
app.kubernetes.io/managed-by: Helm
platform.arxiv.ai/version: {{ .Values.global.platformVersion | quote }}
{{- end -}}
