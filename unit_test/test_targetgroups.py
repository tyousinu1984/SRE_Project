import json
import os
import sys

import pytest
from boto3 import Session

sys.path.append("WorkBase/alarm_setting_checker/universal-lambda")  # NOQA: E402
from resources import handler_of_targetgroup
from utils import application as app

current_directory = os.path.dirname(os.path.abspath(__file__))
_CONFIG_FILE_NAME = current_directory + "/core_orien_config.json"
_CONFIG_FILE_NAME = _CONFIG_FILE_NAME.replace("\\", "/")
service = "targetgroup"


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
    elb_client = session.client("elbv2")
    instance_info_dict = handler_of_targetgroup._get_instance_info(config, elb_client)
    print(instance_info_dict)
    print(f"{sys._getframe().f_code.co_name} end")


def test_whether_alarm_has_been_set_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} start")
    config = setUp
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    elb_client = session.client("elbv2")
    cloudwatch_client = session.client("cloudwatch")
    namespace = "AWS/ApplicationELB"
    instance_info_dict = handler_of_targetgroup._get_instance_info(config, elb_client)
    cloudwatch_alarm = app.get_cloudwatch_alarm(cloudwatch_client, namespace)

    target_groups_info_dict = handler_of_targetgroup._whether_alarm_has_been_set(
        config, instance_info_dict, cloudwatch_alarm
    )
    print(target_groups_info_dict)

    print(f"{sys._getframe().f_code.co_name} end")


def test_make_alarm_data_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} start")
    config = setUp
    _ACCOUNT_NAME = "TEST"
    target_groups_info_dict = {
        "zhang-test": {
            "check_metric_names": {"UnHealthyHostCount": 1},
            "lb_name": "app/staging-mens-qzin/8583768c11dc7690",
        }
    }
    alarm_date = {}

    alarm_date = handler_of_targetgroup._make_alarm_data(
        _ACCOUNT_NAME, config, target_groups_info_dict, alarm_date
    )
    print(alarm_date)
    print(f"{sys._getframe().f_code.co_name} end")


def test_modify_cloudwatch_alarm_date_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} start")
    config = setUp
    alarms_data = {
        "test-1": {
            "AlarmActions": [],
            "MetricName": "UnHealthyHostCount",
            "Threshold": 30,
        }
    }
    alarms_data = handler_of_targetgroup._modify_cloudwatch_alarm_date(
        config, alarms_data
    )
    print(alarms_data)
    print(f"{sys._getframe().f_code.co_name} end")


def test_check_alarm_for_ec2_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} Start.")
    config = setUp
    _ACCOUNT_NAME = "orien"

    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    elb_client = session.client("elbv2")

    (
        alarms_with_wrong_destination,
        alarms_with_wrong_setting,
        instances_without_alarm,
        setting_success,
        setting_fail,
    ) = handler_of_targetgroup.check_for_targetgroup(
        _ACCOUNT_NAME, config, cloudwatch_client, elb_client
    )

    print(alarms_with_wrong_destination)
    print(alarms_with_wrong_setting)
    print(instances_without_alarm)
    print(setting_success)
    print(setting_fail)

    print(f"{sys._getframe().f_code.co_name} End.")
