

## **레플리카셋과 디플로이먼트 차이점**

![image.png](/assets/05/6.png)

실제로는 레플리카셋을 직접 사용하기보다 디플로이먼트(Deployment)를 통해 간접적으로 사용하는 것이 일반적입니다:

- **업데이트 전략**: 디플로이먼트는 롤링 업데이트, 롤백 등 다양한 업데이트 전략을 제공합니다.
- **버전 관리**: 디플로이먼트는 리비전 히스토리를 유지하여 이전 버전으로 쉽게 롤백할 수 있습니다.
- **선언적 업데이트**: 디플로이먼트를 통해 애플리케이션을 선언적으로 업데이트할 수 있습니다.

따라서 실제 프로덕션 환경에서는 디플로이먼트를 사용하는 것이 권장됩니다. 디플로이먼트는 내부적으로 레플리카셋을 생성하고 관리합니다.

## **디플로이먼트 예제**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      nodeSelector:
        # node-role.kubernetes.io/master: "true"
        kubernetes.io/hostname: "worker"
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "250m"
          limits:
            memory: "128Mi"
            cpu: "500m"

```

디플로이먼트의 기본 명령어는 레플리카셋과 유사합니다(kubectl apply, get, describe, scale 등).

## **디플로이먼트(Deployment)의 추가 기능**

디플로이먼트는 레플리카셋을 관리하는 상위 개념으로, 여러 강력한 기능을 제공합니다:

### **1. 롤링 업데이트(Rolling Update)**

롤링 업데이트는 다운타임 없이 애플리케이션을 새 버전으로 업데이트하는 방법입니다:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 3
  selector:
    matchLabels:
      app: nginx
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # 원하는 레플리카 수 이상으로 생성할 수 있는 최대 파드 수
      maxUnavailable: 1  # 업데이트 중 사용할 수 없는 최대 파드 수
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.19  # 이미지 업데이트
```

롤링 업데이트 실행 명령어:

```bash
# 이미지 업데이트
kubectl set image deployment/nginx-deployment nginx=nginx:1.20 --record

# 또는 YAML 파일을 수정한 후
kubectl apply -f deployment.yaml

# 롤링 업데이트 상태 확인
kubectl rollout status deployment/nginx-deployment
```

### **2. 롤백(Rollback)**

문제가 발생했을 때 이전 버전으로 쉽게 되돌릴 수 있습니다:

```bash
# 배포 이력 확인
kubectl rollout history deployment/nginx-deployment

# 특정 리비전의 상세 정보 확인
kubectl rollout history deployment/nginx-deployment --revision=2

# 이전 버전으로 롤백
kubectl rollout undo deployment/nginx-deployment

# 특정 버전으로 롤백
kubectl rollout undo deployment/nginx-deployment --to-revision=2
```

### **3. 배포 일시 중지 및 재개**

배포 과정을 제어할 수 있습니다:

```bash
# 배포 일시 중지
kubectl rollout pause deployment/nginx-deployment

# 변경 사항 적용 (일시 중지 상태에서는 롤링 업데이트가 트리거되지 않음)
kubectl set image deployment/nginx-deployment nginx=nginx:1.21

# 배포 재개
kubectl rollout resume deployment/nginx-deployment
```

### **4. 디플로이먼트 스케일링**

레플리카셋과 유사하게 스케일링이 가능합니다:

```bash
# 명령어로 스케일링
kubectl scale deployment nginx-deployment --replicas=5

# 자동 스케일링 설정
kubectl autoscale deployment nginx-deployment --min=2 --max=5 --cpu-percent=80
```

### **5. 블루-그린 및 카나리 배포**

디플로이먼트를 활용한 고급 배포 전략:

- **블루-그린 배포**: 새 버전(그린)을 완전히 배포한 후, 트래픽을 한 번에 전환합니다. 서비스 셀렉터를 변경하여 구현합니다.
- **카나리 배포**: 새 버전을 일부 사용자에게만 먼저 제공하여 테스트합니다. 동일한 서비스 셀렉터를 사용하되 레이블과 가중치를 활용합니다.

### **6. 디플로이먼트 구성 업데이트**

```bash
# 환경변수 추가
kubectl set env deployment/nginx-deployment NGINX_HOST=example.com

# 리소스 제한 변경
kubectl set resources deployment/nginx-deployment -c=nginx --limits=cpu=200m,memory=512Mi
```

### **7. 주요 차이점 정리**

| **기능** | **레플리카셋** | **디플로이먼트** |
| --- | --- | --- |
| 업데이트 전략 | 지원 안 함 | 롤링 업데이트, 재생성 지원 |
| 롤백 기능 | 지원 안 함 | 리비전 히스토리를 통한 롤백 지원 |
| 일시 중지/재개 | 지원 안 함 | 지원 |
| 사용 목적 | 파드 복제본 관리 | 애플리케이션 배포 및 업데이트 관리 |

실제 운영 환경에서는 대부분의 경우 레플리카셋을 직접 사용하기보다 디플로이먼트를 사용하는 것이 권장됩니다. 디플로이먼트는 더 높은 수준의 추상화를 제공하면서 레플리카셋의 모든 기능을 포함하고 있습니다.
