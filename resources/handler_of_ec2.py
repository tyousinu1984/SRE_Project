import copy
import os
import sys
import traceback

from utils import application, log_handler

# ロガー初期化
_LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
_logger = log_handler.LoggerHander(log_level=_LOG_LEVEL)

_NAMESPACE = "AWS/EC2"


def check_for_ec2(account_name, config, cloudwatch_client, ec2_client):
    """EC2のアラーム設定のチェックと自動付与

    Parameters
    ----------
    account_name : str
        アカウント名
    config : dict
        設定ファイル
    service : str
        AWSのサービス名
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    namespace = _NAMESPACE
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
def _check_alarm_for_ec2(namespace, config, cloudwatch_client, ec2_client):
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


def _get_instance_info(config, ec2_client) -> dict:
    """ec2インスタンスの情報を取得

    Parameters
    ----------
    config : dict
        設定ファイル
    ec2_client :
        ec2のクライアント

    Returns
    -------
    dict
        インスタンスの情報
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


def _whether_alarm_has_been_set(config, instance_info_dict, cloudwatch_alarm):
    """
    cloudwatchアラーム設定しているかどうかをチェック

    Parameters
    -----------

    instance_info_dict : dict
        インスタンスの一覧
    cloudwatch_alarm : dict
        アラーム設定一覧

    Returns
    ----------
    instances_without_alarm : dict[str,list]
        アラート設定していないec2
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


def _has_effective_alarm_setting_for_StatusCheckFailed(alarm_info, config):
    """アラートの設定をチェック

    Parameters
    ----------
    alarm_info : dict
        アラート設定情報
    config : dict
        設定ファイル

    Returns
    -------
    bool
        アラートの設定が正しいかどうか
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


def _verify_cloudwatch_alarms(config, instance_info_dict, ec2_alarm_info):
    """cloudwatchアラーム設定と通知先をチェック

    Parameters
    -----------

    config : dict
        elasticacheの設定変数
    instance_info_dict : dict
        elasticacheのクラスター名
    cloudwatch_alarm : dict
        elasticacheのアラーム設定一覧

    Returns
    ----------
    alarms_with_wrong_destination : list[str]
        通知先の間違っているアラート
    alarms_with_wrong_setting : list[str]
        設定の間違っているアラート
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    alarms_with_wrong_destination_dict = {}
    alarms_with_wrong_setting_dict = {}
    for alarm_name, alarm_info in ec2_alarm_info.items():
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
    account_name,
    namespace,
    config,
    cloudwatch_client,
    alarms_with_wrong_destination,
    alarms_with_wrong_setting,
    instances_without_alarm,
):
    """アラーム付与

    Parameters
    ----------
    account_name : str
        アカウント名
    config : dict
        設定ファイル
    alarms_with_wrong_destination : dict
        SNSの設定が間違っているアラーム
    alarms_with_wrong_setting : dict
        設定が間違っているアラーム
    instances_without_alarm : dict
        アラーム設定しているインスタンス

    Returns
    -------
    setting_success : dict
        アラーム設定成功したインスタンス
    setting_fail : dict
        アラーム設定失敗したインスタンス
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


def _make_alarm_data(account_name, config, instances_without_alarm_dict, alarm_date):
    """alarmデータの補足

    Parameters
    ----------
    account_name : str
        アカウント名
    config : dict
        設定ファイル
    instances_without_alarm_dict : dict
        アラーム設定していないインスタンス情報
    alarm_date : dict
        アラームデータ

    Returns
    -------
    dict
        アラームデータ
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")

    metric_names_to_check = config["check_metric_names"]

    for instance_id, instance_info in instances_without_alarm_dict.items():
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


def _modify_cloudwatch_alarm_date(config, alarm_info_dict):
    """設定の間違っているアラーム情報を修正

    Parameters
    ----------
    config : dict
        設定ファイル
    alarm_info_dict : dict
        設定の間違っているアラーム情報

    Returns
    -------
    dict
        アラームデータ
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")

    for alarm_name, alarm_info in alarm_info_dict.items():
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

        alarm_info_dict[alarm_name] = alarm_info

    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return alarm_info_dict
