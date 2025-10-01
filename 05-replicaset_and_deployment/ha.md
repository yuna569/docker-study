# k3s 고가용성(HA) 구성: HAProxy와 Keepalived 사용 가이드

k3s를 HAProxy와 Keepalived를 사용하여 고가용성 클러스터로 구성하는 방법을 알아보겠습니다. 이 구성은 서버 장애 시에도 Kubernetes 클러스터가 계속 작동할 수 있도록 합니다.

## 아키텍처 개요

기본적인 HA 아키텍처는 다음과 같습니다:

- 여러 대의 k3s 서버 노드 (일반적으로 3대 이상)
- 로드 밸런싱을 위한 HAProxy
- 고가용성을 위한 Keepalived (가상 IP 관리)
- 여러 대의 k3s 에이전트 노드 (선택사항)

```
[클라이언트] → [가상 IP] → [HAProxy + Keepalived] → [k3s 서버 노드들]
                                                  → [k3s 에이전트 노드들]
```

## 1. 환경 준비

### 필요한 서버 구성

- k3s 서버 노드: 최소 3대 (예: server1, server2, server3)
- 가상 IP(VIP): 클러스터 액세스용 (예: 10.200.200.130)

### 초기 설정

모든 노드에서 `/etc/hosts` 파일을 수정하여 **k3s.test.com** 의 ip 를 수동으로 지정합니다

```
127.0.0.1 localhost
127.0.1.1 master-1

10.200.200.131 k3s.test.com

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
```

## 2. keepalived 설치(optional)

### Keepalived 설치 및 구성

마스터 1번 노드에서 실행:

```bash
# Keepalived 설치
sudo apt install -y keepalived

# Keepalived 구성 (마스터)
sudo cat > /etc/keepalived/keepalived.conf << EOF
vrrp_script check_haproxy {
    script "killall -0 haproxy"
    interval 2
    weight 2
}

vrrp_instance VI_1 {
    state MASTER
    interface <ens160>
    virtual_router_id 51
    priority 100
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass <k3sHA>
    }
    virtual_ipaddress {
        10.200.200.130
    }
    track_script {
        check_haproxy
    }
}
EOF

# Keepalived 시작
sudo systemctl restart keepalived
sudo systemctl enable keepalived
```

나머지 마스터노드(2,3)에서 실행 (백업 노드):

```bash
# Keepalived 설정 (백업)
sudo cat > /etc/keepalived/keepalived.conf << EOF
vrrp_script check_haproxy {
    script "killall -0 haproxy"
    interval 2
    weight 2
}

vrrp_instance VI_1 {
    state BACKUP
    interface <ens160>
    virtual_router_id 51
    priority 99
    advert_int 1
    authentication {
        auth_type PASS
        auth_pass <k3sHA>
    }
    virtual_ipaddress {
        10.200.200.130
    }
    track_script {
        check_haproxy
    }
}
EOF

sudo systemctl restart keepalived
sudo systemctl enable keepalived
```

### 주의사항

- `interface`: 각 노드의 실제 네트워크 인터페이스 이름으로 변경 필요 (예: eth0, ens160 등)
    - 인터페이스 확인: `ip addr` 명령어로 확인 가능
- `auth_pass`: 보안을 위해 기본값에서 변경 권장
- `virtual_router_id`: 같은 네트워크에서 고유한 값 사용
- `priority`: MASTER는 높은 값, BACKUP은 낮은 값 설정



### hosts 파일 수정

keepalived 를 설정한다면 `10.200.200.131` 대신 `10.300.300.130` 을 vip로 사용하여 수신하기에 hosts 파일을 수정해야합니다.

```
127.0.0.1 localhost
127.0.1.1 master-1

10.200.200.130 k3s.test.com

# The following lines are desirable for IPv6 capable hosts
::1     ip6-localhost ip6-loopback
fe00::0 ip6-localnet
ff00::0 ip6-mcastprefix
ff02::1 ip6-allnodes
ff02::2 ip6-allrouters
```

## 3. k3s 서버 설치

아래에서 `<token>` 은 클러스터 인증을 위한 토큰으로, 첫 번째 서버 노드에서 클러스터 초기화 시 생성됩니다. 이 토큰은 나머지 서버 노드와 에이전트 노드가 클러스터에 참여할 때 필요합니다.

### 첫 번째 k3s 서버 노드 설치

첫 번째 서버 노드에서 실행:

```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="server" \
	K3S_KUBECONFIG_MODE="644" \
	sh -s - --flannel-backend=vxlan \
	--tls-san=k3s.test.com \
	--cluster-init \
	--token <token>
```

![image.png](/assets/05/1.png)

### 나머지 k3s 서버 노드 설치

두 번째, 세 번째 서버 노드에서 실행:

```bash
curl -sfL https://get.k3s.io | sh -s - server \
  --token=<token> \
  --tls-san=k3s.test.com \
  --write-kubeconfig-mode=644 \
  --server=https://k3s.test.com:6443
```

![image.png](/assets/05/2.png)

## 4. HAProxy 설정(optional)

### HAProxy 설치 및 구성

모든 마스터 노드에서 실행:

```bash
# HAProxy 설치
sudo apt update
sudo apt install -y haproxy

# HAProxy 구성
sudo cat > /etc/haproxy/haproxy.cfg << EOF
global
    log /dev/log local0
    log /dev/log local1 notice
    daemon

defaults
    log global
    mode tcp
    option tcplog
    timeout connect 5000
    timeout client 50000
    timeout server 50000

frontend k3s_frontend
		mode tcp
    bind 10.200.200.130:6443
    default_backend k3s_backend

backend k3s_backend
		mode tcp
    option tcp-check
    balance roundrobin
    server master-1 10.200.200.131:6443 check
    server master-2 10.200.200.132:6443 check
    server master-3 10.200.200.133:6443 check
EOF

# HAProxy 재시작
sudo systemctl restart haproxy
sudo systemctl enable haproxy
```

## 4. 클러스터 확인 및 에이전트 노드 추가

### kubeconfig 파일 수정

k3s 설치 후 kubeconfig 파일에서 서버 주소를 변경해야 원격에서도 클러스터에 접근할 수 있습니다:

```bash
# kubeconfig 파일에서 127.0.0.1을 k3s.test.com으로 변경
sudo sed -i 's/127.0.0.1/k3s.test.com/g' /etc/rancher/k3s/k3s.yaml

# 변경 확인
cat /etc/rancher/k3s/k3s.yaml | grep server
```

![image.png](/assets/05/3.png)

이제 이 kubeconfig 파일을 사용하여 클러스터에 원격으로 접근할 수 있습니다. 필요한 경우 이 파일을 다른 시스템으로 복사하여 사용할 수 있습니다.

클러스터 상태 확인:

```bash
# 어느 서버 노드에서든 실행
sudo kubectl get nodes
```

![image.png](/assets/05/4.png)

에이전트 노드 추가 (선택사항):

```bash
curl -sfL https://get.k3s.io | INSTALL_K3S_EXEC="agent" \
 K3S_URL=https://k3s.test.com:6443 \
 sh -s - --token <token>
```

![image.png](/assets/05/5.png)

## 5. 주의사항 및 팁

- **네트워크 방화벽:** k3s 서버 간 통신을 위해 필요한 포트(6443, 8472 등) 오픈 필요
- **데이터베이스:** 기본적으로 SQLite를 사용하나 대규모 클러스터의 경우 외부 데이터베이스(MySQL, PostgreSQL) 권장
- **보안:** 실제 배포 시 더 강력한 인증 및 암호화 설정 필요
- **모니터링:** 클러스터 상태 모니터링을 위한 도구 설정 권장

이 구성은 기본적인 k3s HA 클러스터 설정을 제공합니다. 실제 프로덕션 환경에서는 필요에 따라 추가적인 보안 및 성능 최적화를 고려해야 합니다.

## 6. 로컬에서 k3s 접속

로컬 시스템에서 원격 k3s 클러스터에 접속하려면 다음 단계를 따르세요:

### k3s.yaml 파일 가져오기

마스터 노드에서 kubeconfig 파일을 로컬 시스템으로 복사합니다:

```bash
# 마스터 노드에서 kubeconfig 파일 복사
scp <pieroot>@k3s-master:/etc/rancher/k3s/k3s.yaml ./k3s.yaml
```

복사한 파일에서 서버 주소가 외부에서 접근 가능한 IP 또는 도메인([k3s.test.com](http://k3s.test.com))으로 되어 있는지 확인합니다:

```bash
# 확인 및 필요시 수정
sed -i 's/127.0.0.1/k3s.test.com/g' ./k3s.yaml

# 또는 파일 내용 확인
cat ./k3s.yaml | grep server
```

### hosts 파일 수정

```
# macOS와 Windows에서 hosts 파일 수정하기

# macOS의 경우:
sudo nano /etc/hosts
# 아래 줄 추가:
10.200.200.130 k3s.test.com

# Windows의 경우:
# 메모장을 관리자 권한으로 실행한 후 C:\Windows\System32\drivers\etc\hosts 파일을 열고
# 아래 줄 추가:
10.200.200.130 k3s.test.com
```

macOS에서 hosts 파일 수정 방법:

1. **터미널 열기:** Applications > Utilities > Terminal 또는 Spotlight(⌘+Space)에서 'Terminal' 검색
2. **hosts 파일 열기:** `sudo vi /etc/hosts` 명령어 실행 (관리자 암호 입력 필요)
3. **hosts 파일 편집:** 파일 하단에 `10.200.200.130 k3s.test.com` 추가
4. **변경사항 저장:** `ESC` 입력 후 `:wq` 로 저장 및 나가기

Windows에서 hosts 파일 수정 방법:

1. **관리자 권한으로 메모장 실행:** 시작 메뉴에서 '메모장' 검색 > 마우스 오른쪽 버튼 클릭 > '관리자 권한으로 실행'
2. **hosts 파일 열기:** 메모장에서 File > Open으로 이동 > `C:\Windows\System32\drivers\etc\hosts` 입력 > 파일 형식을 'All Files (*.*)'로 변경 > Open 클릭
3. **hosts 파일 편집:** 파일 하단에 `10.200.200.130 k3s.test.com` 추가
4. **변경사항 저장:** File > Save 메뉴 선택

변경 확인:

1. **ping 테스트:** 터미널 또는 명령 프롬프트에서 `ping k3s.test.com` 실행하여 10.200.200.130 IP로 응답하는지 확인
2. **kubectl 접속 테스트:** `kubectl --kubeconfig=./k3s.yaml cluster-info` 명령으로 클러스터 접속 확인

### KUBECONFIG 설정

kubectl 이 정상적으로 쿠버네티스 클러스터에 접근하기 위해서는 `KUBECONFIG` 환경 변수가 설정되어 있어야 함.

```bash
export KUBECONFIG=./k3s.yaml
```

### kubectl 구성 및 접속 테스트

로컬 시스템에 kubectl이 설치되어 있어야 합니다. 설치 후 다음과 같이 클러스터 연결을 테스트할 수 있습니다:

```bash
# 클러스터 정보 확인
kubectl cluster-info

# 노드 목록 확인
kubectl get nodes

# 네임스페이스 확인
kubectl get ns
```

### 주의사항

- **보안:** kubeconfig 파일은 클러스터 관리 권한을 가지고 있으므로 안전하게 보관해야 합니다.
- **네트워크:** 로컬 시스템에서 [k3s.test.com](http://k3s.test.com)(또는 VIP)으로 접근 가능해야 합니다. 필요시 로컬의 /etc/hosts 파일을 수정하세요.
- **인증서:** TLS 인증서 관련 문제가 발생하면 kubeconfig 파일에서 인증서 설정을 확인하세요.
- **명령행 도구:** kubectl 버전이 서버 버전과 호환되는지 확인하세요.