import json
import os
import sys
import traceback
from base64 import b64decode
from typing import Tuple

import boto3
from resources import (
    handler_of_ec2,
    handler_of_elasticache,
    handler_of_lambda,
    handler_of_rds,
    handler_of_targetgroup,
)
from utils import log_handler, notify_message

REGION_NAME = os.environ.get("REGION_NAME", "ap-northeast-1")

# ロガー初期化
_LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
_logger = log_handler.LoggerHander(log_level=_LOG_LEVEL)

_HANDLER = {
    "ec2": {
        "handler": handler_of_ec2.check_for_ec2,
        "client": "ec2",
        "namespace": "AWS/EC2",
    },
    "elasticache": {
        "handler": handler_of_elasticache.check_for_elasticache,
        "client": "elasticache",
        "namespace": "AWS/ElastiCache",
    },
    "lambda": {
        "handler": handler_of_lambda.check_for_lambda,
        "client": "lambda",
        "namespace": "AWS/Lambda",
    },
    "rds": {
        "handler": handler_of_rds.check_for_rds,
        "client": "rds",
        "namespace": "AWS/RDS",
    },
    "targetgroup": {
        "handler": handler_of_targetgroup.check_for_targetgroup,
        "client": "elbv2",
        "namespace": "AWS/ApplicationELB",
    },
}


def lambda_handler(event: dict, context: object):
    """Lambdaの呼び出しを処理

    パラメーター
    ----------
    event : dict:
        Lambda 関数に渡されるイベントデータ
    context : object
        Lambda 関数のランタイム情報

    戻り値
    -------
    なし
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    try:
        service = event.get("service")
        if service not in _HANDLER:
            return
        # 環境変数をとる

        _CONFIG_FILE_NAME = os.environ.get("ENV_FILE")
        _ACCOUNT_NAME = os.environ.get("ACCOUNT")
        # _PROFILE_NAMEはローカルテスト時だけ使う
        _PROFILE_NAME = os.environ.get("PROFILE_NAME")
        (cloudwatch_client, kms_client, client) = create_clients(_PROFILE_NAME, service)

        config = _find_config(_CONFIG_FILE_NAME, kms_client, service)
        namespace = _HANDLER[service]["namespace"]
        (
            alarms_with_wrong_destination,
            alarms_with_wrong_setting,
            instances_without_alarm,
            setting_success,
            setting_fail,
        ) = _HANDLER[service]["handler"](
            _ACCOUNT_NAME, namespace, config, cloudwatch_client, client
        )

        message_text = notify_message.make_message_for_alart_check(
            _ACCOUNT_NAME,
            service,
            alarms_with_wrong_destination,
            alarms_with_wrong_setting,
            instances_without_alarm,
        )
        # アラーム確認結果を送信する
        notify_message.send_message(config, message_text)

        # 設定成功
        if len(setting_success) != 0:
            message_text = notify_message.make_setting_success_message_text(
                _ACCOUNT_NAME, service, setting_success
            )
            notify_message.send_message(config, message_text)

        # 設定失敗

        if len(setting_fail) != 0:
            message_text = notify_message.make_setting_fail_message_text(
                _ACCOUNT_NAME, service, setting_fail
            )
            notify_message.send_message(config, message_text)

    except Exception as e:
        _logger.error(f"Error: {sys._getframe().f_code.co_name} ")
        _logger.error(traceback.format_exc())
        raise e
    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def create_clients(
    _PROFILE_NAME: str, service: str
) -> Tuple[boto3.client, boto3.client, boto3.client]:
    """AWS クライアントを作成

    パラメーター
    ----------
    _PROFILE_NAME : str
        AWS プロファイル名
    service : str
        AWSのサービス名

    戻り値
    ----------
    Tuple[boto3.client, boto3.client, boto3.client]
        AWS クライアント オブジェクトを含むタプル
        1.CloudWatchクライアント
        2.KMSクライアント
        3. イベントから取得するサービスのクライアント
    """
    if _PROFILE_NAME is None:
        cloudwatch_client = boto3.client("cloudwatch", region_name=REGION_NAME)
        kms_client = boto3.client("kms", region_name=REGION_NAME)
        client = boto3.client(_HANDLER[service]["client"], region_name=REGION_NAME)

    else:
        session = boto3.Session(profile_name=_PROFILE_NAME, region_name=REGION_NAME)
        cloudwatch_client = session.client("cloudwatch")
        kms_client = session.client("kms")
        client = session.client(_HANDLER[service]["client"])

    return (cloudwatch_client, kms_client, client)


def _find_config(_CONFIG_FILE_NAME, kms_client, service):
    """設定ファイルを読み取り
    パラメーター
    ----------
    _CONFIG_FILE_NAME : str
        設定ファイルの名前。
     kms_client: boto3.client
        KMS クライアント オブジェクト。
     サービス: str
        AWS のサービス名。

    戻り値
    ----------
    dict
        設定ファイル
    """

    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    try:
        with open(_CONFIG_FILE_NAME, "r", encoding="utf-8") as file:
            config = json.load(file)

        api_token = kms_client.decrypt(
            CiphertextBlob=b64decode(config["common"]["chatwork"]["api_token"])
        )["Plaintext"]

        config["common"]["chatwork"]["api_token"] = api_token

        config = _dict_merge(config["common"], config[service])

        return config

    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def _dict_merge(d1: dict, d2: dict) -> dict:
    """辞書を再帰的に結合

    パラメーター
    ----------
    d1 : dict
        一番目の辞書。
    d2 : dict
        二番目の辞書。

    戻り値
    ----------
    dict
        結合された辞書
    """
    if isinstance(d1, dict) and (d2, dict):
        return {
            **d1,
            **d2,
            **{
                k: d1[k] if d1[k] == d2[k] else _dict_merge(d1[k], d2[k])
                for k in {*d1} & {*d2}
            },
        }
    else:
        return [
            *(d1 if isinstance(d1, list) else [d1]),
            *(d2 if isinstance(d2, list) else [d2]),
        ]
