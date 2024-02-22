import copy
import os
import sys
import traceback
from typing import Tuple

import boto3
from utils import application, log_handler

# ロガー初期化
_LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
_logger = log_handler.LoggerHander(log_level=_LOG_LEVEL)


def check_for_ec2(
    account_name: str,
    namespace: str,
    config: dict,
    cloudwatch_client: boto3.client,
    ec2_client: boto3.client,
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
    ec2_client : boto3.client
        EC2の Boto3 クライアント

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
    ) = _check_alarm_for_ec2(namespace, config, cloudwatch_client, ec2_client)

    if not (
        len(alarms_with_wrong_destination) == 0
        and len(alarms_with_wrong_setting) == 0
        and len(instances_without_alarm) == 0
    ):
        setting_success, setting_fail = _attach_alarm_for_ec2(
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
def _check_alarm_for_ec2(
    namespace: str,
    config: dict,
    cloudwatch_client: boto3.client,
    ec2_client: boto3.client,
) -> Tuple[dict, dict, dict]:
    """EC2アラーム設定を確認

    パラメーター
    ----------
    namespace : str
        名前空間
    config : dict
        設定ファイル
    cloudwatch_client : boto3.client
        CloudWatch 用の Boto3 クライアント
    ec2_client : boto3.client
        EC2 用の Boto3 クライアント

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
        instance_info_dict = _get_instance_info(config, ec2_client)
        cloudwatch_alarm = application.get_cloudwatch_alarm(
            cloudwatch_client, namespace
        )

        (
            alarms_with_wrong_destination_dict,
            alarms_with_wrong_setting_dict,
        ) = _verify_cloudwatch_alarms(config, instance_info_dict, cloudwatch_alarm)

        instances_without_alarm_dict = _whether_alarm_has_been_set(
            config, instance_info_dict, cloudwatch_alarm
        )
        return (
            alarms_with_wrong_destination_dict,
            alarms_with_wrong_setting_dict,
            instances_without_alarm_dict,
        )

    except Exception as e:
        _logger.error(f"Error: {sys._getframe().f_code.co_name} ")
        _logger.error(traceback.format_exc())
        raise e
    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def _get_instance_info(config: dict, ec2_client: boto3.client) -> dict:
    """EC2 インスタンスに関する情報を取得

    パラメーター
    ----------
    config : dict
        設定ファイル
    ec2_client : boto3.client
        EC2 用の Boto3 クライアント

    戻り値
    -------
    dict
        EC2インスタンスに関する情報
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    instance_info_dict = {}
    try:
        paginator = ec2_client.get_paginator("describe_instances")
        page_iterator = paginator.paginate(
            Filters=[
                {
                    "Name": "instance-state-name",
                    "Values": [
                        "running",
                    ],
                }
            ],
        )
        # instanceIDを取得
        for page in page_iterator:
            for reservation in page["Reservations"]:
                for instance in reservation["Instances"]:
                    # Tagsを見て、CheckAlarmSettingがNOならば除外(存在しない、またはYESなら追加
                    check_flag = True
                    instance_name = instance["InstanceId"]
                    Tags = instance["Tags"]
                    for tag in Tags:
                        if tag["Key"] == "CheckAlarmSetting":
                            if tag["Value"].upper() == "NO":
                                check_flag = False
                        if tag["Key"] == "Name":
                            instance_name = tag["Value"]
                    if check_flag:
                        instance_info_dict[instance["InstanceId"]] = {
                            "check_metric_names": config["check_metric_names"],
                            "type": instance["InstanceType"],
                            "instance_name": instance_name,
                        }

        return instance_info_dict

    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def _whether_alarm_has_been_set(
    config: dict, instance_info_dict: dict, cloudwatch_alarm: dict
) -> dict:
    """CloudWatch アラームが設定されているかどうかを確認

    パラメーター
    -----------
    instance_info_dict : dict
        インスタンス情報一覧
    Cloudwatch_alarm : dict
        アラーム設定一覧

    戻り値
    ----------
    dict
        CloudWatch アラームのないインスタンス
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    temp = {}

    for alarm_info in cloudwatch_alarm.values():
        instance_id = alarm_info.get("InstanceId")

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


def _has_effective_alarm_setting_for_StatusCheckFailed(alarm_info: dict, config: dict):
    """StatusCheckFailedに対してアラーム設定が有効かを確認

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
    condtion1 = (
        "arn:aws:automate:ap-northeast-1:ec2:recover" in alarm_info["AlarmActions"]
    )
    condtion2 = alarm_info["Threshold"] == 1.0 or alarm_info["Threshold"] == 0.99
    condtion3 = alarm_info["Period"] == 60
    condtion4 = alarm_info["EvaluationPeriods"] == config.get("evaluation_periods")
    condtion5 = (
        alarm_info["ComparisonOperator"] == "GreaterThanThreshold"
        or alarm_info["ComparisonOperator"] == "GreaterThanOrEqualToThreshold"
    )

    return condtion1 and condtion2 and condtion3 and condtion4 and condtion5


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
    alarms_with_wrong_destination_dict = {}
    alarms_with_wrong_setting_dict = {}
    for alarm_name, alarm_info in cloudwatch_alarm.items():
        instance_id = alarm_info.get("InstanceId")

        if instance_id in instance_info_dict:
            stage = application.get_stage_keywords(config, alarm_name)

            if not application.has_valid_action(config, stage, alarm_info):
                # もし必要な通知先に通知していない場合
                alarms_with_wrong_destination_dict[alarm_name] = alarm_info

            if alarm_info["MetricName"] == "StatusCheckFailed_System":
                # もしシステムステータスチェック失敗時のアラームだった場合

                EXCLUDE_INSTANCE_TYPE = config["instance_types_to_exclude"]
                instance_type = instance_info_dict[instance_id]["type"]

                if not _has_effective_alarm_setting_for_StatusCheckFailed(
                    alarm_info, config
                ) and not (instance_type in EXCLUDE_INSTANCE_TYPE):
                    alarms_with_wrong_setting_dict[alarm_name] = alarm_info

    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return alarms_with_wrong_destination_dict, alarms_with_wrong_setting_dict


########## アラーム付与関連###############################
def _attach_alarm_for_ec2(
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

    for instance_id, instance_info in instances_without_alarm.items():
        instance_name = instance_info["instance_name"]
        alarm_name = f"{account_name}-{instance_name}"

        stage = application.get_stage_keywords(config, alarm_name)

        alarm_action = []
        for action in config["check_alarm_actions"][stage]:
            if "Infra-Alert-Notification" in action:
                alarm_action.append(action)

        for metric_name in metric_names_to_check:
            if metric_name == "StatusCheckFailed_System":
                alarm_name = f"{alarm_name}-system-status-check-failed"
                _alarm_action = copy.copy(alarm_action)
                _alarm_action.append("arn:aws:automate:ap-northeast-1:ec2:recover")

            elif metric_name == "StatusCheckFailed_Instance":
                alarm_name = f"{alarm_name}-instance-status-check-failed"
                _alarm_action = copy.copy(alarm_action)
            alarm_name = f"{account_name}-{instance_name}-{metric_name}"
            alarm_date[alarm_name] = {
                "AlarmName": alarm_name,
                "AlarmActions": _alarm_action,
                "MetricName": metric_name,
                "Dimensions": [
                    {"Name": "InstanceId", "Value": instance_id},
                ],
                "Period": config["period"],
                "Threshold": config["check_metric_names"][metric_name],
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

        # evaluation-periods修正
        if alarm_info["EvaluationPeriods"] != config["evaluation_periods"]:
            alarm_info["EvaluationPeriods"] = config["evaluation_periods"]

        if (
            alarm_info["MetricName"] == "StatusCheckFailed_System"
            and "arn:aws:automate:ap-northeast-1:ec2:recover"
            not in alarm_info["AlarmActions"]
        ):
            alarm_info["AlarmActions"].append(
                "arn:aws:automate:ap-northeast-1:ec2:recover"
            )

    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return alarm_data
