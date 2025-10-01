
# Kubernetes 강의 노트

## 목차

1. [HA (High Availability)](#1-ha-high-availability)
2. [ReplicaSet](#2-replicaset)
3. [Deployment](#3-deployment)
4. [Service](#4-service)

---

## [1. HA (High Availability)](ha.md)

### 개요
- 고가용성 클러스터 구성
- 시스템 장애 시에도 서비스 지속성 보장

### 주요 개념
- 로드 밸런싱
- 장애 조치 (Failover)
- 가상 IP (VIP)

### [실습](ha.md)

---

## [2. ReplicaSet](replicaset.md)

### 개요
- Pod의 복제본 수 유지
- 지정된 수의 Pod가 항상 실행되도록 보장

### 주요 기능
- 자동 복구
- 스케일링
- 선언적 관리

### [실습](replicaset.md)

---

## [3. Deployment](deployment.md)

### 개요
- 애플리케이션 배포 및 관리 자동화
- 롤링 업데이트 및 롤백 지원

### 주요 기능
- 롤링 업데이트 (Rolling Update)
- 롤백 (Rollback)
- 선언적 업데이트

### [실습](deployment.md)

---

## [4. Service](service.md)

### 개요
- Pod에 대한 안정적인 네트워크 엔드포인트 제공
- 로드 밸런싱 기능

### Service 타입
- ClusterIP
- NodePort
- LoadBalancer
- ExternalName

### [실습](service.md)
