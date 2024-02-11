import sys

sys.path.insert(1, 'wordpress-server-construction-with-kusanagi-docker/wordpress-server-construction-with-kusanagi')  # NOQA: E402
import boto3
from src.utils import aws_handler
from src import create_resource_with_cfn

# NOQA: E402


profile_name = "core_orien"
session = boto3.Session(profile_name=profile_name,
                        region_name="ap-northeast-1")
cfn_client = session.client("cloudformation")
cfn = aws_handler.Cloudformation(cfn_client)

acm_client = session.client("acm")
acm = aws_handler.ACMCertificate(acm_client)

route53_client = session.client("route53")
route53 = aws_handler.Route53(route53_client)

ec2_client = session.client("ec2")
ec2 = aws_handler.EC2(ec2_client)

config = {
    "iam": {
        "role": "arn:aws:iam::320269048510:role/kusanagi-wordpress-server-builder"
    },
    "cloudformation": {
        "template": "https://orien-infra-bucket.s3.ap-northeast-1.amazonaws.com/cloud-formation/template/kusanagi/main.yaml"
    },
    "vpc": {
        "vpc_id": "vpc-51494936",
        "subnets": {
            "A": "subnet-b128eaf9",
            "C": "subnet-6fdce034",
            "D": "subnet-a232e789"
        }
    },
    "ssm": {
        "run_command": {
            "shell_script": "bash /tmp/kusanagi_provision.sh",
            "pre_exec_commands": [
                "aws s3 cp s3://orien-infra-bucket/cloud-formation/template/kusanagi/tuning/ /tmp  --recursive",
                "aws s3 cp s3://orien-infra-bucket/cloud-formation/template/kusanagi/shell-script/kusanagi_provision.sh /tmp",
                "curl http://169.254.169.254/latest/meta-data/instance-type > /tmp/instance-type",
                "aws ec2 describe-instance-types --instance-types `cat /tmp/instance-type` > /tmp/instance-spec"
            ]
        }
    }
}
args_info = {'caller_account_id': '4669636',
             "caller_room_id": "250157426",
             'host_name': 'higuystest.space',
             'instance_type': 't3.nano',
             'availability_zone': 'A',
             'key_name': 'zhang-test-mail-copy',
             'ami': 'ami-002cedb74d7169fa1',
             'ebs_size': '30',
             'termination_protection': 'false',
             'stack_name': 'test1-higuys-space'}

notifier_config = {
    "sns": "arn:aws:sns:ap-northeast-1:840277471863:building-wordpress-server-with-kusanagi",
    "api_token": "bac2678223bf79f13f41c3a4e250b1be",
    "room_id_list": [
        "250157426"
    ]
}


def test_create_cloudFormation_resource_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")

    create_resource_with_cfn._create_cloudFormation_resource(cfn, acm, route53,
                                                             config,
                                                             args_info)
    print(f"{sys._getframe().f_code.co_name} end")


def test_create_resource_with_cfn_Normal001():
    # stack存在
    print(f"{sys._getframe().f_code.co_name} start")
    create_resource_with_cfn.create_resource_with_cfn(cfn, acm, route53, ec2, config, notifier_config,
                                                      args_info)
    print(f"{sys._getframe().f_code.co_name} end")


def test_create_resource_with_cfn_Normal002():
    # stack存在しない
    print(f"{sys._getframe().f_code.co_name} start")
    create_resource_with_cfn.create_resource_with_cfn(cfn, acm, route53, ec2,
                                                      config, notifier_config,
                                                      args_info)
    print(f"{sys._getframe().f_code.co_name} end")


def test_delete_stack_and_send_message_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    message = "構築成功が、EC2起動失敗\n"
    create_resource_with_cfn._delete_stack_and_send_message(
        cfn, args_info, notifier_config, message)
    print(f"{sys._getframe().f_code.co_name} end")
