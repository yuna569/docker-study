# 06. Volume, ConfigMap, Secret

Kubernetes에서 데이터 관리와 설정 관리를 위한 핵심 개념들을 실습합니다.

## 실습 시나리오

Simple File Server와 MySQL을 Kubernetes에 배포하면서 다음을 다룹니다:
- **ConfigMap**: 포트, 로그 경로, 업로드 디렉터리 설정
- **Volume**: hostPath와 PVC로 로그·업로드 데이터 보존
- **Secret**: MySQL 데이터베이스 자격 증명 관리

## 학습 목표

✅ ConfigMap으로 Simple File Server 환경 변수 관리  
✅ Volume(PV/PVC)으로 로그와 업로드 데이터 영속화  
✅ Secret으로 MySQL 자격 증명을 안전하게 관리

## 디렉토리 구조

```
06-volume_configmap_secret/
├── README.md                    # 이 파일
├── app.py                       # Simple File Server 예제 앱
├── Dockerfile                   # 컨테이너 이미지 빌드 파일
├── 00-namespace.yaml            # 실습용 네임스페이스 생성
├── 01-configmap.yaml            # Simple File Server ConfigMap
├── 02-deployment-configmap.yaml # ConfigMap 기반 Deployment/Service
├── 03-volume.yaml               # 업로드용 PV/PVC
├── 04-deployment-volume.yaml    # Volume을 마운트한 Deployment/Service
├── 05-secret.yaml               # MySQL Secret + Deployment + Service
└── 06-full-deployment.yaml      # 전체 통합 배포 예제
```

## 빠른 시작

```bash
# 1. ConfigMap으로 포트 설정
kubectl apply -f 01-configmap.yaml
kubectl apply -f 02-deployment-configmap.yaml

# 2. Volume으로 로그 저장
kubectl apply -f 03-volume.yaml
kubectl apply -f 04-deployment-volume.yaml

# 3. Secret으로 MySQL 비밀번호 관리
kubectl apply -f 05-secret.yaml

# 4. 전체 통합 예제
kubectl apply -f 06-full-deployment.yaml
```

## 상세 가이드

각 단계별 상세 설명을 확인하세요:

1. [ConfigMap 실습](./configmap.md) - 포트/경로 설정 관리
2. [Volume 실습](./volume.md) - 로그·업로드 디렉터리 영속화
3. [Secret 실습](./secret.md) - MySQL 비밀번호 관리
4. [빠른 통합 가이드](./QUICKSTART.md) - 전체 배포 흐름
