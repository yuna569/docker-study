
## 사전 설정

### 각 노드의 hosts 파일 수정

K3s 클러스터를 구성하기 전, 모든 노드에서 마스터 노드의 IP 주소를 [k3s.test.com](http://k3s.test.com) 도메인으로 인식할 수 있도록 hosts 파일을 수정해야 합니다. 아래 단계를 따라 각 노드에서 수정해 주세요.

### 1. 마스터 노드 IP 확인

```bash
# 마스터 노드에서 실행
ip addr show | grep inet
```

출력된 결과에서 마스터 노드의 IP 주소를 확인합니다. 예: 192.168.1.100

### 2. hosts 파일 수정

모든 노드(마스터 및 워커 노드)에서 다음 명령어를 사용하여 hosts 파일을 수정합니다:

```bash
# 관리자 권한으로 hosts 파일 열기
sudo nano /etc/hosts

# 아래 줄을 추가 (마스터 노드 IP 주소를 실제 IP로 변경)
192.168.1.100 k3s.test.com
```

nano 대신 vi나 vim 등 다른 텍스트 편집기를 사용해도 됩니다.

### 3. hosts 파일 적용 확인

```bash
# 설정이 적용되었는지 확인
ping k3s.test.com
```

이제 모든 노드에서 [k3s.test.com](http://k3s.test.com) 도메인을 통해 마스터 노드와 통신할 수 있습니다. 이 설정이 완료된 후 K3s 설치 작업을 진행하세요.

## K3s 설치

```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server" sh -s - --flannel-backend none --token 12345
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server --flannel-backend none" K3S_TOKEN=12345 sh -s -
curl -sfL https://get.k3s.io | K3S_TOKEN=12345 sh -s - server --flannel-backend none
# server is assumed below because there is no K3S_URL
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="--flannel-backend none --token 12345" sh -s - 
curl -sfL https://get.k3s.io | sh -s - --flannel-backend none --token 12345
```

이제 우리가 사용할 K3s 설치 방법에 대해 구체적으로 설명하겠습니다.

## 우리의 K3s 설치 구성

- **서버 URL:** [k3s.test.com](http://k3s.test.com)
- **네트워크 백엔드:** vxlan (Flannel VXLAN 모드)

### 마스터 노드 설치 명령어

```bash
# 마스터 노드 설치
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server" K3S_URL="https://k3s.test.com" K3S_KUBECONFIG_MODE="644" sh -s - --flannel-backend=vxlan
```

이 명령어는 다음 옵션을 사용합니다:

- **INSTALL_K3S_EXEC="server"**: 이 노드를 마스터(서버) 노드로 설정
- **K3S_URL="https://k3s.test.com"**: 클러스터 API 서버의 URL 설정
- **K3S_KUBECONFIG_MODE="644"**: kubeconfig 파일의 권한을 644로 설정하여 일반 사용자도 접근 가능
- **--flannel-backend=vxlan**: Flannel 네트워크 백엔드로 vxlan 사용

### 워커 노드 설치 명령어

```bash
# 워커 노드 설치 (마스터 노드에서 토큰 값 가져온 후)
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="agent --server https://k3s.test.com:6443 --token <토큰값>" sh -s - --flannel-backend=vxlan
```

워커 노드 설치 시 필요한 토큰은 마스터 노드의 `/var/lib/rancher/k3s/server/node-token` 파일에서 확인할 수 있습니다.

### 설치 확인

설치 완료 후 클러스터 상태를 확인하려면:

```bash
# 노드 상태 확인
kubectl get nodes

# 시스템 파드 확인
kubectl get pods -n kube-system
```