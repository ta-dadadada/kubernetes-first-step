# kubernetes-first-step

## Docker image の準備

はじめに、サンプルとして用意してあるプログラムを Docker image として build し、準備する。

kubernetes で用いる Docker image は、 Docker Hub や ECR などの Docker レジストリに push したものを参照して利用される。
ただし minikube の場合は、ローカル環境の Docker image を利用したデプロイが可能なので、
このチュートリアルではこの機能を利用して進めることにする。

### build

`src` ディレクトリに移動して、わかりやすい名前をつけて build を行う。

```bash
$ docker build -t sample-app:1.0 .
```

ビルドが完了したら、 `docker run` して動作を確認してみる。

```bash
$ docker run -d -p 8000:8000 sample-app:1.0
687fc569a8ce4966cade3e42f282963b212e0c298d2aeecb70135be1ce75cbd6
$ curl -G 172.17.0.1:8000/ | jq -r '.'
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed
100    25  100    25    0     0  12500      0 --:--:-- --:--:-- --:--:-- 12500
{
  "message": "Hello World"
}
```

上記のとおりにバックグラウンドで起動した場合は、使い終わったら止めておく。


```bash
$ docker ps
CONTAINER ID        IMAGE               COMMAND                  CREATED             STATUS              PORTS                    NAMES
687fc569a8ce        sample-app:1.0      "uvicorn main:app --…"   2 minutes ago       Up 2 minutes        0.0.0.0:8000->8000/tcp   epic_leakey
$ docker stop 68
```

## minikube でローカルの docker image を使うための準備

下記を

```bash
$ eval $(minikube docker-env)
$ env | grep DOCKER
DOCKER_CERT_PATH=/home/tada/.minikube/certs
DOCKER_TLS_VERIFY=1
DOCKER_HOST=tcp://192.168.99.100:2376
DOCKER_API_VERSION=1.35
```
