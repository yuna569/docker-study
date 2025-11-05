# ConfigMap 실습: Simple File Server 환경 설정

`ConfigMap`을 사용해 **Simple File Server** 컨테이너의 포트, 로그 경로, 업로드 디렉터리를 이미지 수정 없이 관리합니다.

## ConfigMap이란?

애플리케이션의 설정을 코드와 분리하여 관리하는 Kubernetes 객체입니다. 이미지를 다시 빌드하지 않고도 설정을 변경할 수 있습니다.

## 1. ConfigMap 생성

### 방법 1: 명령어로 생성

```bash
# 포트, 로그, 업로드 디렉터리 설정
kubectl create configmap simple-file-server-config \
  --from-literal=PORT=3001 \
  --from-literal=LOG_PATH=/var/log/app.log \
  --from-literal=UPLOAD_DIR=/var/uploads \
  --namespace 06-volume

# 확인
kubectl get configmap simple-file-server-config -n 06-volume -o yaml
```

### 방법 2: YAML 파일로 생성

**01-configmap.yaml:**

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: simple-file-server-config
  namespace: 06-volume
data:
  PORT: "3001"
  LOG_PATH: "/var/log/app.log"
  UPLOAD_DIR: "/var/uploads"
```

```bash
kubectl apply -f 01-configmap.yaml
```

## 2. Deployment에서 ConfigMap 사용

**02-deployment-configmap.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simple-file-server
  namespace: 06-volume
spec:
  replicas: 2
  selector:
    matchLabels:
      app: simple-file-server
  template:
    metadata:
      labels:
        app: simple-file-server
    spec:
      nodeSelector:
        kubernetes.io/hostname: "worker"
      containers:
      - name: simple-file-server
        image: ghcr.io/jung-geun/simple-file-server:1.0
        imagePullPolicy: IfNotPresent
        ports:
        - containerPort: 3001
        env:
        - name: PORT
          valueFrom:
            configMapKeyRef:
              name: simple-file-server-config
              key: PORT
        - name: LOG_PATH
          valueFrom:
            configMapKeyRef:
              name: simple-file-server-config
              key: LOG_PATH
        - name: UPLOAD_DIR
          valueFrom:
            configMapKeyRef:
              name: simple-file-server-config
              key: UPLOAD_DIR
---
apiVersion: v1
kind: Service
metadata:
  name: simple-file-server
  namespace: 06-volume
spec:
  type: NodePort
  selector:
    app: simple-file-server
  ports:
  - port: 3001
    targetPort: 3001
    nodePort: 30001
```

## 3. 실습: 이미지 빌드 및 배포

```bash
# 1. ConfigMap 생성 (포트 3001)
kubectl apply -f 01-configmap.yaml

# 2. Deployment 및 Service 배포
kubectl apply -f 02-deployment-configmap.yaml

# 3. Pod 상태 확인 (worker 노드 스케줄)
kubectl get pods -n 06-volume -l app=simple-file-server -o wide

# 4. Service 확인
kubectl get svc -n 06-volume simple-file-server

# 5. 접속 테스트
curl http://localhost:30001
```

## 4. 포트 변경 실습

### 포트를 3001에서 3002로 변경

```bash
# ConfigMap 수정
kubectl edit configmap simple-file-server-config -n 06-volume
# PORT: "3001" → PORT: "3002" 로 변경

# 또는 파일을 수정하고 재적용
# 01-configmap.yaml 파일에서 PORT: "3002"로 변경
kubectl apply -f 01-configmap.yaml

# Pod 재시작 (새로운 설정 적용)
kubectl rollout restart deployment -n 06-volume simple-file-server

# 롤아웃 상태 확인
kubectl rollout status deployment -n 06-volume simple-file-server

# 새로운 Pod에서 환경 변수 확인
POD_NAME=$(kubectl get pod -n 06-volume -l app=simple-file-server -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n 06-volume $POD_NAME -- env | grep PORT
```

**주의**: Service의 포트도 함께 변경해야 합니다! `02-deployment-configmap.yaml`의 포트 섹션을 아래처럼 조정합니다.

```yaml
spec:
  ports:
  - port: 3002
    targetPort: 3002
    nodePort: 30002
```

```bash
# Service 포트 변경 후 재배포
kubectl apply -f 02-deployment-configmap.yaml
curl http://localhost:30002
```

## 5. 여러 환경 설정 관리

### 개발 환경 (3001번 포트)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: simple-file-server-config-dev
data:
  PORT: "3001"
  LOG_PATH: "/var/log/app-dev.log"
  ENVIRONMENT: "development"
```

### 스테이징 환경 (3002번 포트)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: simple-file-server-config-staging
data:
  PORT: "3002"
  LOG_PATH: "/var/log/app-staging.log"
  ENVIRONMENT: "staging"
```

### 프로덕션 환경 (3003번 포트)

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: simple-file-server-config-prod
data:
  PORT: "3003"
  LOG_PATH: "/var/log/app-prod.log"
  ENVIRONMENT: "production"
```

Deployment에서 원하는 ConfigMap을 선택:

```yaml
env:
- name: PORT
  valueFrom:
    configMapKeyRef:
      name: simple-file-server-config-dev  # 또는 staging, prod
      key: PORT
```

## 6. ConfigMap 확인 및 디버깅

```bash
# ConfigMap 목록
kubectl get configmap -n 06-volume

# ConfigMap 상세 정보
kubectl describe configmap simple-file-server-config -n 06-volume

# ConfigMap 데이터 확인
kubectl get configmap simple-file-server-config -n 06-volume -o yaml

# Pod에서 환경 변수 확인
kubectl exec -n 06-volume $POD_NAME -- env

# 특정 환경 변수만 확인
kubectl exec -n 06-volume $POD_NAME -- printenv PORT
```

## 7. 정리

```bash
kubectl delete deployment -n 06-volume simple-file-server
kubectl delete service -n 06-volume simple-file-server
kubectl delete configmap -n 06-volume simple-file-server-config
```

## 핵심 정리

✅ **ConfigMap**: 애플리케이션 설정을 코드와 분리  
✅ **환경 변수 주입**: `valueFrom.configMapKeyRef` 사용  
✅ **이미지 재빌드 불필요**: 설정만 변경하고 Pod 재시작  
✅ **다중 환경**: dev, staging, prod 별로 다른 ConfigMap 사용

## 다음 단계

Volume과 PVC를 사용하여 로그 및 업로드 디렉터리를 영속화합니다: [volume.md](./volume.md)
