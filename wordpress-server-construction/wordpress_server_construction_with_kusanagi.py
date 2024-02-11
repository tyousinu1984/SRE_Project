import json
import os
import sys
import time
import traceback
import boto3
import argparse
from src import create_resource_with_cfn, handling_new_domain, ssm_run_command
from src.utils import aws_handler, log_handler, notify_message

# ロガー初期化
_LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
_logger = log_handler.LoggerHander(log_level=_LOG_LEVEL)

_REGION: str = os.environ.get("REGION", "ap-northeast-1")


def main(args_info):
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    _STATUS = "正常"
    error_message = None
    try:
        # 設定ファイル読み取り
        config = _find_config(args_info["account"],  args_info["stage"])
        # 1. ユーザーのroom IDを獲得,args_info に保存
        _direct_chat_room_id = notify_message.get_direct_chat_room_id(config["api_token"],
                                                                      args_info["caller_user_id"])
        args_info["direct_chat_room_id"] = _direct_chat_room_id

        notify_message.send_message(config["api_token"], args_info["caller_room_id"],
                                    "自動構築開始")

        # #############　構築開始 　#################################

        # client生成,class初期化
        cfn_client, acm_client, route53_client, \
            ssm_client, ec2_client = _get_aws_client(config["iam_role"])

        cfn = aws_handler.Cloudformation(cfn_client)
        acm = aws_handler.ACMCertificate(acm_client)
        route53 = aws_handler.Route53(route53_client)
        ec2 = aws_handler.EC2(ec2_client)

        # ----------------------------------------
        # cloudformationによるサーバーの構築
        # ----------------------------------------
        # 4. KeyPairの確認
        args_info = _verify_key_pair(ec2, args_info, config)
        time.sleep(2)

        # 5. domainの確認、新規ドメインかどうか、
        args_info = handling_new_domain.handling_domain(route53, acm,
                                                        args_info)
        if "name_servers" in args_info and args_info["name_servers"] is not None:
            # 新規ドメイン、送信、終了
            message = notify_message.new_domain_message(args_info["host_name"],
                                                        args_info["name_servers"])
            notify_message.send_message(config["api_token"],
                                        args_info["caller_room_id"],
                                        message)
            return

        # 5. CloudFormation でリソースを作成
        # 6 実行結果確認、構築失敗の場合、送信、終了
        args_info = create_resource_with_cfn.create_resource_with_cfn(cfn, acm, route53,
                                                                      ec2, config,
                                                                      args_info)
        if "instance_id" not in args_info:
            _STATUS = "異常"
            return

        # 7 chatworkに通知する
        message = "リソース構築成功、これからWordPressを構築する"
        _logger.info(message)

        notify_message.send_message(config["api_token"],
                                    args_info["caller_room_id"],
                                    message)
        time.sleep(1)

        # ----------------------------------------
        # SSMによるwordpressの設定
        # ----------------------------------------
        ssm = aws_handler.SSM(ssm_client, args_info["instance_id"])
        ssm_result, login_info = ssm_run_command.setup_kusangi_server(ssm, config,
                                                                      args_info["host_name"])

        if ssm_result is False:
            message = notify_message.ssm_run_commamd_failed_message()
            notify_message.send_message(config["api_token"],
                                        args_info["caller_room_id"],
                                        message)
            _STATUS = "異常"
            return

        # ----------------------------------------------------
        # 3. 成功メッセージを個人と鍵置き場それぞれに送る
        # ----------------------------------------------------

        login_info["instance_id"] = args_info["instance_id"]
        login_info["public_ip"] = ec2._get_public_ip(args_info["instance_id"])

        message = notify_message.stack_success_message(login_info,
                                                       args_info["host_name"])
        if args_info["direct_chat_room_id"] is not None:
            config["room_id_list"].append(_direct_chat_room_id)

        for room_id in config["room_id_list"]:
            notify_message.send_message(config["api_token"],
                                        room_id,
                                        message,)
    except Exception as e:
        _logger.error(f"Error: {sys._getframe().f_code.co_name} ")
        _logger.error(traceback.format_exc())
        _STATUS = "異常"
        error_message = f"[code]{str(e)}[/code]"
    finally:

        message = f"処理は {_STATUS} 終了"

        if error_message is not None:
            message += "\n"
            message += error_message

        notify_message.send_message(config["api_token"],
                                    args_info["caller_room_id"],
                                    message)

        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def _verify_key_pair(ec2: aws_handler.EC2, args_info: dict, config: dict):
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")

    try:
        if args_info.get("key_name") is None:
            args_info["key_name"] = args_info["stack_name"]

        is_exist = ec2._check_key_pairs(args_info["key_name"])

        if is_exist:
            _logger.info(f'{args_info["key_name"]} は存在')
        else:
            _logger.info(f'{args_info["key_name"]} は存在しない')
            key_material = ec2._create_key_pair(args_info["key_name"])
            _logger.info("KeyPairを送信")
            _send_key_pair(args_info, config, key_material)

        return args_info
    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def _send_key_pair(args_info, config, key_material):
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")

    message = f'【{args_info["account"]}】アカウントのKeyPair\n'

    files = {
        'file': (f'{args_info["key_name"]}.pem', key_material, 'text/csv'),
        'message': message
    }
    if args_info.get("direct_chat_room_id") is not None:
        config["room_id_list"].append(args_info["direct_chat_room_id"])

    for room_id in config["room_id_list"]:

        notify_message.send_message_with_file(config["api_token"],
                                              room_id, files)

    _logger.info(f"{sys._getframe().f_code.co_name} End.")


def _get_aws_client(iam_role_arn: str = None):
    """IAMロールによりクライアンを生成する

    Parameters
    ----------
    iam_role_arn : str, optional
        IAMのローカ, by default None

    Returns
    -------
    クライアント

    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")

    if iam_role_arn == "" or iam_role_arn is None:
        cfn_client = boto3.client("cloudformation")
        acm_client = boto3.client("acm")
        route53_client = boto3.client("route53")
        ssm_client = boto3.client("ssm")
        ec2_client = boto3.client("ec2")
    else:
        sts = boto3.client("sts")

        iam_role_name = iam_role_arn.split("/")[-1]

        # セッション切り替え
        res = sts.assume_role(
            RoleArn=iam_role_arn,
            RoleSessionName=iam_role_name
        )

        credentals = res['Credentials']
        session = boto3.session.Session(
            aws_access_key_id=credentals['AccessKeyId'],
            aws_secret_access_key=credentals['SecretAccessKey'],
            aws_session_token=credentals['SessionToken'],
            region_name=_REGION
        )
        cfn_client = session.client("cloudformation")
        acm_client = session.client("acm")
        route53_client = session.client("route53")
        ssm_client = session.client("ssm")
        ec2_client = session.client("ec2")

    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return cfn_client, acm_client, route53_client, ssm_client, ec2_client


def _get_get_object(s3_client, bucket: str, key: str) -> str:
    """s3からobjectを読み取り

    Parameters
    ----------
    s3_client :
        s3のクライアント
    bucket : str
        バケット
    key : str
        objectのkey名

    Returns
    -------
    str
        object内容

    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    _logger.info(f"bucket:{bucket},key:{key}")
    try:

        resp = s3_client.get_object(Bucket=bucket,
                                    Key=key)
        body = resp["Body"].read().decode('utf-8')
        return body.strip()
    except Exception as e:
        _logger.error(f"Error: {sys._getframe().f_code.co_name} ")
        _logger.error(traceback.format_exc())
        raise e
    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def _find_config(account, stage) -> dict:
    """Configファイルの情報を取得

    Parameters
    ----------
    _CONFIG_FILE_NAME : str
        設定ファイルのpath

    Returns
    -------
    dict
        Configファイルの情報
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    try:
        # 環境変数をとる
        CONFIG_FILE_BUCKET = os.environ.get("BUCKET", "cor-infra-bucket")
        CONFIG_FILE_KEY = os.environ.get("CONFIG_FILE",
                                         "jsons-for-container/wordpress-server-construction-with-kusanagi/config.json")
        config = {}
        client = boto3.client("s3")
        body = _get_get_object(client, CONFIG_FILE_BUCKET, CONFIG_FILE_KEY)
        _config = json.loads(body)

        _account_id = _config[account]["account_id"]
        _bucket = _config[account]["bucket"]

        config["room_id_list"] = _config["notify_room_list"]
        config["api_token"] = os.environ.get("CHATWORK_TOKEN")

        config["iam_role"] = _config["iam_role"].format(account_id=_account_id)
        config["cfn_template"] = _config["cfn_template"].format(bucket=_bucket)

        config["vpc"] = _config[account]["vpc"][stage]
        config["ssm_run_command"] = _config["ssm_run_command"]
        config["ssm_run_command"]["pre_exec_commands"] = [comm.format(bucket=_bucket)
                                                          for comm in _config["ssm_run_command"]["pre_exec_commands"]]

        return config

    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


if __name__ == '__main__':

    # 環境変数を取得

    try:
        p = argparse.ArgumentParser(
            prog="wordpress-server-construction-with-kusanagi.py",
            description="https://wiki.core-tech.jp/626a36ea8363bb003e472f67", add_help=True, epilog="end"
        )

        # 引数を取得
        p.add_argument("-host", "--host_name", type=str, required=True,
                       help="ホスト名,構築成功後、インスタンス名とNameというタグの値になる")

        p.add_argument("-kn", "--key_name", help="キーペアの名前")

        p.add_argument("-account", "--account", type=str, default="core",
                       help="awsのアカウント名,対応できるアカウント名はcore、mi-light、chocolat、imc、core-ipbunsan、fanne")

        p.add_argument("-stage", "--stage", type=str, default="dev",
                       help="ホスト名,構築成功後、インスタンス名とNameというタグの値になる")

        p.add_argument("-it", "--instance_type", type=str, default="t3.nano",
                       help="インスタンスタイプ")

        p.add_argument("-az", "--availability_zone", type=str, default="A",
                       help="A/C/D から選べるが、基本的にデフォルトでOK")

        p.add_argument("-ami", "--ami", type=str, default="ami-002cedb74d7169fa1",
                       help="AWS側提供するkusanagiのイメージID")

        p.add_argument("-ebs", "--ebs_size", type=str, default="30",
                       help="EBS のサイズ")

        p.add_argument("-tp", "--termination_protection", type=str, default="false",
                       help="EBS のサイズ")
        args_info: dict = vars(p.parse_args())
        args_info["caller_user_id"] = os.environ.get("caller_user_id")
        args_info["caller_room_id"] = os.environ.get("caller_room_id")
        args_info["stack_name"] = args_info["host_name"].replace(".", "-")

        _logger.info(args_info)

        main(args_info)

    except Exception as e:
        _logger.error(traceback.format_exc())
