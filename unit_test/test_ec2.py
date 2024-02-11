import json
import os
import sys

import pytest
from boto3 import Session

sys.path.append("WorkBase/alarm_setting_checker/universal-lambda")  # NOQA: E402
from resources import handler_of_ec2
from utils import application as app

current_directory = os.path.dirname(os.path.abspath(__file__))
_CONFIG_FILE_NAME = current_directory + "/core_orien_config.json"
_CONFIG_FILE_NAME = _CONFIG_FILE_NAME.replace("\\", "/")
service = "ec2"


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
    print(f"{sys._getframe().f_code.co_name} Start.")
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    ec2_client = session.client("ec2")

    config = setUp

    instance_info_dict = handler_of_ec2._get_instance_info(config, ec2_client)
    print(instance_info_dict)
    print(f"{sys._getframe().f_code.co_name} End.")


def test_verify_cloudwatch_alarms_info_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} Start.")
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    ec2_client = session.client("ec2")

    config = setUp

    instance_info_dict = handler_of_ec2._get_instance_info(config, ec2_client)
    cloudwatch_alarm = app.get_cloudwatch_alarm(cloudwatch_client, "AWS/EC2")
    (
        alarms_with_wrong_destination_dict,
        alarms_with_wrong_setting_dict,
    ) = handler_of_ec2._verify_cloudwatch_alarms(
        config, instance_info_dict, cloudwatch_alarm
    )
    print(alarms_with_wrong_destination_dict)
    print(alarms_with_wrong_setting_dict)
    print(f"{sys._getframe().f_code.co_name} End.")


def test_verify_cloudwatch_alarms_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} Start.")
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    ec2_client = session.client("ec2")

    config = setUp

    instance_info_dict = handler_of_ec2._get_instance_info(config, ec2_client)
    cloudwatch_alarm = app.get_cloudwatch_alarm(cloudwatch_client, "AWS/EC2")

    instances_without_alarm_dict = handler_of_ec2._whether_alarm_has_been_set(
        config, instance_info_dict, cloudwatch_alarm
    )

    print(instances_without_alarm_dict)
    print(f"{sys._getframe().f_code.co_name} End.")


def test_check_alarm_for_ec2_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} Start.")
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    ec2_client = session.client("ec2")
    namespace = "AWS/EC2"

    config = setUp

    (
        alarms_with_wrong_destination_dict,
        alarms_with_wrong_setting_dict,
        instances_without_alarm_dict,
    ) = handler_of_ec2.check_alarm_for_ec2(
        namespace, config, cloudwatch_client, ec2_client
    )

    print(alarms_with_wrong_destination_dict)
    print(alarms_with_wrong_setting_dict)
    print(instances_without_alarm_dict)
    print(f"{sys._getframe().f_code.co_name} End.")


def test_make_alarm_data_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} Start.")
    _ACCOUNT_NAME = "test"
    alarm_date = {}
    instances_without_alarm_dict = {
        "i-04d31a27b88c8100f": {
            "check_metric_names": {
                "StatusCheckFailed_System": 0.99,
                "StatusCheckFailed_Instance": 0.99,
            },
            "type": "t2.micro",
            "instance_name": "xyz",
        }
    }
    config = setUp
    alarm_date = handler_of_ec2._make_alarm_data(
        _ACCOUNT_NAME, config, instances_without_alarm_dict, alarm_date
    )
    print(alarm_date)
    print(f"{sys._getframe().f_code.co_name} End.")


def test_check_alarm_for_ec2_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} Start.")
    config = setUp
    _ACCOUNT_NAME = "orien"

    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    ec2_client = session.client("ec2")

    (
        alarms_with_wrong_destination,
        alarms_with_wrong_setting,
        instances_without_alarm,
        setting_success,
        setting_fail,
    ) = handler_of_ec2.check_for_ec2(
        _ACCOUNT_NAME, config, cloudwatch_client, ec2_client
    )

    print(alarms_with_wrong_destination)
    print(alarms_with_wrong_setting)
    print(instances_without_alarm)
    print(setting_success)
    print(setting_fail)

    print(f"{sys._getframe().f_code.co_name} End.")
