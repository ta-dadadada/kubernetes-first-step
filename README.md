# kubernetes-first-step

## Docker image の準備

はじめに、サンプルとして用意してあるプログラムを Docker image として build し、準備する。

kubernetes で用いる Docker image は、 Docker Hub や ECR などの Docker レジストリに push したものを参照して利用される。
ただし minikube の場合は、ローカル環境の Docker image を利用したデプロイが可能なので、
このチュートリアルではこの機能を利用して進めることにする。

## minikube でローカルの docker image を使うための準備

下記を実行し、　docker コマンド使用時に minikube の docker daemon を参照するようにしておく。
build の前にやっておくこと。

```bash
$ eval $(minikube docker-env)
$ env | grep DOCKER
DOCKER_CERT_PATH=/home/tada/.minikube/certs
DOCKER_TLS_VERIFY=1
DOCKER_HOST=tcp://192.168.99.100:2376
DOCKER_API_VERSION=1.35
```

### build

`src` ディレクトリに移動して、わかりやすい名前をつけて build を行う。

```bash
$ docker build -t first-step/sample-app:1.0 .
```

ディレクトリを移動せず、コンテキストを指定してもよい。

```bash
$ docker build -t first-step/sample-app:1.0 src/
```

ビルドが完了したら、 `docker run` して動作を確認してみる。
ホストは `DOCKER_HOST` の IP アドレスを指定すること。

```bash
$ docker run -d -p 8000:8000 first-step/sample-app:1.0
0b5dd0079b714b9f279a9e44555ce29294d1274e1164f1221fa8c953efbd952b
$ curl 192.168.99.100:8000/ | jq -r '.'
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    31  100    31    0     0   6200      0 --:--:-- --:--:-- --:--:--  7750
{
  "message": "Hello kubernetes!"
}

```

上記のとおりにバックグラウンドで起動した場合は、使い終わったら止めておく。


```bash
$ docker ps | grep first-step
0b5dd0079b71        first-step/sample-app:1.0            "uvicorn main:app --…"   About a minute ago   Up About a minute   0.0.0.0:8000->8000/tcp   sleepy_goldberg
$ docker stop 0b5d
0b5d

```

## step1: 初めてのデプロイ

`kubectl apply -f <yaml>` でリソースの作成・更新ができる。
`step1` に準備してある `deployment.yaml` を使って一式を作成してみる。

pod リソースでそれらしいリソースがあり、 `STATUS=Running` ならOK。

```bash
$ kubectl apply -f deployment.yaml 
deployment.apps/sample-app created
$ kubectl get po,svc,deploy
NAME                              READY   STATUS    RESTARTS   AGE
pod/sample-app-5d9c85674d-9c6xh   1/1     Running   0          93s

NAME                 TYPE        CLUSTER-IP   EXTERNAL-IP   PORT(S)   AGE
service/kubernetes   ClusterIP   10.96.0.1    <none>        443/TCP   49d

NAME                               READY   UP-TO-DATE   AVAILABLE   AGE
deployment.extensions/sample-app   1/1     1            1           104s
```

**minikube でローカルの Docker Image を参照できるように設定していたとしても、
`imagePullPolicy` を `Always` にしている場合はリモートレジストリから取得しにいくため、
image の pull に失敗するので注意**


### 動作確認

起動を確認できたら、動作確認する。
まずは コンテナ内部に直接入って curl してみる。

```bash
$ kubectl exec -it sample-app-5767f8747d-mgt5n -- sh
/repos/fast-api-test # curl 127.0.0.1:8000/
{"message":"Hello kubernetes!"}
```

次に、外から動作確認する。
クラスター内部に対する通信は通常許可されていないため、
pod を指定したポートフォワーディングを使って疎通させる。

```bash
$ kubectl port-forward sample-app-5767f8747d-mgt5n 8080:8000
Forwarding from 127.0.0.1:8080 -> 8000
Forwarding from [::1]:8080 -> 8000
```

curl してみる。

```bash
$ curl 127.0.0.1:8080 | jq -r '.'
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    31  100    31    0     0   6200      0 --:--:-- --:--:-- --:--:--  6200
{
  "message": "Hello kubernetes!"
}
```

### rolling update

Pod の更新を行ってみる。
次のように deployment.yaml を変更して、 Pod の数を増やしてみる。


```diff
diff --git a/step1/deployment.yaml b/step1/deployment.yaml
index fa2f18f..db693a8 100644
--- a/step1/deployment.yaml
+++ b/step1/deployment.yaml
@@ -8,7 +8,7 @@ spec:
   selector:
     matchLabels:
       app: sample-app
-  replicas: 1
+  replicas: 3
   template:
     metadata:
       labels:
```

Pod が増えていることがわかる。


```bash
$ kubectl get po
NAME                          READY   STATUS    RESTARTS   AGE
sample-app-5767f8747d-knppn   1/1     Running   0          106s
sample-app-5767f8747d-mgt5n   1/1     Running   0          13m
sample-app-5767f8747d-r7nr6   1/1     Running   0          106s
```

更に、環境変数を変更することで Pod を更新してみる。

```diff
diff --git a/step1/deployment.yaml b/step1/deployment.yaml
index fa2f18f..65d1538 100644
--- a/step1/deployment.yaml
+++ b/step1/deployment.yaml
@@ -8,7 +8,7 @@ spec:
   selector:
     matchLabels:
       app: sample-app
-  replicas: 1
+  replicas: 3
   template:
     metadata:
       labels:
@@ -20,3 +20,6 @@ spec:
           imagePullPolicy: IfNotPresent
           ports:
             - containerPort: 8000
+          env:
+            - name: API_MESSAGE
+              value: "Zen of Python"
```

すると Pod が順番に起動 -> 停止していく様子が確認できる。

```bash
$ kubectl get po
NAME                          READY   STATUS        RESTARTS   AGE
sample-app-5767f8747d-knppn   1/1     Running       0          5m2s
sample-app-5767f8747d-mgt5n   1/1     Running       0          16m
sample-app-5767f8747d-r7nr6   1/1     Terminating   0          5m2s
sample-app-776d8d8756-8rgfm   0/1     Pending       0          0s
sample-app-776d8d8756-x54v2   1/1     Running       0          2s
```

image の変更も試してみよう。

次のようにプログラムを修正して、 build する。
このときタグのフレーバーを変更しておくこと。


```diff
diff --git a/src/main.py b/src/main.py
index 6ca4927..848f69a 100644
--- a/src/main.py
+++ b/src/main.py
@@ -6,7 +6,7 @@ app = FastAPI()
 
 @app.get('/')
 async def root():
-    return JSONResponse({'message': os.getenv('API_MESSAGE', 'Hello kubernetes!')}, status_code=200)
+    return JSONResponse({'message': os.getenv('HOSTNAME', 'Hello kubernetes!')}, status_code=200)
 
 
 @app.get('/health')
```

ビルド。

```bash
$ docker build -t first-step/sample-app:1.1 src/
Sending build context to Docker daemon  43.36MB
Step 1/9 : FROM python:3.6.8-alpine
 ---> 35bb01a3d284
Step 2/9 : WORKDIR repos/fast-api-test
 ---> Using cache
 ---> 03b4d6c65e16
Step 3/9 : RUN pip install --upgrade pip setuptools wheel pipenv
 ---> Using cache
 ---> aa98f90e6940
Step 4/9 : COPY Pipfile Pipfile
 ---> Using cache
 ---> 48ba6447e4d9
Step 5/9 : COPY Pipfile.lock Pipfile.lock
 ---> Using cache
 ---> 8ac152bcfb2a
Step 6/9 : RUN apk add --no-cache --virtual .build-deps     build-base     ca-certificates     curl
 ---> Using cache
 ---> f90a077874eb
Step 7/9 : RUN pipenv install --system
 ---> Using cache
 ---> ae81685f7627
Step 8/9 : COPY main.py .
 ---> 01c954e4b88e
Step 9/9 : CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
 ---> Running in 22e35a1584c3
Removing intermediate container 22e35a1584c3
 ---> 17b5e2d60061
Successfully built 17b5e2d60061
Successfully tagged first-step/sample-app:1.1
```

deployment.yaml もこれに合わせて変更する。


```bash
diff --git a/step1/deployment.yaml b/step1/deployment.yaml
index fa2f18f..bacfa6a 100644
--- a/step1/deployment.yaml
+++ b/step1/deployment.yaml
@@ -3,12 +3,12 @@ kind: Deployment
 metadata:
   name: sample-app
   labels:
-    app-version: "1.0"
+    app-version: "1.1"
 spec:
   selector:
     matchLabels:
       app: sample-app
-  replicas: 1
+  replicas: 3
   template:
     metadata:
       labels:
@@ -16,7 +16,10 @@ spec:
     spec:
       containers:
         - name: api
-          image: first-step/sample-app:1.0
+          image: first-step/sample-app:1.1
           imagePullPolicy: IfNotPresent
           ports:
             - containerPort: 8000
```

apply して、こんどはそれぞれの pod に対して curl を試してみる。

```bash
$ kubectl exec sample-app-6d4bc98559-g6zcw -- curl 127.0.0.1:8000
{"message":"sample-app-6d4bc98559-g6zcw"}
$ kubectl exec sample-app-6d4bc98559-tdgbc -- curl 127.0.0.1:8000 
{"message":"sample-app-6d4bc98559-tdgbc"}
$ kubectl exec sample-app-6d4bc98559-tr2w2 -- curl 127.0.0.1:8000 
{"message":"sample-app-6d4bc98559-tr2w2"}
```

それぞれの Pod にホスト名が設定されていることがわかる。

