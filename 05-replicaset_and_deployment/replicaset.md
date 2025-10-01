# **Kubernetes에서의 레플리카셋 개념**

레플리카셋(ReplicaSet)은 Kubernetes에서 지정된 수의 파드(Pod) 복제본이 항상 실행되도록 보장하는 리소스입니다. 다음과 같은 주요 특징을 가지고 있습니다:

- **파드 복제본 관리**: 지정된 수의 파드가 항상 실행 상태를 유지하도록 합니다.
- **자동 복구**: 파드가 실패하거나 삭제되면 자동으로 새 파드를 생성합니다.
- **스케일링**: 필요에 따라 파드 수를 쉽게 확장하거나 축소할 수 있습니다.
- **선언적 관리**: 원하는 상태를 선언하면 Kubernetes가 그 상태를 유지하도록 관리합니다.

## **레플리카셋 실습 가이드**

### **1. YAML 파일 작성하기**

먼저 레플리카셋을 정의하는 YAML 파일을 작성합니다. 아래는 간단한 예시입니다:

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: nginx-replicaset
  labels:
    app: nginx
spec:
  replicas: 3  # 원하는 파드 수
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        ports:
        - containerPort: 80
```
```
`apiVersion: apps/v1` : 해당 yaml 파일이 쿠버네티스의 어떤 API 버전을 사용하는지 정의. `Replicaset` 은 `apps/v1` 그룹에 속해 있음
`kind: ReplicaSet` : 쿠버네티스 오브젝트 중 어떤 종류의 오브젝트를 생성할지 명시
`metadata` : `Replicaset` 오브젝트를 식별하기 위한 영역
    `name: nginx-replicaset` : 생성될 Replicaset 의 고유한 이름을 지정. 오브젝트를 조회하거나 관리할때 사용
    `labels` : 키-값 쌍의 라벨을 붙임
        `app: nginx` : `nginx` 라는 값을 가진 `app` 을 `Replicaset` 에 할당
`spec` : Replicaset의 원하는 상태를 정의하는 영역
    `replicas: 3` : 유지할 파드의 복제본 개수를 지정
    `selector` : 어떤 파드가 이 Replicaset에 속하는지 결정하는 라벨 선택자
        `matchLabels` : 라벨과 정확히 일치하는 파드를 선택
            `app: nginx` : `app=nginx` 라벨이 있는 파드만 이 Replicaset이 관리
    `template` : 레플리카셋이 새 파드를 생성할 때 사용하는 템플릿 정의
        `metadata` : 생성될 파드에 대한 메타데이터 정의
            `labels` : 파드에 적용할 라벨
                `app: nginx` : 이 라벨은 `selector.matchLabels`와 일치해야 함
        `spec` : 파드의 스펙 정의
            `containers` : 파드 내에서 실행할 컨테이너 목록
                `name: nginx` : 컨테이너의 이름
                `image: nginx:latest` : 사용할 도커 이미지
                `ports` : 컨테이너가 노출할 포트 목록
                `containerPort: 80` : 컨테이너 내부에서 노출될 포트 번호
```

### **2. 레플리카셋 생성 및 확인**

다음 명령어로 레플리카셋을 생성하고 확인합니다:

```bash
# YAML 파일로 레플리카셋 생성
kubectl apply -f nginx-replicaset.yaml 
#or
kubectl create -f nginx-replicaset.yaml

# 레플리카셋 확인
kubectl get replicasets
# 또는 줄여서
kubectl get rs

# 생성된 파드 확인
kubectl get pods

# 레플리카셋 자세한 정보 확인
kubectl describe rs nginx-replicaset
```

### **3. 레플리카셋 동작 테스트**

레플리카셋의 자가 복구 기능을 테스트합니다:

```bash
# 파드 하나 삭제
kubectl delete pod <pod-name>

# 파드 다시 확인 (자동으로 새 파드 생성)
kubectl get pods

# 레플리카 수 조정하기
kubectl scale replicaset nginx-replicaset --replicas=5
kubectl scale replicaset nginx-replicaset --replicas=2
```

### **4. 레플리카셋 삭제**

테스트 완료 후 정리:

```bash
# 레플리카셋 삭제 (모든 파드도 함께 삭제됨)
kubectl delete rs nginx-replicaset
# 또는
kubectl delete -f nginx-replicaset.yaml
```