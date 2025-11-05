# Volume 실습: Simple File Server 로그와 업로드 디렉터리 영속화

`Volume`을 사용해 **Simple File Server**의 로그와 업로드 파일을 Kubernetes 클러스터 밖으로 안전하게 보존합니다.

## Volume이란?

컨테이너가 재시작되거나 교체되어도 데이터를 유지하도록 도와주는 저장소입니다. Kubernetes에서는 다양한 Volume 타입으로 요구사항에 맞는 스토리지를 구성할 수 있습니다.

## 1. PersistentVolume & PersistentVolumeClaim 생성

`03-volume.yaml`은 업로드 파일을 위한 PV/PVC를 정의합니다. hostPath 기반이지만 PVC를 통해 Pod와 느슨하게 연결합니다.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: upload-pv
  namespace: 06-volume
spec:
  capacity:
    storage: 10Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /tmp/upload
    type: DirectoryOrCreate
  persistentVolumeReclaimPolicy: Retain
  storageClassName: ""
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: upload-pvc
  namespace: 06-volume
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
  volumeName: upload-pv
  storageClassName: ""
```

```bash
kubectl apply -f 03-volume.yaml
kubectl get pv,pvc -n 06-volume
```

> PV는 클러스터 범위 객체라 `namespace` 필드가 무시되지만, 파일과 동일한 패턴으로 관리하기 위해 그대로 두었습니다.

## 2. Deployment에서 Volume 사용

`04-deployment-volume.yaml`은 ConfigMap, Deployment, Service를 한 번에 배포합니다. 로그는 hostPath로, 업로드 디렉터리는 PVC로 구성됩니다.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: simple-file-server
  namespace: 06-volume
spec:
  replicas: 3
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
        volumeMounts:
        - name: log-storage
          mountPath: /var/log/app
        - name: upload-storage
          mountPath: /var/uploads
      
      volumes:
      - name: log-storage
        hostPath:
          path: /tmp/flask-logs
          type: DirectoryOrCreate
      - name: upload-storage
        persistentVolumeClaim:
          claimName: upload-pvc
```

Service는 `NodePort 30001`을 통해 외부에서 접근할 수 있습니다.

```bash
kubectl apply -f 04-deployment-volume.yaml
kubectl get pods -n 06-volume -l app=simple-file-server -o wide
kubectl get svc -n 06-volume simple-file-server
```

> `nodeSelector`가 `worker` 노드를 가리키므로, 실제 노드 이름이 다르면 `kubernetes.io/hostname` 라벨 값을 확인하고 YAML을 수정하세요.

## 3. 로그와 업로드 데이터 확인

```bash
# 애플리케이션 호출로 로그와 파일 생성
for i in {1..3}; do curl http://localhost:30001; done

# Pod 내부 로그 확인
POD_NAME=$(kubectl get pod -n 06-volume -l app=simple-file-server -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n 06-volume $POD_NAME -- cat /var/log/app/app.log

# 호스트 측 로그 확인 (hostPath)
cat /tmp/flask-logs/app.log

# 업로드 PVC가 마운트됐는지 확인
kubectl exec -n 06-volume $POD_NAME -- ls -l /var/uploads
```

## 4. 데이터 영속성 테스트

```bash
# 현재 로그 및 업로드 디렉터리 확인
cat /tmp/flask-logs/app.log
ls -l /tmp/upload

# 모든 Pod 삭제 (ReplicaSet이 다시 생성)
kubectl delete pod -n 06-volume -l app=simple-file-server
kubectl get pods -n 06-volume -l app=simple-file-server -w

# 새 Pod에서도 이전 데이터가 유지되는지 확인
cat /tmp/flask-logs/app.log
ls -l /tmp/upload
```

## 5. 다른 Volume 타입 살펴보기

- **emptyDir**: 같은 Pod 안의 컨테이너 간 임시 데이터 공유에 적합. Pod 삭제 시 데이터가 사라집니다.
- **PersistentVolumeClaim**: NFS, CSI 드라이버 등 외부 스토리지를 Kubernetes 방식으로 추상화합니다.
- **CSI 드라이버**: AWS EBS, S3, Ceph, Longhorn 등 클라우드/온프레미스 스토리지를 사용할 때 필수.

### emptyDir 예시

```yaml
volumes:
- name: shared-data
  emptyDir: {}

volumeMounts:
- name: shared-data
  mountPath: /data
```

### PVC 예시 (커스텀)

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: simple-file-server-logs-pv
spec:
  capacity:
    storage: 1Gi
  accessModes:
    - ReadWriteOnce
  hostPath:
    path: /mnt/simple-file-server/logs
    type: DirectoryOrCreate
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: simple-file-server-logs-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 500Mi
```

## 6. 로그 관리 팁

```bash
# 실시간 로그 tail
tail -f /tmp/flask-logs/app.log

# 로그 파일 크기 확인
du -h /tmp/flask-logs/app.log

# 로그 정리
> /tmp/flask-logs/app.log   # 내용만 초기화
# 또는
rm /tmp/flask-logs/app.log  # 파일 삭제 후 애플리케이션이 다시 생성하도록 유도
```

## 7. 정리

```bash
kubectl delete -f 04-deployment-volume.yaml
kubectl delete -f 03-volume.yaml

sudo rm -rf /tmp/flask-logs
sudo rm -rf /tmp/upload
```

## 핵심 정리

✅ **hostPath + PVC 조합**으로 로그와 업로드 데이터를 분리 관리  
✅ **ConfigMap**으로 로그 경로/업로드 디렉터리 설정값 유지  
✅ **Replica 재시작** 후에도 PVC 덕분에 업로드 데이터 유지  
✅ **nodeSelector**로 특정 노드에 워크로드 고정 가능

## Volume 선택 가이드

| 용도 | Volume 타입 |
|------|-------------|
| 간편한 로컬 로그 저장 | hostPath |
| 업로드 파일 영속화 | PVC (upload-pvc) |
| Pod 간 임시 공유 | emptyDir |
| 외부 스토리지 연동 | NFS, CSI (EBS, S3 등) |

## 다음 단계

Secret을 사용하여 MySQL 비밀번호를 안전하게 관리합니다: [secret.md](./secret.md)
