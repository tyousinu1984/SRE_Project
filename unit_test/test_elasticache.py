import json
import os
import sys

import pytest
from boto3 import Session

sys.path.append("WorkBase/alarm_setting_checker/universal-lambda")  # NOQA: E402
from resources import handler_of_elasticache

current_directory = os.path.dirname(os.path.abspath(__file__))
_CONFIG_FILE_NAME = current_directory + "/core_orien_config.json"
_CONFIG_FILE_NAME = _CONFIG_FILE_NAME.replace("\\", "/")

service = "elasticache"


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
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    elasticache_client = session.client("elasticache")
    config = setUp

    instance_info_dict = handler_of_elasticache._get_instance_info(
        config, elasticache_client
    )
    print(instance_info_dict)
    print(f"{sys._getframe().f_code.co_name} end")


def test_has_effective_alarm_setting_Normal001(setUp):
    config = setUp
    alarm_info = {"MetricName": "CurrConnections", "Threshold": 200}
    result = handler_of_elasticache._has_effective_alarm_setting(alarm_info, config)
    print("result", result)
    assert result is True


def test_has_effective_alarm_setting_Normal002(setUp):
    alarm_info = {"MetricName": "Evictions", "Threshold": 30}
    config = setUp
    result = handler_of_elasticache._has_effective_alarm_setting(alarm_info, config)
    print(result)
    assert result is False


def test_verify_cloudwatch_alarms_Normal001(setUp):
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    elasticache_client = session.client("elasticache")
    cloudwatch_client = session.client("cloudwatch")

    config = setUp
    instance_info_dict = handler_of_elasticache._get_instance_info(
        elasticache_client, config
    )
    cloudwatch_alarm = handler_of_elasticache._get_cloudwatch_alarm(cloudwatch_client)

    (
        alarms_with_wrong_destination,
        alarms_with_wrong_setting,
    ) = handler_of_elasticache._verify_cloudwatch_alarms(
        config, instance_info_dict, cloudwatch_alarm
    )
    print(alarms_with_wrong_destination)
    print(alarms_with_wrong_setting)


def test_whether_alarm_has_been_set_Normal001(setUp):
    config = setUp
    instance_info_dict = {
        "dev-ex-deli-fargate": {
            "check_metric_names": {
                "CurrConnections": 200,
                "Evictions": 40,
                "CPUUtilization": 40,
            }
        },
        "dev-ranking-delijp": {
            "check_metric_names": {
                "CurrConnections": 200,
                "Evictions": 40,
                "CPUUtilization": 40,
            }
        },
        "zhang-test-1-001": {
            "check_metric_names": {
                "CurrConnections": 200,
                "Evictions": 40,
                "CPUUtilization": 40,
            }
        },
        "zhang-test-1-002": {
            "check_metric_names": {
                "CurrConnections": 200,
                "Evictions": 40,
                "CPUUtilization": 40,
            }
        },
        "zhang-test-1-003": {
            "check_metric_names": {
                "CurrConnections": 200,
                "Evictions": 40,
                "CPUUtilization": 40,
            }
        },
    }
    cloudwatch_alarm = {
        "cor-ElastiCache-dev-ranking-delijp-CPUUtilization": {
            "AlarmName": "cor-ElastiCache-dev-ranking-delijp-CPUUtilization",
            "MetricName": "CPUUtilization",
            "Dimensions": [{"Name": "CacheClusterId", "Value": "dev-ranking-delijp"}],
            "CacheClusterId": "dev-ranking-delijp",
        },
        "cor-ElastiCache-dev-ranking-delijp-CurrConnections": {
            "AlarmName": "cor-ElastiCache-dev-ranking-delijp-CurrConnections",
            "MetricName": "CurrConnections",
            "Dimensions": [{"Name": "CacheClusterId", "Value": "dev-ranking-delijp"}],
            "CacheClusterId": "dev-ranking-delijp",
        },
        "cor-ElastiCache-dev-ranking-delijp-Evictions": {
            "AlarmName": "cor-ElastiCache-dev-ranking-delijp-Evictions",
            "MetricName": "Evictions",
            "Dimensions": [{"Name": "CacheClusterId", "Value": "dev-ranking-delijp"}],
            "CacheClusterId": "dev-ranking-delijp",
        },
        "cor-ElasticCache-dev-ex-deli-fargate-CurrConnections": {
            "AlarmName": "cor-ElasticCache-dev-ex-deli-fargate-CurrConnections",
            "MetricName": "CurrConnections",
            "Dimensions": [{"Name": "CacheClusterId", "Value": "dev-ex-deli-fargate"}],
            "CacheClusterId": "dev-ex-deli-fargate",
        },
        "cor-Elasti\xadCache-Evictions-dev-ex-deli-fargate": {
            "AlarmName": "cor-Elasti\xadCache-Evictions-dev-ex-deli-fargate",
            "MetricName": "Evictions",
            "Namespace": "AWS/ElastiCache",
            "Dimensions": [{"Name": "CacheClusterId", "Value": "dev-ex-deli-fargate"}],
            "CacheClusterId": "dev-ex-deli-fargate",
        },
        "core-Elasti\xadCache-CPUUtilization": {
            "AlarmName": "core-Elasti\xadCache-CPUUtilization",
            "MetricName": "CPUUtilization",
            "Dimensions": [{"Name": "CacheClusterId", "Value": "dev-ex-deli-fargate"}],
            "CacheClusterId": "dev-ex-deli-fargate",
        },
    }
    instances_without_alarm = handler_of_elasticache._whether_alarm_has_been_set(
        config, instance_info_dict, cloudwatch_alarm
    )
    print(instances_without_alarm)


def test_check_for_elasticache_Normal001(setUp):
    print(f"{sys._getframe().f_code.co_name} Start.")
    config = setUp
    _ACCOUNT_NAME = "orien"

    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    elasticache_client = session.client("elasticache")

    (
        alarms_with_wrong_destination,
        alarms_with_wrong_setting,
        instances_without_alarm,
        setting_success,
        setting_fail,
    ) = handler_of_elasticache.check_for_elasticache(
        _ACCOUNT_NAME, config, cloudwatch_client, elasticache_client
    )

    print(alarms_with_wrong_destination)
    print(alarms_with_wrong_setting)
    print(instances_without_alarm)
    print(setting_success)
    print(setting_fail)

    print(f"{sys._getframe().f_code.co_name} End.")
