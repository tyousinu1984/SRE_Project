
import sys
import os
import boto3
#sys.path.insert(1, 'wordpress-server-construction-with-kusanagi-docker/wordpress-server-construction-with-kusanagi')  # NOQA: E402
#sys.path.append("..")  # NOQA: E402
import wordpress_server_construction_with_kusanagi as target
from src.utils import aws_handler

os.environ["CHATWORK_TOKEN"] = "aec8f75de3a107a34a4137fc04cb7b9d"

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


def test_find_config_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    account = "core"
    stage = "dev"
    config = target._find_config(account, stage)
    print(config)
    print(f"{sys._getframe().f_code.co_name} end")


def test_verify_key_pair_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    args_info = {'host_name': 'fanne.co.jp',
                 'stack_name': 'fanne-co-jp', "account": "core-orien"}
    config = {'room_id_list': ['250157426'],
              'api_token': 'aec8f75de3a107a34a4137fc04cb7b9d'}
    args_info = target._verify_key_pair(ec2, args_info, config)
    print(args_info)
    print(f"{sys._getframe().f_code.co_name} end")


def test_main_Normal001():
    # stack存在しない
    print(f"{sys._getframe().f_code.co_name} start")
    args_info = {"host_name": "higuys.space",
                 "stack_name": "higuys-space",
                 "account": "orien",
                 "stage": "dev",
                 "instance_type": "t3.small",
                 "availability_zone": "A",
                 "key_name": "zhang-test-mail-copy",
                 "ami": "ami-002cedb74d7169fa1",
                 "ebs_size": "30",
                 "caller_user_id": "5757341",
                 "caller_room_id": "250157426"}

    target.main(args_info)

    print(f"{sys._getframe().f_code.co_name} end")


def test_main_Normal002():
    # stack存在
    print(f"{sys._getframe().f_code.co_name} start")
    args_info = {"host_name": "help1.higuys.space",
                 "account": "orien",
                 "stage": "dev",
                 "instance_type": "t3.nano",
                 "availability_zone": "A",
                 "key_name": None,
                 "ami": "ami-002cedb74d7169fa1",
                 "ebs_size": "30",
                 "caller_user_id": "5757341",
                 "caller_room_id": "250157426"}

    target.main(args_info)

    print(f"{sys._getframe().f_code.co_name} end")


def test_main_Normal003():

    print(f"{sys._getframe().f_code.co_name} start")
    args_info = {'host_name': 'zhangtest.vootec.net', 'key_name': 'zhang-test-mail-copy',
                 'account': 'orien', 'stage': 'dev', 'instance_type': 't3.medium', 'availability_zone': 'A',
                 'ami': 'ami-002cedb74d7169fa1', 'ebs_size': '50', 'termination_protection': 'true',
                 'caller_user_id': '5757341', 'caller_room_id': '250157426', 'stack_name': 'zhangtest-vootec-net'}

    target.main(args_info)

    print(f"{sys._getframe().f_code.co_name} end")
