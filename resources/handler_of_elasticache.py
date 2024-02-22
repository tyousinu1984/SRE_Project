import os
import sys
import traceback
from typing import Tuple

import boto3
from utils import application, log_handler

# ロガー初期化
_LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
_logger = log_handler.LoggerHander(log_level=_LOG_LEVEL)


def check_for_elasticache(
    account_name: str,
    namespace: str,
    config: dict,
    cloudwatch_client: boto3.client,
    elasticache_client: boto3.client,
) -> Tuple[dict, dict, dict, dict]:
    """アラーム設定を確認し、自動的に適用

    パラメーター
    ----------
    account_name : str
        AWS アカウントの名前
    namespace : str
        名前空間
    config : dict
        設定ファイル
    cloudwatch_client : boto3.client
        CloudWatchの Boto3 クライアント
    elasticache_client : boto3.client
        ElastiCacheの Boto3 クライアント

    戻り値
    -------
    Tuple[dict,dict,dict,dict]
        以下を表すdictのセットを含むTuple:
        1. 間違った宛先のアラーム
        2. 間違った設定のアラーム
        3. アラームのないインスタンス
        4. 設定成功のアラーム
        5. 設定失敗のアラーム
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")

    setting_success, setting_fail = {}, {}

    (
        alarms_with_wrong_destination,
        alarms_with_wrong_setting,
        instances_without_alarm,
    ) = _check_alarm_for_elasticatcahe(
        namespace, config, cloudwatch_client, elasticache_client
    )

    if not (
        len(alarms_with_wrong_destination) == 0
        and len(alarms_with_wrong_setting) == 0
        and len(instances_without_alarm) == 0
    ):
        (
            setting_success,
            setting_fail,
        ) = _attach_alarm_for_elasticache(
            account_name,
            namespace,
            config,
            cloudwatch_client,
            alarms_with_wrong_destination,
            alarms_with_wrong_setting,
            instances_without_alarm,
        )
    _logger.info(f"{sys._getframe().f_code.co_name} End.")

    return (
        alarms_with_wrong_destination,
        alarms_with_wrong_setting,
        instances_without_alarm,
        setting_success,
        setting_fail,
    )


########### アラームチェック ##############
def _check_alarm_for_elasticatcahe(
    namespace: str,
    config: dict,
    cloudwatch_client: boto3.client,
    elasticache_client: boto3.client,
) -> Tuple[dict, dict, dict, dict]:
    """ElastiCacheアラーム設定を確認

    パラメーター
    ----------
    namespace : str
        ElastiCache の名前空間
    config : 辞書
        設定ファイル
    Cloudwatch_client : boto3.client
        CloudWatch 用の Boto3 クライアント
    elasticache_client : boto3.client
        ElastiCache 用の Boto3 クライアント

    戻り値
    -------
    Tuple[dict, dict, dict]
        以下を表すdictを含むTuple:
        1. 間違った宛先のアラーム
        2. 間違った設定のアラーム
        3. アラームのないインスタンス
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    try:
        instance_info_dict = _get_instance_info(config, elasticache_client)
        cloudwatch_alarm = application.get_cloudwatch_alarm(
            cloudwatch_client, namespace
        )

        (
            alarms_with_wrong_destination,
            alarms_with_wrong_setting,
        ) = _verify_cloudwatch_alarms(config, instance_info_dict, cloudwatch_alarm)

        instances_without_alarm = _whether_alarm_has_been_set(
            config, instance_info_dict.copy(), cloudwatch_alarm
        )

        return (
            alarms_with_wrong_destination,
            alarms_with_wrong_setting,
            instances_without_alarm,
        )

    except Exception as e:
        _logger.error(f"Error: {sys._getframe().f_code.co_name} ")
        _logger.error(traceback.format_exc())
        raise e
    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def _get_instance_info(config: dict, elasticache_client: boto3.client):
    """Elasticache クラスターに関する情報を取得

    パラメーター
    ----------
    config : dict
        設定ファイル
    elasticache_client : boto3.client
        Elasticache 用の Boto3 クライアント

    戻り値
    -------
    dict
        Elasticache クラスターに関する情報
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    instance_info_dict = {}
    # ページャーで全て取得
    paginator = elasticache_client.get_paginator("describe_cache_clusters")
    page_iterator = paginator.paginate()

    # instanceIDを取得
    for page in page_iterator:
        for instance in page["CacheClusters"]:
            arn = config["cluster_arn_prefix"] + instance["CacheClusterId"]
            # tagを取得
            tag_res = elasticache_client.list_tags_for_resource(ResourceName=arn)

            check_flag = True
            for tag in tag_res["TagList"]:
                if tag["Key"] == "CheckAlarmSetting":
                    if tag["Value"].upper() == "NO":
                        check_flag = False
                        break
            if check_flag:
                instance_info_dict[instance["CacheClusterId"]] = {
                    "check_metric_names": config["check_metric_names"]
                }
    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return instance_info_dict


def _whether_alarm_has_been_set(
    config: dict, instance_info_dict: dict, cloudwatch_alarm: dict
) -> dict:
    """CloudWatch アラームが設定されているかどうかを確認

    パラメーター
    -----------
    instance_info_dict : dict
        インスタンス情報一覧
    cloudwatch_alarm : dict
        アラーム設定一覧

    戻り値
    ----------
    dict
        CloudWatch アラームのないインスタンス
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    temp = {}

    for alarm_info in cloudwatch_alarm.values():
        instance_id = alarm_info.get("CacheClusterId")
        if (
            alarm_info["MetricName"] in config["check_metric_names"]
            and instance_id is not None
        ):
            temp.setdefault(instance_id, []).append(alarm_info["MetricName"])

    for instance_id, instance_info in instance_info_dict.items():
        if instance_id in temp:
            instance_info["check_metric_names"] = list(
                set(instance_info["check_metric_names"]) - set(temp[instance_id])
            )

    instance_info_dict = {
        instance_id: instance_info
        for instance_id, instance_info in instance_info_dict.items()
        if instance_info["check_metric_names"]
    }

    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return instance_info_dict


def _has_effective_alarm_setting(alarm_info: dict, config: dict) -> bool:
    """アラーム設定が有効かを確認

    パラメーター
    ----------
    alarm_info : dict
        アラーム設定情報
    config : dict
        設定ファイル

    戻り値
    -------
    bool
        アラーム設定が正しい場合は True、そうでない場合は False
    """
    metric_names = alarm_info["MetricName"]

    return alarm_info["Threshold"] >= config["check_metric_names"][metric_names]


def _verify_cloudwatch_alarms(
    config: dict, instance_info_dict: dict, cloudwatch_alarm: dict
) -> Tuple[dict, dict]:
    """CloudWatch アラームの設定と宛先を確認

    パラメーター
    ----------
    config : dict
        設定ファイル
    instance_info_dict : dict
        インスタンス情報一覧
    cloudwatch_alarm : dict
        CloudWatchアラーム設定一覧

    戻り値
    -------
    Tuple[dict, dict]
        以下を表す辞書のセットを含むTuple:
        1. 間違った宛先のアラーム
        2. 間違った設定のアラーム
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    alarms_with_wrong_destination = {}
    alarms_with_wrong_setting = {}
    for alarm_name, alarm_info in cloudwatch_alarm.items():
        instance_id = alarm_info.get("CacheClusterId")

        if instance_id in instance_info_dict:
            stage = application.get_stage_keywords(config, alarm_info["AlarmName"])
            if config.get("dev_stag_check") or stage == "prod":
                if not application.has_valid_action(config, stage, alarm_info):
                    alarms_with_wrong_destination[alarm_name] = alarm_info

            if not _has_effective_alarm_setting(alarm_info, config):
                alarms_with_wrong_setting[alarm_name] = alarm_info

    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return alarms_with_wrong_destination, alarms_with_wrong_setting


########## アラーム付与関連###############################
def _attach_alarm_for_elasticache(
    account_name: str,
    namespace: str,
    config: dict,
    cloudwatch_client: boto3.client,
    alarms_with_wrong_destination: dict,
    alarms_with_wrong_setting: dict,
    instances_without_alarm: dict,
) -> Tuple[dict, dict]:
    """アラームを取り付ける

    パラメーター
    ----------
    account_name : str
        AWS アカウント名
    namespace : str
        名前空間
    config : dict
        設定ファイル
    alarms_with_wrong_destination : dict
        間違った宛先のアラーム
    alarms_with_wrong_setting : dict
        間違った設定のアラーム
    instances_without_alarm : dict
        アラームが設定されていないインスタンス

    戻り値
    -------
        Tuple[dict, dict]
        以下を表す辞書のセットを含むタプル:
            1. アラーム設定成功
            2. アラーム設定失敗
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    setting_success, setting_fail, alarm_date = {}, {}, {}
    alarms_with_wrong = {**alarms_with_wrong_destination, **alarms_with_wrong_setting}

    if len(alarms_with_wrong) != 0:
        alarm_date = _modify_cloudwatch_alarm_date(config, alarms_with_wrong)

    if len(instances_without_alarm) != 0:
        _make_alarm_data(account_name, config, instances_without_alarm, alarm_date)

    for alarm_name, alarm_info in alarm_date.items():
        try:
            application.put_metric_alarm(cloudwatch_client, alarm_info, namespace)
            setting_success[alarm_name] = alarm_info
        except Exception:
            setting_fail[alarm_name] = traceback.format_exc()
            _logger.error(traceback.format_exc())

    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return setting_success, setting_fail


def _make_alarm_data(
    account_name: str, config: dict, instances_without_alarm: dict, alarm_date: dict
) -> dict:
    """アラームデータを補足

    パラメーター
    ----------
    account_name : str
        AWS アカウント名
    config : dict
        設定ファイル
    instances_without_alarm_dict : dict
        アラームのないインスタンスに関する情報
    alarm_date : dict
        アラームデータ

    戻り値
    -------
    dict
        アラームデータ
    """

    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    metric_names_to_check = config["check_metric_names"]

    for instance_id, _ in instances_without_alarm.items():
        for metric_name in metric_names_to_check:
            if metric_name == "CPUUtilization":
                alarm_name = f"{account_name}-{instance_id}-CPUUtil-Notification"
            elif metric_name == "Evictions":
                alarm_name = f"{account_name}-{instance_id}-Eviction"
            elif metric_name == "CurrConnections":
                alarm_name = f"{account_name}-{instance_id}-CurrConnection-Notification"

            stage = application.get_stage_keywords(config, alarm_name)

            alarm_action = []
            for action in config["check_alarm_actions"][stage]:
                if "Infra-Alert-Notification" in action:
                    alarm_action.append(action)

            alarm_date[alarm_name] = {
                "AlarmName": alarm_name.replace("\xad", ""),
                "AlarmActions": alarm_action,
                "MetricName": metric_name,
                "Dimensions": [
                    {"Name": "CacheClusterId", "Value": instance_id},
                ],
                "Threshold": config["check_metric_names"][metric_name],
                "Period": config["period"],
                "ComparisonOperator": "GreaterThanOrEqualToThreshold",
                "EvaluationPeriods": config["evaluation_periods"],
            }

    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return alarm_date


def _modify_cloudwatch_alarm_date(config: dict, alarm_data: dict) -> dict:
    """間違ったアラーム設定を変更

    パラメーター
    ----------
    config : dict
        設定ファイル
    alarm_info_dict : dict
        間違った設定のアラーム

    戻り値
    -------
    dict
        アラームデータ
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")

    for alarm_name, alarm_info in alarm_data.items():
        # AlarmActionsを補完
        stage = application.get_stage_keywords(config, alarm_name)
        for action in config["check_alarm_actions"][stage]:
            if (
                "Infra-Alert-Notification" in action
                and action not in alarm_info["AlarmActions"]
            ):
                alarm_info["AlarmActions"].append(action)

        for action in alarm_info["AlarmActions"]:
            if stage == "prod" and action in config["check_alarm_actions"]["dev"]:
                alarm_info["AlarmActions"].remove(action)
            if stage == "dev" and action in config["check_alarm_actions"]["prod"]:
                alarm_info["AlarmActions"].remove(action)

        # threshold 修正
        if alarm_info["MetricName"] in config["check_metric_names"]:
            alarm_info["Threshold"] = config["check_metric_names"][
                alarm_info["MetricName"]
            ]
        alarm_data[alarm_name] = alarm_info

    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return alarm_data
