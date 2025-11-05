# 빠른 시작 가이드

## 준비사항

- Docker 설치
- kubectl 설치
- k3s 또는 Kubernetes 클러스터 실행 중

## 1. Docker 이미지 빌드

```bash
cd /Users/pieroot/code/k3s-study/06-volume_configmap_secret
# 필요 시 애플리케이션 이미지를 재빌드할 수 있지만, 예제에서는
# ghcr.io/jung-geun/simple-file-server:1.0 이미지를 바로 사용합니다.
```

## 2. ConfigMap 실습 (5분)

```bash
# 배포
kubectl apply -f 01-configmap.yaml
kubectl apply -f 02-deployment-configmap.yaml

# 테스트
curl http://localhost:30001
curl http://localhost:30001/health

# 정리
kubectl delete -f 02-deployment-configmap.yaml
kubectl delete -f 01-configmap.yaml
```

## 3. Volume 실습 (5분)

```bash
# 배포
kubectl apply -f 03-volume.yaml
kubectl apply -f 04-deployment-volume.yaml

# 로그 생성
for i in {1..5}; do curl http://localhost:30001; done

# 호스트에서 로그 확인
cat /tmp/flask-logs/app.log

# 브라우저에서 로그 확인
curl http://localhost:30001/logs

# 정리
kubectl delete -f 04-deployment-volume.yaml
kubectl delete -f 03-volume.yaml
rm -rf /tmp/flask-logs /tmp/upload
```

## 4. Secret 실습 (10분)

```bash
# 배포
kubectl apply -f 05-secret.yaml

# MySQL 접속
MYSQL_POD=$(kubectl get pod -n 06-volume -l app=mysql -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n 06-volume -it $MYSQL_POD -- mysql -u root -prootPassword123!

# MySQL에서:
# SHOW DATABASES;
# USE flask_db;
# CREATE TABLE test (id INT, name VARCHAR(50));
# INSERT INTO test VALUES (1, 'Hello K8s');
# SELECT * FROM test;
# exit

# 정리
kubectl delete -f 05-secret.yaml
sudo rm -rf /tmp/mysql-data
```

## 5. 전체 통합 실습 (15분)

```bash
# 배포
kubectl apply -f 06-full-deployment.yaml

# Pod 대기
kubectl wait --for=condition=ready pod -n 06-volume -l app=mysql --timeout=60s
kubectl wait --for=condition=ready pod -n 06-volume -l app=simple-file-server --timeout=60s

# 테스트
curl http://localhost:30001
curl http://localhost:30001/logs

# MySQL 테스트
MYSQL_POD=$(kubectl get pod -n 06-volume -l app=mysql -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n 06-volume -it $MYSQL_POD -- mysql -u flask_user -pflaskPassword456! flask_db

# 정리
kubectl delete -f 06-full-deployment.yaml
sudo rm -rf /tmp/flask-logs /tmp/mysql-data
```

## 상세 가이드

- [ConfigMap 상세](./configmap.md)
- [Volume 상세](./volume.md)
- [Secret 상세](./secret.md)
- [전체 배포 YAML](./06-full-deployment.yaml)
