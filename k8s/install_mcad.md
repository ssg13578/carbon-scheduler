# MCAD 설치 가이드

## 1. 네임스페이스 생성
for c in k3d-kr k3d-jp k3d-us k3d-eu; do
  kubectl --context $c create ns mcad || true
done

## 2. Controller / CRD 설치
for c in k3d-kr k3d-jp k3d-us k3d-eu; do
  kubectl --context $c apply -n mcad -f https://raw.githubusercontent.com/IBM/multi-cluster-app-dispatcher/main/deploy/crd.yaml
  kubectl --context $c apply -n mcad -f https://raw.githubusercontent.com/IBM/multi-cluster-app-dispatcher/main/deploy/mcad-controller.yaml
done

## 3. 허브 RBAC 권한 추가
for c in k3d-kr k3d-jp k3d-us k3d-eu; do
  kubectl --context $c apply -f k8s/rbac-hub.yaml
done
