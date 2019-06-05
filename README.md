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

