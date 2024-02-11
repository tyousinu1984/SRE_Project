import sys

sys.path.insert(1, 'wordpress-server-construction-with-kusanagi-docker/wordpress-server-construction-with-kusanagi')  # NOQA: E402
import boto3
from src.utils import aws_handler
from src import ssm_run_command


profile_name = "fanne"
session = boto3.Session(profile_name=profile_name,
                        region_name="ap-northeast-1")


config = {'iam_role': 'arn:aws:iam::872863745688:role/ecsTaskKusanagiWordpressServerBuilderRole', 'cfn_template': 'https://fanne-infra-bucket.s3.ap-northeast-1.amazonaws.com/cloud-formation/template/kusanagi/main.yaml', 'vpc': {'vpc_id': 'vpc-0336b5789d2324d38', 'subnets': {'A': 'subnet-0e086f6aa48dab487', 'C': 'subnet-0a0a6a2c8cec4bdf5', 'D': 'subnet-01475156d94fe94a5'}}, 'ssm_run_command': {'shell_script': 'kusanagi_provision.sh',
                                                                                                                                                                                                                                                                                                                                                                                                            'pre_exec_commands': ['aws s3 cp s3://fanne-infra-bucket/cloud-formation/template/kusanagi/tuning/ /tmp  --recursive', 'aws s3 cp s3://fanne-infra-bucket/cloud-formation/template/kusanagi/shell-script/kusanagi_provision.sh /tmp', 'curl http://169.254.169.254/latest/meta-data/instance-type > /tmp/instance-type', 'aws ec2 describe-instance-types --instance-types `cat /tmp/instance-type` > /tmp/instance-spec']}}
args_info = {'host_name': 'fanne.co.jp', 'key_name': 'fannecojp', 'account': 'fanne', 'stage': 'prod', 'instance_type': 't3.medium', 'availability_zone': 'A', 'ami': 'ami-002cedb74d7169fa1', 'ebs_size': '50', 'termination_protection': 'true', 'caller_user_id': '530605', 'caller_room_id': '250157426',
             'stack_name': 'fanne-co-jp', 'direct_chat_room_id': '36504184', 'acm_certificate_arn': '', 'host_zone_id': 'Z0602969200WYVYQS5U3S', 'domain_name': 'fanne.co.jp', 'subnet_id': 'subnet-0e086f6aa48dab487', 'subnet_id2': 'subnet-0a0a6a2c8cec4bdf5', 'vpc_id': 'vpc-0336b5789d2324d38', 'instance_id': 'i-06d7385577e512dc7'}

notifier_config = {
    "api_token": "bac2678223bf79f13f41c3a4e250b1be",
    "room_id_list": [
        "250157426"
    ]
}


def test_setup_kusangi_server_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    host_name = 'fanne.co.jp'
    instance_id = "i-06d7385577e512dc7"
    ssm_client = session.client("ssm")
    ssm = aws_handler.SSM(ssm_client, instance_id)
    result, login_info = ssm_run_command.setup_kusangi_server(ssm, config,
                                                              host_name)
    print(result)
    print(login_info)
    print(f"{sys._getframe().f_code.co_name} end")
