FROM 88888888888.dkr.ecr.ap-northeast-1.amazonaws.com/wordpress-server-construction-with-kusanagi
#FROM python:3
USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
RUN unzip -o awscliv2.zip
RUN ./aws/install --update

COPY wordpress-server-construction/wordpress_server_construction_with_kusanagi.py /opt/wordpress_server_construction_with_kusanagi.py
COPY wordpress-server-construction/requirements.txt /opt/requirements.txt
COPY wordpress-server-construction/src/ /opt/src/
COPY wordpress-server-construction/env/ /opt/env/

WORKDIR /opt/


RUN apt update && \
    apt upgrade -y && \
    pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

ENTRYPOINT ["python3", "wordpress_server_construction_with_kusanagi.py"]