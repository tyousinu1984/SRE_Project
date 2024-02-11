import json
import os
import sys

import pytest
from boto3 import Session

sys.path.append("WorkBase/alarm_setting_checker/universal-lambda")  # NOQA: E402
from resources import handler_of_rds
from utils import application as app

current_directory = os.path.dirname(os.path.abspath(__file__))
_CONFIG_FILE_NAME = current_directory + "/core_orien_config.json"
_CONFIG_FILE_NAME = _CONFIG_FILE_NAME.replace("\\", "/")
service = "rds"


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


def test_get_instance_list_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} Start.")
    config = setUp
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")

    rds_client = session.client("rds")

    instance_info_dict = handler_of_rds._get_instance_info(config, rds_client)
    print(instance_info_dict)

    print(f"{sys._getframe().f_code.co_name} End.")


def test_has_effective_alarm_setting_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} start")
    config = setUp
    alarm_info = {
        "MetricName": "CPUUtilization",
        "Threshold": 81,
        "EvaluationPeriods": 3,
        "ComparisonOperator": "GreaterThanThreshold",
    }
    result = handler_of_rds._has_effective_alarm_setting(alarm_info, config)
    print(result)
    assert result is True
    print(f"{sys._getframe().f_code.co_name} end")


def test_has_effective_alarm_setting_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} start")
    config = setUp
    alarm_info = {
        "MetricName": "CPUUtilization",
        "Threshold": 70,
        "EvaluationPeriods": 1,
        "ComparisonOperator": "GreaterThanThreshold",
    }
    result = handler_of_rds._has_effective_alarm_setting(alarm_info, config)
    print(result)
    assert result is False
    print(f"{sys._getframe().f_code.co_name} end")


def test_check_alarm_for_rds_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} start")
    _ACCOUNT_NAME = "orien"

    config = setUp
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    rds_client = session.client("rds")

    (
        alarms_with_wrong_destination,
        alarms_with_wrong_setting,
        instances_without_alarm,
        setting_success,
        setting_fail,
    ) = handler_of_rds.check_for_rds(
        _ACCOUNT_NAME, config, cloudwatch_client, rds_client
    )
    print(alarms_with_wrong_destination)
    print(alarms_with_wrong_setting)
    print(instances_without_alarm)
    print(setting_success)
    print(setting_fail)
    print(f"{sys._getframe().f_code.co_name} end")
