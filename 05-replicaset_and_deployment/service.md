# k3s의 서비스(Service) 개념 이해하기

## 1. 서비스(Service)란?

k3s는 경량화된 쿠버네티스(Kubernetes) 배포판으로, 쿠버네티스의 핵심 개념인 '서비스(Service)'를 그대로 구현합니다. 쿠버네티스 서비스는 다음과 같은 중요한 역할을 합니다:

- 포드(Pod) 집합에 대한 단일 접점 제공
- 포드의 IP 주소가 변경되더라도 안정적인 네트워크 엔드포인트 유지
- 로드 밸런싱 기능 제공
- 서비스 디스커버리 메커니즘 구현

## 2. 서비스가 필요한 이유

쿠버네티스/k3s 환경에서 포드는 일시적인 존재입니다. 포드는:

- 언제든지 생성되거나 삭제될 수 있음
- 스케일링, 업데이트, 장애 시 재생성 과정에서 IP가 변경됨
- 여러 복제본이 존재할 수 있음

이런 환경에서 안정적인 네트워크 통신을 위해 서비스라는 추상화 계층이 필요합니다.

## 3. 서비스 유형

k3s에서 사용 가능한 서비스 유형은 다음과 같습니다:

### 3.1 ClusterIP (기본 타입)

클러스터 내부에서만 접근 가능한 서비스입니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-internal-service
spec:
  selector:
    app: nginx
  ports:
  - port: 8080 # 파드에 접근할때 사용할 포트
    targetPort: 80 # 실제 파드의 포트
  type: ClusterIP
```

### 3.2 NodePort

클러스터 외부에서 접근할 수 있도록 각 노드의 특정 포트를 서비스에 할당합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-nodeport-service
spec:
  selector:
    app: nginx
  ports:
  - port: 8080
    targetPort: 80
    nodePort: 30007  # 30000-32767 범위에서 지정. 외부에서 접근에 사용할 포트
  type: NodePort
```

### 3.3 LoadBalancer

클라우드 제공업체의 로드 밸런서를 프로비저닝하여 서비스에 외부 IP를 할당합니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-loadbalancer-service
spec:
  selector:
    app: nginx
  ports:
  - port: 8080 # 외부에서 접근할 lb port
    targetPort: 80 # 실제 파드의 포트
  type: LoadBalancer
```

### 3.4 ExternalName

외부 서비스를 k3s 클러스터 내부에서 접근할 수 있게 해주는 특별한 유형입니다.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-externalname-service
spec:
  type: ExternalName
  externalName: my.database.example.com
```

## 4. 서비스 디스커버리

**서비스 디스커버리**는 마이크로서비스와 같이 분산된 환경에서, **하나의 서비스(또는 클라이언트)가 다른 서비스의 네트워크 위치(IP 주소와 포트)를 동적으로 찾아내는 과정 또는 메커니즘**을 의미합니다.

### **왜 서비스 디스커버리가 필요한가?**

전통적인 환경에서는 서버의 IP 주소가 잘 바뀌지 않았기 때문에, 설정 파일에 IP 주소를 직접 입력해도 큰 문제가 없었습니다.

하지만 Kubernetes와 같은 클라우드 네이티브 환경에서는 상황이 완전히 다릅니다:

1. **동적인 IP 주소:** 파드(Pod)는 언제든지 종료되고 재시작될 수 있습니다. 파드가 재시작되면 **완전히 새로운 IP 주소**를 할당받습니다.
2. **확장성(Scalability):** 트래픽 증가 시 Deployment는 파드 수를 3개에서 10개로 빠르게 확장할 수 있습니다. 이때 새로 생성된 7개 파드는 모두 고유한 IP 주소를 가집니다.
3. **위치 투명성(Location Transparency):** 파드는 클러스터 내 어떤 노드(서버)에서 실행될지 미리 알 수 없습니다.

이런 환경에서 프론트엔드 파드가 백엔드 파드에 접속해야 한다고 가정해보세요. 백엔드 파드의 IP가 계속 변경되고 개수도 수시로 달라진다면, 어떻게 연결 주소를 찾아낼 수 있을까요? **IP 주소를 하드코딩하는 방식은 불가능합니다.**

k3s는 두 가지 주요 서비스 디스커버리 메커니즘을 제공합니다:

### 4.1 환경 변수

k3s는 활성 서비스에 대한 환경 변수를 Pod에 자동으로 주입합니다. 예를 들어 'FOO' 서비스가 있다면:

- FOO_SERVICE_HOST: 서비스의 IP
- FOO_SERVICE_PORT: 서비스의 포트

이미 시작된 Pod는 새로운 서비스에 대한 환경 변수를 받아올 수 없기에 잘 사용되지 않는 방법입니다.

### 4.2 DNS

더 일반적인 방법으로, k3s는 CoreDNS를 사용하여 자동으로 DNS 레코드를 생성합니다:

- `서비스명.네임스페이스.svc.cluster.local`
- 같은 네임스페이스 내에서는 간단히 `서비스명`으로 접근 가능

## 5. 서비스 라우팅 방식

k3s 서비스는 다음과 같은 방식으로 트래픽을 라우팅합니다:

- **레이블 셀렉터(Label Selector):** 서비스와 포드를 연결하는 메커니즘
- **kube-proxy:** 각 노드에서 실행되며 서비스에 대한 네트워크 규칙 관리
- **iptables 규칙:** 실제 트래픽 라우팅을 담당 (기본 모드)

## 6. 실습: k3s에서 서비스 생성 및 활용

### 6.1 배포 생성하기

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
      containers:
      - name: nginx
        image: nginx:1.29
        ports:
        - containerPort: 80
```

### 6.2 서비스 생성하기

```yaml
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
  type: LoadBalancer
```

### 6.3 서비스 상태 확인

```bash
kubectl get services
kubectl describe service nginx-service
```

## 7. 서비스 트러블슈팅

서비스가 예상대로 작동하지 않을 때 확인해야 할 사항들:

- **셀렉터 확인:** 서비스의 셀렉터가 포드의 레이블과 일치하는지 확인
- **엔드포인트 확인:** `kubectl get endpoints [서비스명]`으로 확인
- **포드 상태 확인:** 대상 포드가 정상적으로 실행 중인지 확인
- **네트워크 정책:** 네트워크 정책이 통신을 차단하지 않는지 확인

## 8. 결론 및 모범 사례

k3s 서비스를 효과적으로 활용하기 위한 모범 사례:

- **명확한 레이블링 전략:** 일관된 레이블 사용으로 서비스와 포드 연결 관리
- **적절한 서비스 타입 선택:** 사용 사례에 맞는 서비스 타입 선택
- **헬스 체크 구현:** 포드의 레디니스/라이브니스 프로브 설정
- **서비스 메시 고려:** 복잡한 마이크로서비스 아키텍처에는 Istio와 같은 서비스 메시 도입 검토

k3s의 서비스는 쿠버네티스의 핵심 개념을 그대로 유지하면서도, 가벼운 환경에서 효율적으로 작동하도록 최적화되어 있습니다. 이러한 서비스 추상화를 통해 동적인 컨테이너 환경에서도 안정적인 네트워크 통신을 구현할 수 있습니다.

