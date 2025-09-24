# 쿠버네티스(Kubernetes, K8s)란?

쿠버네티스는 컨테이너화된 애플리케이션의 배포, 확장 및 관리를 자동화하는 오픈소스 플랫폼입니다. 원래 Google에서 개발되었으며, 현재는 Cloud Native Computing Foundation(CNCF)에서 관리하고 있습니다.

## 쿠버네티스의 주요 기능

- **자동화된 배포 및 롤백:** 애플리케이션 배포와 업데이트를 자동화할 수 있습니다.
- **수평적 확장:** 트래픽에 따라 애플리케이션을 자동으로 확장할 수 있습니다.
- **서비스 검색 및 로드 밸런싱:** 네트워크 트래픽을 분산하여 배포를 안정적으로 유지합니다.
- **자동 복구:** 실패한 컨테이너를 재시작하고, 응답하지 않는 컨테이너를 교체합니다.
- **구성 관리:** 중요한 정보를 저장하고 관리할 수 있는 시스템을 제공합니다.

![image.png](/assets/04/1.png)

## 쿠버네티스 아키텍처

쿠버네티스 클러스터는 **마스터 노드**와 **워커 노드**로 구성됩니다.

### 마스터 노드 (Control Plane)

![image.png](/assets/04/2.png)

### 워커 노드

![image.png](/assets/04/3.png)

### 쿠버네티스 사용의 필요성: 왜 이걸 사용해야 하는가?

기존의 모놀리식(Monolithic) 아키텍처나 수동 컨테이너 관리 방식과 비교했을 때, 쿠버네티스는 다음과 같은 중요한 이점을 제공합니다.

- **확장성(Scalability) 📈**: 트래픽 증가에 따라 애플리케이션을 자동으로 확장하거나 축소할 수 있습니다. 수동으로 서버를 늘리고 줄일 필요가 없어 효율적입니다.
- **고가용성(High Availability) 💯**: 특정 노드나 파드에 문제가 생기면, 쿠버네티스가 자동으로 감지하여 다른 곳에서 파드를 다시 시작합니다. 덕분에 서비스 중단 없이 안정적으로 운영할 수 있습니다.
- **자동화된 배포(Automated Deployment) 🤖**: 애플리케이션의 새로운 버전을 배포할 때, 다운타임 없이 점진적으로 업데이트하는 **롤링 업데이트(Rolling Update)**나 **카나리 배포(Canary Deployment)** 같은 고급 배포 전략을 쉽게 구현할 수 있습니다.
- **자원 효율성(Resource Efficiency) ♻️**: 클러스터 내의 자원을 효율적으로 사용하여 서버 비용을 절감할 수 있습니다. 스케줄러가 파드를 가장 적합한 노드에 배치해줍니다.
- **서비스 디스커버리(Service Discovery) 🌐**: 파드에 문제가 생겨 IP가 변경되어도, 쿠버네티스 서비스(Service)를 통해 파드에 접근할 수 있습니다. 개발자는 IP 주소를 일일이 추적할 필요 없이 서비스 이름으로 통신하면 됩니다.

## K3s란?

K3s는 Rancher Labs에서 개발한 경량 쿠버네티스 배포판입니다. K3s는 작은 메모리 풋프린트와 간단한 설치 과정으로 Edge, IoT 환경이나 개발 환경에 적합합니다.

![image.png](/assets/04/4.png)

## K3s 설치를 위한 사전 조건

- **하드웨어 요구사항:**
  - 서버 노드: 최소 1GB RAM, 1 CPU
  - 에이전트 노드: 최소 512MB RAM, 1 CPU
  - 디스크 공간: 최소 4GB 이상 권장
- **운영 체제:**
  - Linux (Ubuntu, Debian, CentOS 등)
  - x86_64, ARM64, ARMv7 아키텍처 지원
- **네트워크 요구사항:**
  - 노드 간 통신을 위한 네트워크 연결
  - 서버 노드: 6443 포트 오픈 (Kubernetes API)
  - 클러스터 내 통신을 위한 포트: 10250 (Kubelet)
- **필수 소프트웨어:**
  - curl 또는 wget (설치 스크립트 다운로드용)
- **방화벽 설정:**
  - K3s 서버: TCP 6443 (Kubernetes API)
  - K3s 서버: UDP 8472 (Flannel VXLAN, 기본 네트워크 사용 시)
  - 모든 노드: TCP 10250 (Kubelet)

K3s는 표준 쿠버네티스보다 가벼우면서도 완전한 기능을 제공하며, 설치 과정이 매우 간단합니다. 다음 섹션에서는 K3s의 실제 설치 방법에 대해 알아보겠습니다.

### [k3s 설치](./install.md)

### [k3s 제거](./uninstall.md)

## kubectl 이란?

kubectl은 쿠버네티스 클러스터와 상호작용하기 위한 커맨드라인 도구입니다. kubectl을 사용하면 클러스터에 애플리케이션을 배포하고, 리소스를 관리하며, 로그를 확인하는 등 다양한 작업을 수행할 수 있습니다.

### 간단한 kubectl 명령어 예시
- 클러스터 정보 확인:
  ```bash
  kubectl cluster-info
  ```
- 노드 목록 조회:
  ```bash
  kubectl get nodes
  ```
- 파드 목록 조회:
  ```bash
  kubectl get pods
  ```
- 서비스 목록 조회:
  ```bash
  kubectl get services
  ```
- 디플로이먼트 생성:
  ```bash
  kubectl create deployment my-app --image=my-image
  ```
- 디플로이먼트 업데이트:
  ```bash
  kubectl set image deployment/my-app my-app=my-new-image
  ```
- 디플로이먼트 롤백:
  ```bash
  kubectl rollout undo deployment/my-app
  ```
- 파드 로그 확인:
  ```bash
  kubectl logs <pod-name>
  ```
- 파드에 접속:
  ```bash
  kubectl exec -it <pod-name> -- /bin/bash
  ```
- 리소스 삭제:
  ```bash
  kubectl delete pod <pod-name>
  ```
- 디플로이먼트 제거:
  ```bash
  kubectl delete deployment my-app
  ```
- YAML 파일로 리소스 생성:
  ```bash
  kubectl apply -f resource.yaml
  ```