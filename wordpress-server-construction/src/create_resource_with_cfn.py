import os
import sys
import traceback
from datetime import datetime
from src.utils import log_handler, notify_message

# ロガー初期化
_LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
_logger = log_handler.LoggerHander(log_level=_LOG_LEVEL)


def create_resource_with_cfn(cfn, acm, route53, ec2, config, args_info):
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    message = None
    try:
        # stackのチェック,stack存在すれば停止、存在しないと構築
        is_exiting, stack_status = cfn._find_cfn_stack(args_info["stack_name"])

        if is_exiting:
            message = f"{args_info['host_name']}のstackすでに存在,stack statusは {stack_status}\n"
            _logger.info(message)

            if stack_status not in ['CREATE_IN_PROGRESS', 'CREATE_COMPLETE']:

                _delete_stack_and_send_message(cfn, args_info,
                                               config, message)
            else:

                notify_message.send_message(config["api_token"],
                                            args_info["caller_room_id"],
                                            message)

        else:
            # 5. 存在しないと、CloudFormation でリソースを作成
            cfn_result = _create_cloudFormation_resource(cfn, acm,
                                                         route53, config,
                                                         args_info)

            if cfn_result == "stack failed":
                message = f"{args_info['stack_name']} 構築失敗\n"
                _delete_stack_and_send_message(cfn, args_info,
                                               config, message)
                return

            if not ec2._check_ec2_state(cfn_result):
                message = f"{args_info['stack_name']} 構築成功が、EC2起動失敗\n"
                _delete_stack_and_send_message(cfn, args_info,
                                               config, message)
                return

        # 6.1 構築成功の場合、EC2インスタンスIDを保存して、リターン

            args_info["instance_id"] = cfn_result
    except Exception as e:
        _logger.error(f"Error: {sys._getframe().f_code.co_name} ")
        _logger.error(traceback.format_exc())
    finally:
        _logger.info(f"args_info:{args_info}")
        _logger.info(f"{sys._getframe().f_code.co_name} End.")
        return args_info


def _delete_stack_and_send_message(cfn, args_info, config, message):

    message += f'{datetime.now()}, {args_info["stack_name"]} の削除開始\n'
    cfn._delete_cloudformation_stack(args_info["stack_name"])
    message += f'{datetime.now()}, {args_info["stack_name"]} の削除終了\n'

    notify_message.send_message(config["api_token"],
                                args_info["caller_room_id"],
                                message)
    return message


def _create_cloudFormation_resource(cfn, acm, route53, config: dict,
                                    args_info: dict) -> str:
    """cloudFormationスタックを作成する

    Parameters
    ----------
    cfn_client :
        cloudformationのクライアント
    acm_client :
        ACMのクライアント
    route53_client :
        route53のクライアント
    config : dict
        設定ファイル
    args_info : dict
        KUSANAGIの設定情報

    Returns
    -------
    str or bool
        作成に成功すればインスタンス ID を、失敗すれば 失敗原因メッセージの送信
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")

    try:

        # ドメイン関連設定
        host_zone_id, domain_name = route53._host_name_info_in_route53(
            args_info["host_name"])
        acm_certificate_arn = acm._get_acm_certificate_arn(domain_name)

        args_info = cfn._make_cfn_stack_parameter(args_info, config,
                                                  host_zone_id, acm_certificate_arn,
                                                  domain_name)
        cfn_result = cfn._create_cfn_stack(config['cfn_template'],
                                           args_info)
        if cfn_result is None:
            _logger.error(f"構築失敗")
            return "stack failed"

        _logger.info(f"構築成功、cfn_result:{cfn_result}")
        return cfn_result
    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")
