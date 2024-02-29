FROM python:3.11-slim-buster

# 引数
# https://matsuand.github.io/docs.docker.jp.onthefly/compose/compose-file/compose-file-v3/s
ARG UID
ARG GID

WORKDIR /home/app

RUN apt update && apt install -y \
    curl \
    git \
    make

# nodejs, npmのインストール
# RUN curl -sL https://deb.nodesource.com/setup_16.x | bash -
RUN curl -sL https://deb.nodesource.com/setup_20.x | bash -
RUN apt install -y nodejs

# serverless framework のインストール
RUN npm install -g serverless@^3

# 開発用パッケージのインストール
COPY ./requirements-dev.txt ./
RUN pip install -r requirements-dev.txt

# aws profileのコピー
COPY ./aws_config /root/.aws/config

COPY ./entrypoint.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/entrypoint.sh



# ユーザー作成
RUN groupadd -g ${GID} serverless && \
    useradd serverless -u ${UID} -g ${GID} -d /home/serverless -s /bin/bash
# aws profileのコピー
COPY ./aws_config /home/serverless/.aws/config
# パーミッション変更
RUN    chown serverless.serverless -R /home/serverless/
# ユーザー切り替え
USER serverless
# ワークディレクトリ変更
WORKDIR /home/serverless/app

CMD ["entrypoint.sh"]
