import sys

sys.path.insert(1, 'wordpress-server-construction-with-kusanagi-docker/wordpress-server-construction-with-kusanagi')  # NOQA: E402
import boto3
from src.utils import aws_handler
from src import handling_new_domain
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


def test_create_new_hostzone_and_dns_record_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    domain = "test03.xyz"
    name_servers = handling_new_domain._create_new_hostzone_and_dns_record(route53,
                                                                           acm,
                                                                           domain)
    print(name_servers)

    print(f"{sys._getframe().f_code.co_name} end")


def test_handling_domain_Normal001():
    # ACM,rout53存在
    print(f"{sys._getframe().f_code.co_name} Start.")
    notifier_config = {"caller_room_id": "250157426",
                       "api_token": "bac2678223bf79f13f41c3a4e250b1be"}
    args_info = {"host_name": "test.higuys.space"}
    args_info = handling_new_domain.handling_domain(route53, acm,
                                                    notifier_config, args_info)
    print(args_info)
    print(f"{sys._getframe().f_code.co_name} end")


def test_handling_domain_Normal002():
    # ACM,rout53存在
    print(f"{sys._getframe().f_code.co_name} Start.")
    notifier_config = {
        "api_token": "bac2678223bf79f13f41c3a4e250b1be"}
    args_info = {"host_name": "higuystext.space",
                 "caller_room_id": "250157426"}
    args_info = handling_new_domain.handling_domain(route53, acm,
                                                    notifier_config, args_info)
    print(args_info)
    print(f"{sys._getframe().f_code.co_name} end")
