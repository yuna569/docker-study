# 07. DaemonSet

DaemonSet은 클러스터의 모든 노드(또는 특정 노드들)에 파드를 하나씩 배포하는 컨트롤러입니다. 주로 모니터링 에이전트, 로그 수집기 등과 같이 각 노드에서 실행되어야 하는 작업에 사용됩니다.

## 구성 요소

1. **Namespace**: `monitoring` 네임스페이스 생성
2. **ServiceAccount**: `node-exporter`와 `prometheus` 서비스 어카운트 생성
3. **RBAC**: Prometheus가 Kubernetes 리소스를 탐색할 수 있도록 권한 부여
4. **Node Exporter DaemonSet**: 각 노드에 시스템 메트릭 수집기 배포
5. **Services**: 
   - Node Exporter 서비스 (ClusterIP, NodePort)
   - Prometheus 서비스 (ClusterIP, LoadBalancer)
   - Grafana 서비스 (ClusterIP, LoadBalancer)
6. **Prometheus**: 메트릭 수집 및 저장
7. **Grafana**: 메트릭 데이터 시각화

## Node Exporter DaemonSet

Node Exporter는 시스템 메트릭을 수집하여 Prometheus가 수집할 수 있도록 하는 도구입니다. DaemonSet으로 배포되어 각 노드에서 실행됩니다.

### 특징

- `prom/node-exporter:v1.8.1` 이미지 사용
- hostNetwork 사용으로 노드의 네트워크 직접 접근
- control-plane/master 노드에도 배포 가능 (tolerations 설정)
- rootfs 마운트를 통해 시스템 정보 수집

### 배포 방법

```bash
# 네임스페이스 생성
kubectl apply -f namespace.yaml

# 서비스 어카운트 생성
kubectl apply -f serviceaccount.yaml

# Node Exporter DaemonSet 배포
kubectl apply -f node-exporter-daemonset.yaml

# 서비스 생성
kubectl apply -f node-exporter-service.yaml
```

### 확인 방법

```bash
# DaemonSet 상태 확인
kubectl get daemonset -n monitoring

# Pod 상태 확인
kubectl get pods -n monitoring -l app=node-exporter

# 서비스 확인
kubectl get svc -n monitoring
```

## Prometheus & Grafana

Prometheus는 메트릭을 수집하고 저장하는 모니터링 시스템입니다. Grafana는 Prometheus에서 수집한 데이터를 시각화하는 대시보드 도구입니다.

### 배포 방법

```bash
# Prometheus 설정 및 배포
kubectl apply -f grafana.yaml

# Prometheus 서비스 생성
kubectl apply -f prometheus-service.yaml

# Grafana 서비스 생성
kubectl apply -f grafana-service.yaml
```

### 확인 방법

```bash
# Prometheus 상태 확인
kubectl get pods -n monitoring -l app=prometheus

# Grafana 상태 확인
kubectl get pods -n monitoring -l app=grafana

# 서비스 확인
kubectl get svc -n monitoring
```

### 접근 정보

- Prometheus: `http://<MASTER_NODE_IP>:9090`
- Grafana: `http://<MASTER_NODE_IP>:3000` (기본 계정: admin/admin)