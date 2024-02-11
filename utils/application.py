import sys
import traceback

from utils import log_handler

_logger = log_handler.LoggerHander()


def put_metric_alarm(cloudwatch_client, alarm_info, namespace):
    """アラーム設定を更新・作成

    Parameters
    ----------
    cloudwatch_client :
        cloudwatchのクライアント
    alarm_info : dict
        アラームデータ

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


def get_cloudwatch_alarm(cloudwatch_client, namespace) -> dict:
    """cloudwatch_alarmを取得

    Parameters
    -----------
    cloudwatch_client:
        cloudwatchのclientオブジェクト

    Returns
    ----------
    cloudwatch_alarm : dict{str,dict}
        アラーム設定一覧
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


def get_stage_keywords(config, name):
    """インスタンスのステージを判断

    Parameters
    ----------
    config : dict
        設定ファイル
    alarm_name : str
        アラート名

    Returns
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



def has_valid_action(config, stage, alarm):
    """指定したアラームが有効なアクションを指定しているかを確認する。

    Parameters
    -------------------
    config : dict
        elasticacheの設定変数
    stage : str
        アラームのステージ
    alarm : dict
        検証すべきアラーム
    Returns
    ------
    bool
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
