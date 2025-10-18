# Prometheus + Grafana 설치 가이드

## 1. Helm Repo 추가
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

## 2. 클러스터별 설치
kubectl --context k3d-kr create ns monitoring || true
helm upgrade --install kps prometheus-community/kube-prometheus-stack \
  -n monitoring --kube-context k3d-kr \
  --set grafana.adminPassword=admin \
  --set prometheus.prometheusSpec.scrapeInterval=15s

## 3. 포트포워딩
kubectl --context k3d-kr -n monitoring port-forward svc/kps-grafana 3000:80
# Grafana -> http://localhost:3000  (admin / admin)
