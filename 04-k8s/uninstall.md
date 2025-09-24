
## K3s 제거하는 방법

K3s를 설치했던 방식에 따라 제거 방법이 다릅니다. 아래는 주요 제거 방법입니다.

### 스크립트를 이용한 제거

K3s는 설치 시 자동으로 제거 스크립트도 제공합니다.

- **서버(마스터) 노드 제거:**

```bash
/usr/local/bin/k3s-uninstall.sh
```

- **에이전트(워커) 노드 제거:**

```bash
/usr/local/bin/k3s-agent-uninstall.sh
```

### 수동으로 정리하기

스크립트가 제대로 작동하지 않을 경우, 다음 단계를 통해 수동으로 정리할 수 있습니다:

- **서비스 중지:**

```bash
systemctl stop k3s
# 에이전트 노드의 경우
systemctl stop k3s-agent
```

- **프로세스 확인 및 종료:**

```bash
ps aux | grep k3s
# 관련 프로세스 종료
kill -9 <PID>
```

- **파일 시스템 정리:**

```bash
# 구성 파일 제거
rm -rf /etc/rancher /etc/kubernetes

# 데이터 제거 (주의: 모든 워크로드 데이터가 삭제됨)
rm -rf /var/lib/rancher /var/lib/kubelet /var/lib/cni

# 로그 제거
rm -rf /var/log/pods /var/log/containers
```

- **네트워크 인터페이스 정리:**

```bash
# Flannel 인터페이스 제거
ip link delete flannel.1
ip link delete cni0
```

### 제거 후 확인

모든 K3s 관련 프로세스가 종료되었는지 확인합니다.

```bash
ps aux | grep k3s
systemctl status k3s
# 또는 에이전트 노드의 경우
systemctl status k3s-agent
```

이렇게 K3s를 완전히 제거하면, 시스템이 초기 상태로 돌아가며 필요한 경우 다시 설치할 수 있습니다.