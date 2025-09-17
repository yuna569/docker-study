# 02. Docker 기본

이 섹션에서는 Docker의 기본 개념과 핵심 기능들을 학습합니다.

## 📚 학습 목표

- Docker 컨테이너와 이미지의 개념 이해
- Docker 기본 명령어 완전 숙지
- 이미지 pull, tag, push 작업 수행
- Dockerfile 작성 및 이미지 빌드
- Docker Registry 구축 및 활용
- 컨테이너 라이프사이클 관리

## 🔧 사전 준비

1. Docker Desktop 설치 확인

```bash
docker --version
docker-compose --version
```

2. Docker 서비스 실행 확인

```bash
docker ps
```

## 📋 실습 순서

### 1. Docker 기본 명령어 완전 정복

#### 시스템 정보 확인

```bash
# Docker 버전 정보
docker version

# Docker 시스템 정보
docker system info

# Docker 디스크 사용량 확인
docker system df

# 사용하지 않는 리소스 정리
docker system prune

# 모든 미사용 리소스 정리 (주의!)
docker system prune -a
```

#### 이미지 관리 - 기본

```bash
# 이미지 목록 확인
docker images
docker image ls

# 특정 이미지 검색
docker search nginx
docker search python

# 이미지 다운로드 (pull)
docker pull nginx:latest
docker pull nginx:1.21-alpine
docker pull python:3.9
docker pull ubuntu:20.04

# 이미지 상세 정보 확인
docker image inspect nginx:latest

# 이미지 히스토리 확인
docker image history nginx:latest

# 이미지 삭제
docker rmi nginx:latest
docker image rm python:3.9

# 사용하지 않는 이미지 일괄 삭제
docker image prune
```

#### 이미지 태깅 (Tagging)

```bash
# 기존 이미지에 새로운 태그 추가
docker tag nginx:latest my-nginx:v1.0
docker tag nginx:latest localhost:5000/my-nginx:latest

# 여러 태그 추가
docker tag python:3.9 my-python:latest
docker tag python:3.9 my-python:3.9
docker tag python:3.9 registry.example.com/my-python:3.9
```

#### 컨테이너 관리 - 완전 정복

```bash
# 컨테이너 실행 - 기본
docker run hello-world
docker run nginx
docker run -d nginx  # 백그라운드 실행

# 컨테이너 실행 - 고급 옵션
docker run -d --name web-server -p 8080:80 nginx
docker run -d --name db -e MYSQL_ROOT_PASSWORD=secret mysql:8.0
docker run -it --name ubuntu-container ubuntu:20.04 /bin/bash

# 포트 포워딩 다양한 방법
docker run -d -p 8080:80 nginx                    # 호스트:컨테이너
docker run -d -p 127.0.0.1:8080:80 nginx         # IP 지정
docker run -d -P nginx                            # 자동 포트 할당

# 볼륨 마운트
docker run -d -v /host/path:/container/path nginx
docker run -d -v my-volume:/data alpine
docker run -d --mount type=bind,source=/host/path,target=/container/path nginx

# 실행 중인 컨테이너 확인
docker ps
docker container ls

# 모든 컨테이너 확인 (중지된 것 포함)
docker ps -a
docker container ls -a

# 컨테이너 상세 정보
docker inspect web-server
docker container inspect web-server

# 컨테이너 리소스 사용량 확인
docker stats
docker stats web-server

# 컨테이너 내부 접속
docker exec -it web-server /bin/bash
docker exec -it web-server sh

# 컨테이너 조작
docker stop web-server          # 정상 종료
docker kill web-server          # 강제 종료
docker restart web-server       # 재시작
docker pause web-server         # 일시 정지
docker unpause web-server       # 일시 정지 해제

# 컨테이너 삭제
docker rm web-server            # 중지된 컨테이너 삭제
docker rm -f web-server         # 강제 삭제 (실행 중이어도)

# 컨테이너 로그 확인
docker logs web-server
docker logs -f web-server       # 실시간 로그
docker logs --tail 100 web-server  # 마지막 100줄
docker logs --since 1h web-server  # 1시간 전부터

# 컨테이너에서 파일 복사
docker cp web-server:/etc/nginx/nginx.conf ./nginx.conf
docker cp ./index.html web-server:/usr/share/nginx/html/

# 모든 중지된 컨테이너 삭제
docker container prune
```

### 2. Docker 이미지 빌드와 관리

#### Python Flask 애플리케이션 예제

**app.py 파일 생성**

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"
```

**requirements.txt 파일 생성**

```
Flask==3.1.2
```

**Dockerfile 작성**

```dockerfile
FROM ubuntu:22.04

RUN apt-get update && apt-get install -y python3 python3-pip && rm -rf /var/lib/apt/lists/*
RUN pip install flask

COPY app.py /app.py

ENV FLASK_APP=app
ENV HOST=0.0.0.0
ENV PORT=8000

EXPOSE 8000

ENTRYPOINT [ "flask", "run" ]

CMD ["--host=$HOST", "--port=$PORT"]
```

#### Docker 빌드 명령어 상세

```bash
# 기본 빌드
docker build -t my-python-app .

# 태그 지정하여 빌드
docker build -t my-python-app:1.0 .
docker build -t my-python-app:latest .

# 빌드 컨텍스트 지정
docker build -t my-app -f Dockerfile .
docker build -t my-app -f custom.Dockerfile /path/to/context

# 빌드 아규먼트 사용
docker build --build-arg APP_VERSION=2.0 -t my-app:2.0 .

# 캐시 없이 빌드
docker build --no-cache -t my-app .

# 특정 스테이지까지만 빌드 (멀티스테이지)
docker build --target builder -t my-app:builder .

# 빌드 진행상황 상세 출력
docker build --progress=plain -t my-app .
```

#### 빌드된 이미지 실행 및 테스트

```bash
# 컨테이너 실행
docker run -d --name python-container -p 8000:8000 my-python-app:1.0

# 환경 변수 설정하여 실행
docker run -d --name python-v2 -p 8001:8000 -e APP_VERSION=2.0 my-python-app:1.0

# 브라우저에서 확인
# http://localhost:8000

# 실행 중인 애플리케이션 테스트
curl http://localhost:8000
```

### 3. Docker Registry 구축 및 이미지 배포

#### 로컬 Docker Registry 구축

```bash
# 로컬 Registry 컨테이너 실행
docker run -d \
  --name registry \
  --restart=unless-stopped \
  -p 5000:5000 \
  -v registry-data:/var/lib/registry \
  registry:2

# Registry 상태 확인
docker ps | grep registry
curl http://localhost:5000/v2/_catalog
```

#### 이미지 태깅 및 Push/Pull

```bash
# 로컬 Registry용 태그 생성
docker tag my-python-app:1.0 localhost:5000/my-python-app:1.0
docker tag my-python-app:1.0 localhost:5000/my-python-app:latest

# Registry에 이미지 Push
docker push localhost:5000/my-python-app:1.0
docker push localhost:5000/my-python-app:latest

# Registry에서 이미지 목록 확인
curl http://localhost:5000/v2/_catalog
curl http://localhost:5000/v2/my-python-app/tags/list

# 로컬 이미지 삭제 후 Registry에서 Pull
docker rmi localhost:5000/my-python-app:1.0
docker pull localhost:5000/my-python-app:1.0

# Pull한 이미지로 컨테이너 실행
docker run -d --name app-from-registry -p 8002:8000 localhost:5000/my-python-app:1.0
```

#### HTTPS가 적용된 Registry 구축

```bash
# SSL 인증서 생성 (자체 서명)
mkdir -p certs
openssl req -newkey rsa:4096 -nodes -sha256 -keyout certs/domain.key \
  -x509 -days 365 -out certs/domain.crt \
  -subj "/C=KR/ST=Seoul/L=Seoul/O=MyCompany/CN=localhost"

# HTTPS Registry 실행
docker run -d \
  --name secure-registry \
  --restart=unless-stopped \
  -p 5443:5000 \
  -v $(pwd)/certs:/certs \
  -v registry-secure-data:/var/lib/registry \
  -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
  -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
  registry:2
```

#### Registry 인증 추가

```bash
# 기본 인증 설정
mkdir -p auth
docker run --entrypoint htpasswd httpd:2 -Bbn admin password > auth/htpasswd

# 인증이 적용된 Registry 실행
docker run -d \
  --name auth-registry \
  --restart=unless-stopped \
  -p 5001:5000 \
  -v $(pwd)/auth:/auth \
  -v registry-auth-data:/var/lib/registry \
  -e REGISTRY_AUTH=htpasswd \
  -e REGISTRY_AUTH_HTPASSWD_REALM="Registry Realm" \
  -e REGISTRY_AUTH_HTPASSWD_PATH=/auth/htpasswd \
  registry:2

# 인증이 필요한 Registry에 로그인
docker login localhost:5001
# Username: admin
# Password: password

# 로그인 후 이미지 push/pull
docker tag my-python-app:1.0 localhost:5001/my-python-app:1.0
docker push localhost:5001/my-python-app:1.0
```

#### 외부 Registry 활용 (Docker Hub)

```bash
# Docker Hub 로그인
docker login
# 또는 토큰 사용
echo $DOCKER_TOKEN | docker login --username $DOCKER_USERNAME --password-stdin

# Docker Hub용 태그 생성 (username/repository:tag 형식)
docker tag my-python-app:1.0 yourusername/my-python-app:1.0
docker tag my-python-app:1.0 yourusername/my-python-app:latest

# Docker Hub에 Push
docker push yourusername/my-python-app:1.0
docker push yourusername/my-python-app:latest

# 다른 곳에서 Pull
docker pull yourusername/my-python-app:1.0
```

#### Registry 관리 및 정리

```bash
# Registry 내 이미지 목록 확인
curl -s http://localhost:5000/v2/_catalog | jq .

# 특정 이미지의 태그 목록
curl -s http://localhost:5000/v2/my-python-app/tags/list | jq .

# Registry 볼륨 정리
docker volume ls | grep registry
docker volume rm registry-data registry-secure-data registry-auth-data

# Registry 컨테이너 정리
docker stop registry secure-registry auth-registry
docker rm registry secure-registry auth-registry
```

### 4. 볼륨과 네트워크

#### 볼륨 마운트

```bash
# 호스트 디렉토리를 컨테이너에 마운트
docker run -d --name nginx-with-volume \
    -p 8080:80 \
    -v $(pwd)/html:/usr/share/nginx/html \
    nginx

# 도커 볼륨 생성 및 사용
docker volume create my-volume
docker run -d --name app-with-volume \
    -v my-volume:/data \
    alpine sleep 3600
```

#### 네트워크 관리

```bash
# 네트워크 목록 확인
docker network ls

# 사용자 정의 네트워크 생성
docker network create my-network

# 네트워크에 컨테이너 연결
docker run -d --name app1 --network my-network alpine sleep 3600
docker run -d --name app2 --network my-network alpine sleep 3600
```

### 4. 멀티 스테이지 빌드

#### 최적화된 Dockerfile

```dockerfile
# 빌드 스테이지
FROM python:3.9 as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user -r requirements.txt

# 실행 스테이지
FROM python:3.9-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY app.py .
ENV PATH=/root/.local/bin:$PATH
EXPOSE 5000
CMD ["python", "app.py"]
```

## 🧪 실습 과제

1. **Docker 기본 명령어 마스터하기**

   - 다양한 이미지를 pull하고 태그 추가
   - 컨테이너를 다양한 옵션으로 실행
   - 로그 확인 및 리소스 모니터링 실습

2. **Python 애플리케이션 완전 컨테이너화**

   - Flask 웹 애플리케이션 작성
   - 효율적인 Dockerfile 작성
   - 이미지 빌드 및 실행 테스트
   - 다양한 환경 변수로 동작 확인

3. **로컬 Docker Registry 구축**

   - 로컬 Registry 서버 구축
   - 자체 제작 이미지를 Registry에 push
   - 다른 환경에서 pull하여 실행
   - 인증이 적용된 Registry 구성

4. **이미지 최적화 및 보안**

   - 멀티 스테이지 빌드로 이미지 크기 최적화
   - alpine 베이스 이미지 활용
   - 보안 모범 사례 적용 (non-root 사용자 등)

5. **실전 시나리오**
   - 개발 환경용 이미지와 프로덕션용 이미지 분리
   - Docker Hub에 공개 이미지 배포
   - 자동화된 빌드 파이프라인 구성

## 🔍 주요 개념 정리

### Docker 아키텍처

- **이미지**: 애플리케이션과 실행 환경을 포함한 읽기 전용 템플릿
- **컨테이너**: 이미지를 실행한 인스턴스
- **Dockerfile**: 이미지를 빌드하기 위한 명령어 스크립트
- **Registry**: 이미지를 저장하고 배포하는 중앙 저장소
- **Tag**: 이미지의 버전이나 변형을 구분하는 라벨

### 이미지와 컨테이너 관계

```
Dockerfile → (build) → Image → (run) → Container
                         ↓
                     (tag) → Tagged Image → (push) → Registry
```

### Docker Registry 종류

- **Docker Hub**: 공식 퍼블릭 레지스트리
- **Private Registry**: 자체 구축한 프라이빗 레지스트리
- **Cloud Registry**: AWS ECR, Google GCR, Azure ACR 등

### 컨테이너 라이프사이클

1. **Created**: 컨테이너가 생성된 상태
2. **Running**: 컨테이너가 실행 중인 상태
3. **Paused**: 컨테이너가 일시 정지된 상태
4. **Stopped**: 컨테이너가 중지된 상태
5. **Deleted**: 컨테이너가 삭제된 상태

### 이미지 레이어 구조

- Docker 이미지는 여러 레이어로 구성
- 각 Dockerfile 명령어가 새로운 레이어 생성
- 레이어는 캐시되어 빌드 성능 향상
- 하위 레이어 변경 시 상위 레이어 재빌드 필요

## 🎯 체크포인트

**기본 명령어 숙지**

- [ ] Docker 시스템 정보를 확인할 수 있다
- [ ] 이미지를 검색, 다운로드, 삭제할 수 있다
- [ ] 컨테이너를 다양한 옵션으로 실행할 수 있다
- [ ] 실행 중인 컨테이너를 관리할 수 있다

**이미지 관리 및 빌드**

- [ ] 이미지에 태그를 추가하고 관리할 수 있다
- [ ] Dockerfile을 작성하여 이미지를 빌드할 수 있다
- [ ] 빌드 옵션을 활용하여 효율적으로 빌드할 수 있다
- [ ] 멀티 스테이지 빌드로 이미지를 최적화할 수 있다

**Registry 활용**

- [ ] 로컬 Docker Registry를 구축할 수 있다
- [ ] 이미지를 Registry에 push/pull할 수 있다
- [ ] Registry에 인증을 적용할 수 있다
- [ ] Docker Hub와 프라이빗 Registry를 활용할 수 있다

**고급 기능**

- [ ] 볼륨 마운트를 활용하여 데이터를 관리할 수 있다
- [ ] 네트워크를 생성하고 컨테이너를 연결할 수 있다
- [ ] 컨테이너 리소스 사용량을 모니터링할 수 있다
- [ ] 로그를 효과적으로 확인하고 분석할 수 있다

## 📖 참고 자료

### 공식 문서

- [Docker 공식 문서](https://docs.docker.com/)
- [Dockerfile 레퍼런스](https://docs.docker.com/engine/reference/builder/)
- [Docker CLI 레퍼런스](https://docs.docker.com/engine/reference/commandline/cli/)
- [Docker Registry API](https://docs.docker.com/reference/api/registry/latest/)

### 모범 사례

- [Dockerfile 모범 사례](https://docs.docker.com/develop/dev-best-practices/)
- [Docker 보안 가이드](https://docs.docker.com/engine/security/)
- [이미지 최적화 가이드](https://docs.docker.com/dhi/)

### 고급 주제

- [Docker 네트워킹](https://docs.docker.com/network/)
- [Docker 볼륨](https://docs.docker.com/storage/volumes/)
- [멀티 스테이지 빌드](https://docs.docker.com/develop/dev-best-practices/#use-multi-stage-builds)

## 💡 추가 팁

### 성능 최적화

```bash
# 빌드 캐시 최적화를 위한 .dockerignore 사용
echo "node_modules" >> .dockerignore
echo "*.log" >> .dockerignore

# 병렬 빌드 활성화
export DOCKER_BUILDKIT=1
docker build --parallel -t my-app .
```

### 보안 강화

```dockerfile
# Non-root 사용자 생성
RUN addgroup -g 1001 -S nodejs
RUN adduser -S nextjs -u 1001
USER nextjs

# 불필요한 권한 제거
RUN chmod -R 755 /app
```

### 디버깅

```bash
# 컨테이너 내부 파일 시스템 확인
docker exec -it container-name find / -name "*.log" 2>/dev/null

# 이미지 레이어별 크기 확인
docker history my-app:latest

# 컨테이너 리소스 제한
docker run -m 512m --cpus="1.0" my-app
```

## 🔄 다음 단계

다음 강의: [03. Docker Compose](../03-docker-compose/README.md)
