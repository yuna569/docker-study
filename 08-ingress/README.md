# 08. Ingress

Ingress는 클러스터 내부 Service에 대한 외부 접근을 HTTP(S) 라우팅 규칙으로 제어하는 리소스입니다. `ClusterIP` 타입 서비스 앞단에 위치하여 하나의 엔드포인트(도메인, 경로)로 여러 서비스를 노출할 수 있습니다.

## 구성 요소

- **Namespace**: `file-server` 네임스페이스 생성 (`namespace.yaml`)
- **ConfigMap & Deployment**: 간단한 파일 업로드 서버 배포 (`deployment.yaml`)
- **Service**: 백엔드 서비스를 `ClusterIP` 로 노출 (`service.yaml`)
- **Ingress**: `file.test.com` 도메인으로 서비스 라우팅 (`ingress.yaml`)

## 사전 준비

- K3s 기본 Ingress Controller(traefik) 또는 별도의 Ingress Controller가 설치되어 있어야 합니다.
- 로컬 테스트 시 `/etc/hosts` 에 마스터 노드 IP와 `file.test.com` 을 매핑합니다.

```bash
sudo sh -c 'echo "<MASTER_NODE_IP> file.test.com" >> /etc/hosts'
```

## 배포 순서

```bash
# 네임스페이스 생성
kubectl apply -f namespace.yaml

# 애플리케이션 및 서비스 배포
kubectl apply -f deployment.yaml
kubectl apply -f service.yaml

# Ingress 생성
kubectl apply -f ingress.yaml
```

## 확인 방법

```bash
# 리소스 상태 확인
kubectl get all -n file-server
kubectl describe ingress simple-file-server-ingress -n file-server

# 브라우저 또는 curl 로 접근
curl http://file.test.com/
```

## 정리

- Ingress 규칙은 기본적으로 HTTP/HTTPS 트래픽을 라우팅합니다.
- `ingress.yaml` 의 `ingressClassName` 을 사용 중인 컨트롤러에 맞게 조정할 수 있습니다.
- 여러 경로 또는 호스트를 추가하여 단일 엔드포인트로 여러 서비스를 노출할 수 있습니다.

