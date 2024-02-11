import sys

sys.path.insert(1, 'wordpress-server-construction-with-kusanagi-docker/wordpress-server-construction-with-kusanagi')  # NOQA: E402
import boto3
from src.utils import aws_handler

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
# ##################Cloudformation#####################


def test_find_cfn_stack_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    name = "bs-response-check-ecr"
    resp, stack_status = cfn._find_cfn_stack(name)
    print(stack_status)
    assert resp is False
    print(f"{sys._getframe().f_code.co_name} end")


def test_find_cfn_stack_Normal002():
    print(f"{sys._getframe().f_code.co_name} start")
    name = "All-in-one-TM-FileStorageSecurity"
    resp, stack_status = cfn._find_cfn_stack(name)
    print(stack_status)
    assert resp is True
    print(f"{sys._getframe().f_code.co_name} end")


def test_delete_cloudformation_stack_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    stack_name = "cloudfront-bill-per-medium-dev-main"
    cfn._delete_cloudformation_stack(stack_name)
    print(f"{sys._getframe().f_code.co_name} end")


# ################ACMCertificate########################
def test_get_acm_certificate_arn_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")

    domain_name = "higuys.space"
    arn = acm._get_acm_certificate_arn(domain_name)
    print(arn)
    print(f"{sys._getframe().f_code.co_name} end")


def test_make_certificate_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    domain_name = "test.xyz"
    certificate_arn = acm._make_certificate(domain_name)
    print(certificate_arn)
    print(f"{sys._getframe().f_code.co_name} end")


def test_describe_certificate_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    certificate_arn = "arn:aws:acm:ap-northeast-1:320269048510:certificate/94d8f8e3-95e1-4c31-86fa-118a6a4e7c69"
    cname_record = acm._describe_certificate(certificate_arn)
    print(cname_record)
    print(f"{sys._getframe().f_code.co_name} end")


# ################Route53########################
def test_get_route53_hosted_zone_id_and_domain_name_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")

    host_name = "adtokyo-test.vootec.net11"
    hosted_zone_id, domain_name = route53._host_name_info_in_route53(host_name)
    print(hosted_zone_id, domain_name)
    print(f"{sys._getframe().f_code.co_name} end")


def test_create_hosted_zone_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")

    host_name = "test.xyz"
    route53._create_hosted_zone(host_name)

    print(f"{sys._getframe().f_code.co_name} end")


def test_change_resource_record_sets_Normal001():
    hosted_zone_id = "Z089394918TS7Z6MJ6MU7"
    record_set = {'Name': '_5ec78db47c3444e8a20a8240113af3a8.test.xyz.', 'Type': 'CNAME',
                  'Value': '_d5f6b8f0dfcec5b080a00ae78056a7df.yzdtlljtvc.acm-validations.aws.'}
    route53._change_resource_record_sets(hosted_zone_id, record_set)


# ################ EC2 ########################
def test_check_ec2_state_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    instance_id = ""
    ec2._check_ec2_state(instance_id)
    print(f"{sys._getframe().f_code.co_name} end")


def test_check_key_pairs_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    key_name = "lagnasystems"
    res = ec2._check_key_pairs(key_name)
    print(res)
    print(f"{sys._getframe().f_code.co_name} end")
