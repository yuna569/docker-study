# Secret 실습: MySQL Root 비밀번호 관리

Secret을 사용하여 MySQL 데이터베이스의 root 비밀번호를 안전하게 관리합니다.

## Secret이란?

비밀번호, API 키, 인증서와 같은 민감한 정보를 안전하게 저장하는 Kubernetes 객체입니다.

## ConfigMap vs Secret

| 구분 | ConfigMap | Secret |
|------|-----------|--------|
| 용도 | 일반 설정 (포트, 경로 등) | 민감 정보 (비밀번호, 토큰) |
| 저장 방식 | 평문 | Base64 인코딩 |
| 보안 | 낮음 | 높음 (암호화 가능) |

## 1. Secret 생성

### 방법 1: 명령어로 생성

```bash
# MySQL root 비밀번호 생성 (06-volume 네임스페이스)
kubectl create secret generic mysql-secret \
  --from-literal=MYSQL_ROOT_PASSWORD=mySecurePassword123! \
  --namespace 06-volume

# 확인 (값은 Base64로 인코딩되어 보임)
kubectl get secret mysql-secret -n 06-volume -o yaml
```

### 방법 2: YAML 파일로 생성

**05-secret.yaml:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  namespace: 06-volume
type: Opaque
stringData:
  MYSQL_ROOT_PASSWORD: mySecurePassword123!
  MYSQL_DATABASE: flask_db
  MYSQL_USER: flask_user
  MYSQL_PASSWORD: flaskPassword456!
```

```bash
kubectl apply -f 05-secret.yaml
```

**주의**: `stringData`는 평문으로 작성 가능, `data`는 Base64 인코딩 필요

### 방법 3: Base64로 직접 인코딩

```bash
# Base64 인코딩
echo -n 'mySecurePassword123!' | base64
# 출력: bXlTZWN1cmVQYXNzd29yZDEyMyE=

# YAML에 직접 사용
cat <<EOF | kubectl apply -n 06-volume -f -
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
type: Opaque
data:
  MYSQL_ROOT_PASSWORD: bXlTZWN1cmVQYXNzd29yZDEyMyE=
EOF
```

## 2. MySQL with Secret

**05-secret.yaml:**

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
  namespace: 06-volume
type: Opaque
stringData:
  MYSQL_ROOT_PASSWORD: rootPassword123!
  MYSQL_DATABASE: flask_db
  MYSQL_USER: flask_user
  MYSQL_PASSWORD: flaskPassword456!
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mysql
  namespace: 06-volume
spec:
  replicas: 1
  selector:
    matchLabels:
      app: mysql
  template:
    metadata:
      labels:
        app: mysql
    spec:
      containers:
      - name: mysql
        image: mysql:8.0
        ports:
        - containerPort: 3306
        env:
        - name: MYSQL_ROOT_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_ROOT_PASSWORD
        - name: MYSQL_DATABASE
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_DATABASE
        - name: MYSQL_USER
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_USER
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_PASSWORD
        volumeMounts:
        - name: mysql-storage
          mountPath: /var/lib/mysql
      
      volumes:
      - name: mysql-storage
        hostPath:
          path: /tmp/mysql-data
          type: DirectoryOrCreate
---
apiVersion: v1
kind: Service
metadata:
  name: mysql
  namespace: 06-volume
spec:
  selector:
    app: mysql
  ports:
  - port: 3306
    targetPort: 3306
  type: ClusterIP
```

## 3. 실습: MySQL 배포 및 접속

```bash
# 1. Secret과 MySQL 배포
kubectl apply -f 05-secret.yaml

# 2. Pod 상태 확인 (Ready 될 때까지 대기)
kubectl get pods -n 06-volume -l app=mysql -w

# 3. MySQL Service 확인
kubectl get svc -n 06-volume mysql

# 4. MySQL 접속 테스트
POD_NAME=$(kubectl get pod -n 06-volume -l app=mysql -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n 06-volume -it $POD_NAME -- mysql -u root -p
# 비밀번호 입력: rootPassword123!

# MySQL 프롬프트에서:
# mysql> SHOW DATABASES;
# mysql> USE flask_db;
# mysql> CREATE TABLE users (id INT, name VARCHAR(50));
# mysql> INSERT INTO users VALUES (1, 'Alice');
# mysql> SELECT * FROM users;
# mysql> exit
```

## 4. 환경 변수로 Secret 확인

```bash
# Secret 값 확인 (Base64 인코딩된 상태)
kubectl get secret mysql-secret -n 06-volume -o yaml

# Secret 디코딩
kubectl get secret mysql-secret -n 06-volume -o jsonpath='{.data.MYSQL_ROOT_PASSWORD}' | base64 -d
echo ""

# Pod 내부에서 환경 변수 확인
kubectl exec -n 06-volume $POD_NAME -- env | grep MYSQL
```

**주의**: 프로덕션에서는 Secret 값을 직접 출력하지 마세요!

## 5. Flask 애플리케이션에서 MySQL 연결

**app-mysql.py:**

```python
from flask import Flask
import os
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'mysql'),
        user=os.getenv('MYSQL_USER', 'flask_user'),
        password=os.getenv('MYSQL_PASSWORD'),
        database=os.getenv('MYSQL_DATABASE', 'flask_db')
    )

@app.route('/')
def home():
    return "<h1>Flask + MySQL on Kubernetes</h1>"

@app.route('/db-test')
def db_test():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT VERSION()")
        version = cursor.fetchone()
        cursor.close()
        conn.close()
        return f"<h2>MySQL Version: {version[0]}</h2>"
    except Exception as e:
        return f"<h2>Database Error: {e}</h2>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
```

**flask-deployment.yaml:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: flask-app
spec:
  replicas: 1
  selector:
    matchLabels:
      app: flask
  template:
    metadata:
      labels:
        app: flask
    spec:
      containers:
      - name: flask
        image: pieroot/flask-mysql-app:latest
        ports:
        - containerPort: 3000
        env:
        - name: MYSQL_HOST
          value: mysql
        - name: MYSQL_USER
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_USER
        - name: MYSQL_PASSWORD
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_PASSWORD
        - name: MYSQL_DATABASE
          valueFrom:
            secretKeyRef:
              name: mysql-secret
              key: MYSQL_DATABASE
```

## 6. Secret 보안 강화

### 1) Secret을 불변(immutable)으로 설정

```yaml
apiVersion: v1
kind: Secret
metadata:
  name: mysql-secret
immutable: true  # 수정 불가능
type: Opaque
stringData:
  MYSQL_ROOT_PASSWORD: mySecurePassword123!
```

### 2) RBAC으로 접근 제어

```yaml
apiVersion: rbac.authorization.k8s.io/v1
kind: Role
metadata:
  name: secret-reader
rules:
- apiGroups: [""]
  resources: ["secrets"]
  resourceNames: ["mysql-secret"]
  verbs: ["get"]
```

### 3) 파일로 마운트 (환경 변수보다 안전)

```yaml
volumeMounts:
- name: mysql-secret
  mountPath: /etc/mysql-secret
  readOnly: true

volumes:
- name: mysql-secret
  secret:
    secretName: mysql-secret
```

```bash
# 파일로 읽기
kubectl exec $POD_NAME -- cat /etc/mysql-secret/MYSQL_ROOT_PASSWORD
```

## 7. Secret 디버깅

```bash
# Secret 목록
kubectl get secrets -n 06-volume

# Secret 상세 정보 (값은 보이지 않음)
kubectl describe secret mysql-secret -n 06-volume

# Secret 값 확인 (Base64 인코딩)
kubectl get secret mysql-secret -n 06-volume -o yaml

# 특정 키 디코딩
kubectl get secret mysql-secret -n 06-volume -o jsonpath='{.data.MYSQL_ROOT_PASSWORD}' | base64 -d

# Pod에서 환경 변수 확인
kubectl exec -n 06-volume $POD_NAME -- printenv MYSQL_ROOT_PASSWORD
```

## 8. 정리

```bash
kubectl delete -f 05-secret.yaml

# 데이터 삭제
sudo rm -rf /tmp/mysql-data
```

## 핵심 정리

✅ **Secret**: 민감한 정보를 Base64로 인코딩하여 저장  
✅ **환경 변수 주입**: `valueFrom.secretKeyRef` 사용  
✅ **볼륨 마운트**: 파일로 마운트하여 더 안전하게 사용  
✅ **보안**: immutable 설정, RBAC 사용, Git에 커밋 금지

## 주의사항

⚠️ **Git에 커밋하지 마세요**: Secret YAML 파일을 Git에 올리지 마세요  
⚠️ **Base64는 암호화가 아님**: 쉽게 디코딩 가능  
⚠️ **로그에 출력 금지**: Secret 값을 로그에 출력하지 마세요  
⚠️ **접근 제한**: RBAC으로 Secret 접근을 제한하세요

## 대안

프로덕션 환경에서는 다음을 고려하세요:
- **HashiCorp Vault**: 중앙 집중식 Secret 관리
- **AWS Secrets Manager**: AWS에서 제공하는 Secret 관리 서비스
- **Sealed Secrets**: Git에 안전하게 저장 가능한 암호화된 Secret

## 다음 단계

전체를 통합한 실습을 진행합니다: [QUICKSTART.md](./QUICKSTART.md)
