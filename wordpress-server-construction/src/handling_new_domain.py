import os
import sys
import traceback

from src.utils import log_handler

# ロガー初期化
_LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
_logger = log_handler.LoggerHander(log_level=_LOG_LEVEL)


def handling_domain(route53, acm, args_info):
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    name_servers = None
    try:
        host_zone_id, domain_name = route53._host_name_info_in_route53(
            args_info["host_name"])
        _logger.info(
            f"host_zone_id: {host_zone_id}, domain_name: {domain_name}")

        if host_zone_id is not None and domain_name is not None:
            # ドメインがすでに存在、acm のarnをとる
            acm_certificate_arn = acm._get_acm_certificate_arn(domain_name)
            args_info["acm_certificate_arn"] = acm_certificate_arn
            args_info["host_zone_id"] = host_zone_id
            args_info["domain_name"] = domain_name

        else:
            name_servers = _create_new_hostzone_and_dns_record(route53, acm,
                                                               args_info["host_name"])
            args_info["name_servers"] = name_servers

        return args_info
    except Exception as e:
        _logger.error(f"Error: {sys._getframe().f_code.co_name} ")
        _logger.error(traceback.format_exc())
    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def _create_new_hostzone_and_dns_record(route53, acm, domain) -> list:
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    # 新規 host_zoneとamcを作成
    hosted_zone_id, name_servers = route53._create_hosted_zone(domain)
    # 新規ACM作成
    _logger.info(f"{hosted_zone_id} 作成済み")
    certificate_arn = acm._make_certificate(domain)
    # CNAMEレコードを取得

    cname_record = acm._describe_certificate(certificate_arn)
    if cname_record == {}:
        return [f"{domain}のACM作成失敗"]

    _logger.info(f"CNAMEレコードを取得済み{cname_record}")

    # CNAMEレコードをhostzoneに登録
    route53._change_resource_record_sets(hosted_zone_id, cname_record)
    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return name_servers
