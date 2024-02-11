import sys

import pytest
from boto3 import Session

sys.path.append("WorkBase/alarm_setting_checker/universal-lambda")  # NOQA: E402
from utils import application


@pytest.fixture()
def setUp():
    pass


def test_get_cloudwatch_alarm_Normal001():
    profile_name = "default"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    namespace = "AWS/EC2"
    res = application.get_cloudwatch_alarm(cloudwatch_client, namespace)
    print(res)


def test_get_cloudwatch_alarm_Normal002():
    profile_name = "default"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    namespace = "AWS/ApplicationELB"
    res = application.get_cloudwatch_alarm(cloudwatch_client, namespace)
    print(res)


def test_get_cloudwatch_alarm_Normal003():
    profile_name = "default"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    namespace = "AWS/ElastiCache"
    res = application.get_cloudwatch_alarm(cloudwatch_client, namespace)
    print(res)


def test_get_cloudwatch_alarm_Normal004():
    profile_name = "default"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    namespace = "AWS/RDS"
    res = application.get_cloudwatch_alarm(cloudwatch_client, namespace)
    print(res)


def test_get_cloudwatch_alarm_Normal005():
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    namespace = "AWS/ApplicationELB"
    res = application.get_cloudwatch_alarm(cloudwatch_client, namespace)
    print(res)


def test_put_metric_alarm_Normal001():
    profile_name = "core_orien"
    session = Session(profile_name=profile_name, region_name="ap-northeast-1")
    cloudwatch_client = session.client("cloudwatch")
    namespace = "AWS/EC2"

    alarm_info = {
        "AlarmName": "test-xyz-StatusCheckFailed_System",
        "AlarmActions": [
            "arn:aws:sns:ap-northeast-1:320269048510:Infra-Alert-Notification",
            "arn:aws:automate:ap-northeast-1:ec2:recover",
        ],
        "MetricName": "StatusCheckFailed_System",
        "Dimensions": [{"Name": "InstanceId", "Value": "i-04d31a27b88c8100f"}],
        "Period": 60,
        "Threshold": 0.99,
        "ComparisonOperator": "GreaterThanOrEqualToThreshold",
        "EvaluationPeriods": 3,
    }

    application.put_metric_alarm(cloudwatch_client, alarm_info, namespace)
