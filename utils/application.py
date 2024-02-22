import sys
import traceback
from typing import Tuple

import boto3
from utils import log_handler

_logger = log_handler.LoggerHander()


def put_metric_alarm(cloudwatch_client: boto3.client, alarm_info: dict, namespace: str):
    """アラーム設定を更新または作成する

    パラメーター
    ----------
    cloudwatch_client : boto3.client
        CloudWatch クライアント
    alarm_info : dict
         アラームデータ
    namespace : str
         名前空間

    戻り値
    -------
    なし
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")

    try:
        cloudwatch_client.put_metric_alarm(
            AlarmName=alarm_info["AlarmName"],
            AlarmDescription=alarm_info["AlarmName"],
            ActionsEnabled=alarm_info.get("ActionsEnabled", True),
            OKActions=alarm_info.get("OKActions", []),
            AlarmActions=alarm_info["AlarmActions"],
            InsufficientDataActions=alarm_info.get("InsufficientDataActions", []),
            MetricName=alarm_info["MetricName"],
            Namespace=namespace,
            Statistic=alarm_info.get("Statistic", "Maximum"),
            Dimensions=alarm_info["Dimensions"],
            Period=alarm_info.get("Period"),
            EvaluationPeriods=alarm_info["EvaluationPeriods"],
            Threshold=alarm_info.get("Threshold"),
            ComparisonOperator=alarm_info.get(
                "ComparisonOperator", "GreaterThanOrEqualToThreshold"
            ),
            TreatMissingData=alarm_info.get("TreatMissingData", "missing"),
        )
        _logger.info(f'{alarm_info["AlarmName"]} is created or updated')
    except Exception as e:
        _logger.error(f"Error: {sys._getframe().f_code.co_name} ")
        _logger.error(traceback.format_exc())
        raise e
    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def get_cloudwatch_alarm(cloudwatch_client: boto3.client, namespace: str) -> dict:
    """CloudWatchのアラームを取得する

    パラメーター
    -------
    cloudwatch_client : boto3.client
        CloudWatch クライアント
    namespace : str
        名前空間

    戻り値
    -------
    dict
        アラーム設定を収録した辞書です
    """

    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    try:
        cloudwatch_alarm = {}
        cloud_watch_paginator = cloudwatch_client.get_paginator("describe_alarms")

        page_iterator = cloud_watch_paginator.paginate()
        for page in page_iterator:
            alarms = page["MetricAlarms"]

            for alarm in alarms:
                if alarm["Namespace"] == namespace:
                    # EC2のアラートだけ取り出す
                    cloudwatch_alarm[alarm["AlarmName"]] = alarm

                    dimensions_dict = {
                        dimension["Name"]: dimension["Value"]
                        for dimension in alarm["Dimensions"]
                    }
                    cloudwatch_alarm[alarm["AlarmName"]].update(dimensions_dict)
        return cloudwatch_alarm

    except Exception as e:
        _logger.error(f"Error: {sys._getframe().f_code.co_name} ")
        _logger.error(traceback.format_exc())
        raise e
    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def get_stage_keywords(config: dict, name: str) -> str:
    """インスタンスのステージを決定

    パラメーター
    -------
    config : dict
        設定変数
    name : str
        アラーム名

    戻り値
    -------
    str
        ステージ
    """
    stage = "prod"
    for keyword in config.get("dev_stage_keywords"):
        if keyword in name.lower():
            stage = "dev"
            break
    return stage


def has_valid_action(config: dict, stage: str, alarm: dict) -> bool:
    """指定されたアラームに有効なアクションがあるかどうかを確認

    パラメーター
    -------
    config : dict
        設定変数
    stage : str
        アラームのステージ
    alarm : dict
        検証するアラーム

    戻り値
    -------
    bool:
        アラームに有効なアクションがある場合は True、それ以外の場合は False
    """
    for alarmAction in alarm["AlarmActions"]:
        if stage == "prod":
            if alarmAction in config.get("check_alarm_actions").get("dev"):
                return False
        elif stage == "dev":
            if alarmAction in config.get("check_alarm_actions").get("prod"):
                return False

    for alarmAction in alarm["AlarmActions"]:
        if alarmAction in config.get("check_alarm_actions").get(stage):
            return True

    return False
