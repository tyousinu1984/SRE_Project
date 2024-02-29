# sls-lambda-docker

## 概要

ローカルでServerless Frameworkを用いてLambda開発をおこなうためのDocker環境です。

## 想定する環境

- Python 3.11.x
- Node.js 20.x
- serverless (sls) framework v3


## このブランチを利用するために必要なもの

- OS
    - Linux
    - macOS
    - Windows
        - WSL
- 必要な Unix コマンド
    - id
    - whoami
    - sed
    - docker
        `docker compose` が使えるもバージョン前提
    - make




## 利用開始方法

### 1. このをcloneする

### 2. Serverless Frameworkを使うための認証情報を用意する

Serverless FrameworkはAWSへのデプロイ・リソース作成をおこなうので、アクセス権限を付与してあげる必要があります。

```sh
# .envのひな形をコピー
cp .env.example .env

# .env の中身
cat .env
AWS_ACCESS_KEY_ID=
AWS_SECRET_ACCESS_KEY=
```

アクセスキーとシークレットがわからない場合、新しく作成する必要があります。

- 「[AWS IAM 認証情報](https://us-east-1.console.aws.amazon.com/iam/home#/security_credentials?credentials=iam)」→「アクセスキーの作成」

作成したアクセスキーとシークレットを上の `.env` に記載してください。

AWS CLI などを使用したことがある人は、ホストPCの`~/.aws/credentials`にアクセスキーとシークレットが記載されている可能性があります。


### 3. 初期設定スクリプトを実行する


**docker コマンドを内部で利用します。事前に Docker デーモン（Windows なら Docker Desktop）を起動しておいてください。**

```sh
bash setup.sh 
```

これで、Docker 環境が利用可能になります。


### 4. ソースコードを変更したいレポジトリを直下に clone する


`setup.sh` などがあるディレクトリに、対象のCodecommit レポジトリをダウンロードします。

以下、coretech_lambda レポジトリの場合です。 


ディレクトリ階層構造は、以下のようになります。

```
sls-lambda-docker
├── universal-lambda
│   └── ソースコード
├── dockerfiles
│   ├── Dockerfile
│   ├── aws_config
│   ├── entrypoint.sh
│   └── requirements-dev.txt
├── vscode-settings
├── Makefile
├── README.md
├── docker-compose.yml
└── setup.sh
```



### 5. デプロイ時は、対象 Docker コンテナに入る

以下コマンドを実行することで、core-tech アカウントへのデプロイ用コンテナに自動で入ります。

```bash
make univ
```


### 6. デプロイ

コンテナ上で以下コマンドを実施します。

```bash
# core-tech アカウントの場合
## dev ステージ
make deploy_core_dev

## prod ステージ
make deploy_core_prod
```



## 参考

[/SREチーム/業務運用手順/Lambda関数開発/](https://wiki.core-tech.jp/SREチーム/業務運用手順/Lambda関数開発/)
