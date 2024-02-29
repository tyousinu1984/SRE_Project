#!/bin/bash

# 秘密情報をビルドに含めない
# serverless framework にAWSアカウントを紐付ける
serverless config credentials \
    --provider aws \
    --key $AWS_ACCESS_KEY_ID \
    --secret $AWS_SECRET_ACCESS_KEY \
    --overwrite &&

# exitしないためにベースイメージの`CMD`実行
python
