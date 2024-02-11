import json
import os
import sys

sys.path.append("WorkBase/alarm_setting_checker/universal-lambda")  # NOQA: E402
import pytest
from boto3 import Session
from resources import handler_of_lambda
from utils import application

current_directory = os.path.dirname(os.path.abspath(__file__))
_CONFIG_FILE_NAME = current_directory + "/core_orien_config.json"
_CONFIG_FILE_NAME = _CONFIG_FILE_NAME.replace("\\", "/")
service = "lambda"


@pytest.fixture()
def setUp():
    with open(_CONFIG_FILE_NAME, "r", encoding="utf-8") as file:
        config = json.load(file)

    config = _dict_merge(config["common"], config[service])
    return config


def _dict_merge(d1, d2):
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


def test_get_instance_info_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} start")
    config = setUp
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")

    lambda_client = session.client("lambda")

    instance_info_dict = handler_of_lambda._get_instance_info(config, lambda_client)
    print(instance_info_dict)
    print(f"{sys._getframe().f_code.co_name} end")


def test_has_effective_alarm_setting_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} start")
    config = setUp
    alarm_info = {"MetricName": "Errors", "Threshold": 1}
    result = handler_of_lambda._has_effective_alarm_setting(alarm_info, config)
    print(result)
    assert result is True
    print(f"{sys._getframe().f_code.co_name} end")


def test_has_effective_alarm_setting_Normal002(setUp):
    print(f"{sys._getframe().f_code.co_name} start")
    config = setUp
    alarm_info = {"MetricName": "Errors", "Threshold": 30}
    result = handler_of_lambda._has_effective_alarm_setting(alarm_info, config)
    print(result)
    assert result is False
    print(f"{sys._getframe().f_code.co_name} end")


def test_verify_cloudwatch_alarms_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} start")
    config = setUp
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")

    lambda_client = session.client("lambda")
    cloudwatch_client = session.client("cloudwatch")

    instance_info_dict = handler_of_lambda._get_instance_info(config, lambda_client)
    cloudwatch_alarm = application.get_cloudwatch_alarm(cloudwatch_client)

    (
        alarms_with_wrong_destination,
        alarms_with_wrong_setting,
    ) = handler_of_lambda._verify_cloudwatch_alarms(
        config, instance_info_dict, cloudwatch_alarm
    )
    print(alarms_with_wrong_destination)
    print(alarms_with_wrong_setting)


def test_whether_alarm_has_been_set_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} start")
    config = setUp
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")

    lambda_client = session.client("lambda")
    cloudwatch_client = session.client("cloudwatch")
    instance_info_dict = handler_of_lambda._get_instance_info(config, lambda_client)
    cloudwatch_alarm = application.get_cloudwatch_alarm(cloudwatch_client)
    instances_without_alarm = handler_of_lambda._whether_alarm_has_been_set(
        instance_info_dict, cloudwatch_alarm
    )
    print(instances_without_alarm)

    print(f"{sys._getframe().f_code.co_name} end")


def test_check_alarm_for_lambda_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} start")
    config = setUp
    (
        alarms_with_wrong_destination,
        alarms_with_wrong_setting,
        instances_without_alarm,
    ) = handler_of_lambda.check_alarm_for_lambda(config)
    print(alarms_with_wrong_destination)
    print(alarms_with_wrong_setting)
    print(instances_without_alarm)
    print(f"{sys._getframe().f_code.co_name} end")


def test_check_alarm_for_lambda_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} start")

    config = setUp
    _ACCOUNT_NAME = "orien"
    profile_name = "core_orien"

    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    ec2_client = session.client("lambda")

    (
        alarms_with_wrong_destination,
        alarms_with_wrong_setting,
        instances_without_alarm,
        setting_success,
        setting_fail,
    ) = handler_of_lambda.check_for_lambda(
        _ACCOUNT_NAME, config, cloudwatch_client, ec2_client
    )

    print(alarms_with_wrong_destination)
    print(alarms_with_wrong_setting)
    print(instances_without_alarm)
    print(setting_success)
    print(setting_fail)

    print(f"{sys._getframe().f_code.co_name} end")
