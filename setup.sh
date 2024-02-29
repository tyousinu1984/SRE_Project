#!/bin/bash

# 実行ユーザーの名前を取得（IAM ユーザーと同じ名前を想定）
user=$(whoami)
# 実行ユーザーの UID, GID を取得
uid=$(id -u)
gid=$(id -g)

# echo $user $uid $gid

# セッション名を変更
sed -i "s/SESSION_NAME/$user/g" dockerfiles/aws_config

# UID, GID を合わせる
sed -i "s/UID\=1000/UID\=$uid/g"  docker-compose.yml
sed -i "s/GID\=1000/GID\=$uid/g"  docker-compose.yml


# dockerのビルド
DIR_NAME=. docker compose build || exit 1
