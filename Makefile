
# DIR_NAME で直下のディレクトリ内にあるディレクトリをマウント先に指定する

# 参考
# https://zenn.dev/nyancat/articles/20230711-docker-file-switch-image

# 主要アカウント共通
univ:
	export DIR_NAME=universal-lambda  && \
        docker compose  up -d && \
        docker compose  exec python bash
