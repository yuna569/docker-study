# 03. Docker Compose & Docker Swarm

이 섹션에서는 Docker Compose를 사용한 멀티 컨테이너 관리와 Docker Swarm을 활용한 클러스터 오케스트레이션을 학습합니다.

## 📚 학습 목표

- Docker Compose의 개념과 활용법 완전 숙지
- docker-compose.yml 파일 작성 및 서비스 관리
- Replicas를 통한 스케일링 구현
- Docker Swarm 클러스터 구축 및 배포
- 로드 밸런싱과 서비스 디스커버리 이해
- 실제 애플리케이션의 다양한 배포 시나리오 실습

## 🔧 사전 준비

1. Docker Compose 설치 확인
```bash
docker compose --version
# 또는 최신 Docker CLI 내장 명령어
docker compose version
```

2. Docker Swarm 기능 확인
```bash
docker swarm --help
```

3. 이전 강의 (02-docker-basics) 완료 및 app.py 파일 준비

## 📋 실습 순서

### 1. Flask 애플리케이션 준비

#### 사용할 app.py 파일 (02-docker-basics에서 가져옴)
```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, World!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
```

#### requirements.txt
```
Flask==3.1.2
```

#### Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

ENV FLASK_HOST=0.0.0.0
ENV FLASK_PORT=5000

COPY app.py .

EXPOSE 5000

CMD ["python", "app.py"]
```

### 2. Docker Compose 기본 배포

#### docker-compose.yml (기본 배포)
```yaml
version: '3.8'

services:
  flask:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=development
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    depends_on:
      - flask
    restart: unless-stopped
```

#### nginx.conf 설정
```nginx
upstream flask_app {
    server flask:5000;
}

server {
    listen 80;
    # 로그
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;
    
    location / {
        proxy_pass http://flask_app;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

#### 기본 Docker Compose 명령어
```bash
# 서비스 시작 (빌드 포함)
docker compose up --build

# 백그라운드에서 시작
docker compose up -d

# 로그 확인
docker compose logs
docker compose logs flask
docker compose logs -f nginx

# 서비스 상태 확인
docker compose ps

# 서비스 중지
docker compose stop

# 서비스 중지 및 컨테이너 삭제
docker compose down

# 볼륨까지 삭제
docker compose down -v
```

### 3. Replicas를 통한 스케일링 배포

#### docker-compose-replicas.yml
```yaml
version: '3.8'

services:
  flask:
    build: .
    environment:
      - FLASK_ENV=production
    restart: unless-stopped
    deploy:
      mode: replicated
      replicas: 3

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx-lb.conf:/etc/nginx/conf.d/default.conf
    depends_on:
      - flask
    restart: unless-stopped
```

#### 스케일링 명령어
```bash
# replicas 파일로 실행
docker compose -f docker-compose-replicas.yml up -d

# 수동 스케일링
docker compose up -d --scale flask=5

# 스케일링 상태 확인
docker compose ps
```

#### 스케일링 명령어
```bash
# replicas 파일로 실행
docker compose -f docker-compose-replicas.yml up -d

# 수동 스케일링
docker compose up -d --scale flask=5

# 스케일링 상태 확인
docker compose ps

# 특정 서비스만 재시작
docker compose restart flask

# 롤링 업데이트
docker compose up -d --no-deps flask
```

### 4. Docker Swarm을 활용한 클러스터 배포

#### Docker Swarm 클러스터 초기화
```bash
# Swarm 모드 초기화
docker swarm init

# 노드 목록 확인
docker node ls
```

#### docker-swarm-stack.yml
```yaml
version: '3.8'

services:
  flask:
    image: my-flask-app:latest
    build: .
    deploy:
      replicas: 3
      update_config:
        parallelism: 1
        delay: 10s
      restart_policy:
        condition: on-failure
    networks:
      - app-network

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx/nginx-swarm.conf:/etc/nginx/conf.d/default.conf:ro
    deploy:
      replicas: 1
    networks:
      - app-network

  visualizer:
    image: dockersamples/visualizer:stable
    ports:
      - "8080:8080"
    volumes:
      - "/var/run/docker.sock:/var/run/docker.sock"
    deploy:
      replicas: 1
    networks:
      - app-network

networks:
  app-network:
    driver: overlay
```

#### Docker Swarm 명령어
```bash
# 이미지 빌드
docker build -t my-flask-app:latest .

# 스택 배포
docker stack deploy -c docker-swarm-stack.yml myapp

# 스택 상태 확인
docker stack services myapp
docker service ls

# 서비스 스케일링
docker service scale myapp_flask=5

# 스택 제거
docker stack rm myapp

# Swarm 해제
docker swarm leave --force
```

#### Swarm 모니터링 및 관리
```bash
# 노드 상태 모니터링
docker node ls
docker node inspect self

# 서비스 로그 실시간 확인
docker service logs -f myapp_web

# 클러스터 리소스 사용량 확인
docker system df
docker system events

# 서비스 제약사항 설정
docker service update --constraint-add node.labels.environment==production myapp_web

# 시크릿 관리
echo "mysecret" | docker secret create db_password -
docker service update --secret-add db_password myapp_web
```

### 5. 성능 비교 및 모니터링

#### 각 배포 방식의 성능 테스트
```bash
# Apache Bench를 사용한 부하 테스트
# 기본 배포 테스트
docker compose up -d
ab -n 1000 -c 10 http://localhost/

# Replicas 배포 테스트  
docker-compose -f docker-compose-replicas.yml up -d --scale web=3
ab -n 1000 -c 10 http://localhost/

# Swarm 배포 테스트
docker stack deploy -c docker-swarm-stack.yml myapp
ab -n 1000 -c 10 http://localhost/
```

#### 리소스 모니터링
```bash
# Docker Compose 리소스 사용량
docker compose top
docker stats $(docker compose ps -q)

# Swarm 서비스 리소스 사용량
docker service ps myapp_web
docker stats

# 실시간 로그 모니터링
docker compose logs -f --tail=100
docker service logs -f myapp_web
```

## 🧪 실습 과제

### 과제 1: 기본 Docker Compose 배포
1. **Flask + Nginx 구성**
   - 기본 웹 애플리케이션 구축
   - Nginx 리버스 프록시 설정
   - 정상 동작 확인

### 과제 2: Replicas 스케일링 배포
1. **다중 인스턴스 배포**
   - 웹 서비스를 3개 replica로 배포
   - 로드 밸런서 설정으로 부하 분산 확인

### 과제 3: Docker Swarm 클러스터 배포
1. **Swarm 클러스터 구축**
   - 단일 노드 Swarm 클러스터 초기화
   - 스택을 사용한 서비스 배포
   - Visualizer로 클러스터 상태 확인

## 🔍 주요 개념 정리

### Docker Compose vs Docker Swarm

| 특징 | Docker Compose | Docker Swarm |
|------|----------------|---------------|
| **용도** | 개발/테스트 환경 | 프로덕션 클러스터 |
| **스케일링** | 수동 스케일링 | 자동/수동 스케일링 |
| **고가용성** | 단일 호스트 | 다중 노드 클러스터 |
| **로드 밸런싱** | 외부 도구 필요 | 내장 로드 밸런서 |

### 배포 전략 비교
- **기본 Compose**: 간단한 설정, 개발 환경에 적합
- **Replicas 스케일링**: 부하 분산, 가용성 향상
- **Swarm 배포**: 고가용성, 자동 복구, 프로덕션 환경

## 🎯 체크포인트

**Docker Compose 기본**
- [ ] docker-compose.yml 파일을 작성할 수 있다
- [ ] 멀티 서비스 애플리케이션을 배포할 수 있다
- [ ] 서비스 간 의존성을 설정할 수 있다

**스케일링 및 로드 밸런싱**
- [ ] 서비스를 여러 replica로 배포할 수 있다
- [ ] Nginx를 활용한 로드 밸런싱을 설정할 수 있다
- [ ] 수동 스케일링을 수행할 수 있다

**Docker Swarm 클러스터**
- [ ] Swarm 클러스터를 초기화할 수 있다
- [ ] 스택을 사용하여 서비스를 배포할 수 있다
- [ ] 서비스 스케일링을 수행할 수 있다

## 🧪 실습 과제

1. **간단한 웹 스택 구성**
   - Nginx + PHP + MySQL 조합으로 LAMP 스택 구축
   - 각 서비스 간 통신 확인

2. **마이크로서비스 아키텍처**
   - API Gateway + 여러 백엔드 서비스 + 데이터베이스
   - 서비스 간 네트워킹 구성

3. **모니터링 스택**
   - 애플리케이션 + 데이터베이스 + 모니터링 도구 (Prometheus, Grafana)

##  참고 자료

### 공식 문서
- [Docker Compose 공식 문서](https://docs.docker.com/compose/)
- [Compose 파일 레퍼런스](https://docs.docker.com/compose/compose-file/)
- [Docker Swarm 공식 문서](https://docs.docker.com/engine/swarm/)

### 네트워킹 및 스토리지
- [Docker Compose 네트워킹](https://docs.docker.com/compose/networking/)
- [Docker Overlay 네트워크](https://docs.docker.com/network/overlay/)

##  실습 파일 구조

```
03-docker-compose/
├── README.md
├── app.py                          # Flask 애플리케이션
├── requirements.txt                # Python 의존성
├── Dockerfile                      # 이미지 빌드 파일
├── docker-compose.yml              # 기본 Compose 설정
├── docker-compose-replicas.yml     # 스케일링 설정
├── docker-swarm-stack.yml          # Swarm 스택 설정
└── nginx/                          # Nginx 설정 파일들
    ├── nginx.conf                  # 기본 설정
    ├── nginx-lb.conf               # 로드 밸런서 설정
    └── nginx-swarm.conf            # Swarm용 설정
```

## 🚀 빠른 시작 가이드

```bash
# 1. 기본 배포
docker compose up -d
curl http://localhost

# 2. 스케일링 배포  
docker compose -f docker-compose-replicas.yml up -d --scale flask=3
curl http://localhost

# 3. Swarm 배포
docker swarm init
docker build -t my-flask-app:latest .
docker stack deploy -c docker-swarm-stack.yml myapp
curl http://localhost

# 정리
docker compose down
docker stack rm myapp
docker swarm leave --force
```

## 🔄 다음 단계

다음 강의에서는 Kubernetes의 기본 개념과 실습을 진행할 예정입니다.