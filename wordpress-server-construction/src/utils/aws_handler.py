import sys
import json
from datetime import datetime
from src.utils import log_handler
import time

_logger = log_handler.LoggerHander()


class EC2(object):

    def __init__(self, ec2_client) -> None:
        self.client = ec2_client

    def _get_public_ip(self, instance_id):
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")

        res = self.client.describe_instances(
            InstanceIds=[instance_id]
        )
        _logger.info(f"{sys._getframe().f_code.co_name} End.")
        return res['Reservations'][0]["Instances"][0]["PublicIpAddress"]

    def _check_ec2_state(self, instance_id):
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")
        ec2_waiter = self.client.get_waiter('instance_running')
        try:
            ec2_waiter.wait(
                InstanceIds=[instance_id],
                WaiterConfig={
                    'Delay': 10,
                    'MaxAttempts': 10
                }
            )
            _logger.info("Start EC2 OK")
            return True
        except Exception:
            _logger.error("Start EC2 Error")
            return False
        finally:
            _logger.info(f"{sys._getframe().f_code.co_name} End.")

    def _create_key_pair(self, key_name):
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")
        try:
            response = self.client.create_key_pair(KeyName=key_name)
            return response['KeyMaterial']
        except Exception as e:
            _logger.error(f"Error: {e}")
            return None
        finally:
            _logger.info(f"{sys._getframe().f_code.co_name} End.")

    def _check_key_pairs(self, key_name):
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")
        try:
            response = self.client.describe_key_pairs(
                Filters=[
                    {
                        'Name': 'key-name',
                        'Values': [
                            key_name
                        ]
                    }
                ]
            )

            if len(response['KeyPairs']) != 0:
                return True
            else:
                return False
        finally:
            _logger.info(f"{sys._getframe().f_code.co_name} End.")


class SSM(object):
    def __init__(self, ssm_client, instance_id: str) -> None:
        self.client = ssm_client
        self.instance_id = instance_id

    def _send_ssm_command(self,  document_name: str,
                          parameters: dict) -> str or bool:
        """SSM Run Command を実行。

        Parameters
        ----------
        instance_ids : str
            コマンドを実行したいインスタンス ID
        document_name : str
            使用したい SSM Run Command のドキュメントの名前。
            基本は AWS-RunShellScript だけで事足りる
        parameters : dict
            パラメーターを格納した辞書。
            ドキュメントの種類に応じて必要なキーと値が変わるので注意が必要。

        Returns
        -------
        str or bool
            成功した場合は文字列で コマンド ID を、失敗した場合は False を返す
        """
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")

        try:
            res = self.client.send_command(
                InstanceIds=[self.instance_id],
                DocumentName=document_name,
                Parameters=parameters,
                OutputS3BucketName="cor-infra-bucket",
                OutputS3KeyPrefix='cloud-formation/log/',
            )

            _command_id = res['Command']['CommandId']
            # エラーにならなかった場合、コマンド ID を返す
            if _command_id is not None:
                return _command_id
            else:
                return False

        except Exception as e:
            _logger.error(f"Error: {sys._getframe().f_code.co_name} ")
            return False
        finally:
            _logger.info(f"{sys._getframe().f_code.co_name} End.")

    def _wait_ssm_command_execution(self, command_id: str) -> bool:
        """SSM Run Command の指定コマンド実行完了を待つ

        Parameters
        ----------
        command_id : str
            実行完了まで待機したいコマンドの ID
        instance_id : str
            コマンド実行が行われているインスタンスの ID

        Returns
        -------
        bool
            待機中にコマンド実行が完了した場合は True,
            待機中にコマンド実行が終わらなかった場合は False
        """
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")

        try:

            # コマンド実行完了まで待機させる
            _waiter = self.client.get_waiter('command_executed')

            _waiter.wait(
                CommandId=command_id,
                InstanceId=self.instance_id,
                WaiterConfig={
                    'Delay': 60,
                    'MaxAttempts': 20
                }
            )
            # タイムアウトしなかった場合、True
            return True

        except Exception:
            _logger.error(f"Error: {sys._getframe().f_code.co_name} ")
            return False
        finally:
            _logger.info(f"{sys._getframe().f_code.co_name} End.")


class ACMCertificate(object):
    def __init__(self, acm_client) -> None:
        self.client = acm_client

    def _get_acm_certificate_arn(self, domain_name: str) -> str:
        """指定したドメインに対応した ACM SSL 証明書の ARN を取得する

        Parameters
        ----------
        acm_client :

        domain_name : _type_
            該当 ACM SSL 証明書が対応している筈のドメイン名

        Returns
        -------
        str
            ACM SSL 証明書の ARN
        """
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")
        _paginator = self.client.get_paginator('list_certificates')

        _status_filter: list = ['PENDING_VALIDATION', 'ISSUED']
        # 既に発行されているものだけ検索
        for _page in _paginator.paginate(CertificateStatuses=_status_filter):
            for _cert_summary in _page.get("CertificateSummaryList", []):
                # _logger.info(_cert_summary)
                if domain_name == _cert_summary.get("DomainName"):
                    _logger.info(f"{sys._getframe().f_code.co_name} End.")
                    return _cert_summary.get("CertificateArn")
        # 一致するものがなかった場合
        _logger.info(f"{sys._getframe().f_code.co_name} End.")
        return ""

    def _make_certificate(self, domain):
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")
        response = self.client.request_certificate(
            DomainName=domain,
            ValidationMethod='DNS',
            SubjectAlternativeNames=[
                f"*.{domain}"
            ]
        )

        _logger.info(f"{sys._getframe().f_code.co_name} End.")

        return response['CertificateArn']

    def _describe_certificate(self, certificate_arn):
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")
        try:
            for _ in range(10):
                res = self.client.describe_certificate(
                    CertificateArn=certificate_arn
                )
                if 'DomainValidationOptions' in res['Certificate'] and \
                        'ResourceRecord' in res['Certificate']['DomainValidationOptions'][0]:
                    return res['Certificate']['DomainValidationOptions'][0]['ResourceRecord']
                time.sleep(10)
            return {}
        finally:
            _logger.info(f"{sys._getframe().f_code.co_name} End.")


class Route53():
    def __init__(self, route53_client) -> None:
        self.client = route53_client

    def _host_name_info_in_route53(self, host_name: str):
        """Route 53 の ホストゾーンの ID とそのドメイン名（末尾の'.'は省く）を返す

        Parameters
        ----------
        route53_client:
            route53のクライアント
        host_name : str
            検索に利用するホスト名。末尾の '.' の有無は関係なく検索可能。

        Returns
        -------
        list
            1つ目にホストゾーン ID を、２つ目にドメイン名（最後の'.'除く）を返す
        """
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")

        paginator = self.client.get_paginator("list_hosted_zones")
        # ホスト名が '.' で終わらない場合、追加する
        host_name = host_name if host_name.endswith(".") else host_name+"."

        for page in paginator.paginate():
            for _hosted_zone in page.get("HostedZones", []):
                _domain_name = _hosted_zone.get("Name")

                if _domain_name in host_name:

                    _hosted_zone_id = _hosted_zone["Id"].replace(
                        "/hostedzone/", "")
                    _logger.info(f"{sys._getframe().f_code.co_name} End.")
                    return _hosted_zone_id, _domain_name[0:-1]
        _logger.info(f"{sys._getframe().f_code.co_name} End.")
        return None, None

    def _create_hosted_zone(self, host_name):
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")
        response = self.client.create_hosted_zone(
            Name=host_name,
            CallerReference=host_name
        )
        hosted_zone_id = response["HostedZone"]["Id"].replace(
            "/hostedzone/", "")
        name_servers = response['DelegationSet']['NameServers']
        _logger.info(f"{sys._getframe().f_code.co_name} End.")

        return hosted_zone_id, name_servers

    def _change_resource_record_sets(self, hosted_zone_id, record_set):
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")
        self.client.change_resource_record_sets(
            HostedZoneId=hosted_zone_id,
            ChangeBatch={
                'Changes': [
                    {
                        'Action': 'CREATE',
                        'ResourceRecordSet': {
                            'Name': record_set['Name'],
                            'Type': record_set['Type'],
                            'TTL':300,
                            'ResourceRecords': [
                                {
                                    'Value': record_set['Value']
                                },
                            ]
                        }
                    },
                ]
            }
        )

        _logger.info(f"{sys._getframe().f_code.co_name} End.")


class Cloudformation(object):
    def __init__(self, cfn_client):
        self.client = cfn_client

    def _find_cfn_stack(self, name: str) -> bool:
        """指定したスタックが存在するか探す。
        Parameters
        ----------
        cfn_client :
            cloudFormationのクライアント
        name : str
            検索する CloudFormation スタック名

        Returns
        -------
        bool
            指定したスタックが存在すれば True, なければ False
        """
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")
        # Status to check
        stack_status_filter = ['CREATE_IN_PROGRESS', 'CREATE_FAILED',
                               'CREATE_COMPLETE', 'ROLLBACK_IN_PROGRESS',
                               'ROLLBACK_FAILED', 'ROLLBACK_COMPLETE',
                               'DELETE_IN_PROGRESS'
                               ]

        # find_stack だと存在しない場合に例外を返すので、一覧を取得している
        #res = self.client.list_stacks(StackStatusFilter=stack_status_filter)
        paginator = self.client.get_paginator('list_stacks')

        for page in paginator.paginate(StackStatusFilter=stack_status_filter):

            for _item in page.get('StackSummaries', []):
                if _item.get('StackName', "") == name:
                    _logger.error(f"Stack {name} すでに存在")
                    return True,  _item.get('StackStatus', None)

            _logger.info(f"{sys._getframe().f_code.co_name} End.")
            return False, None

    def _create_cfn_stack(self, template_url, args_info) -> str or bool:
        """EC2 インスタンス用の CloudFormation スタックを作成する。

        Parameters
        ----------
        cfn_client :
            cloudFormationのクライアント
        template_url :
            テンプレートの所在URL
        args_info :
            KUSANAGIの設定情報

        Returns
        -------
        str or bool
            作成に成功すればインスタンス ID を、失敗すれば None を返す。
        """

        _logger.info(f"{sys._getframe().f_code.co_name} Start.")
        try:
            res = self.client.create_stack(
                StackName=args_info["stack_name"],
                TemplateURL=template_url,
                Parameters=[
                    {
                        'ParameterKey': 'HostName',
                        'ParameterValue': args_info["host_name"]
                    },
                    {
                        'ParameterKey': 'AmiId',
                        'ParameterValue': args_info["ami"]
                    },
                    {
                        'ParameterKey': 'KeyName',
                        'ParameterValue': args_info["key_name"]
                    },
                    {
                        'ParameterKey': 'InstanceType',
                        'ParameterValue': args_info["instance_type"]
                    },
                    {
                        'ParameterKey': 'SubnetId',
                        'ParameterValue': args_info["subnet_id"]
                    },
                    {
                        'ParameterKey': 'SubnetId2',
                        'ParameterValue': args_info["subnet_id2"]
                    },
                    {
                        'ParameterKey': 'VPCId',
                        'ParameterValue': args_info["vpc_id"]
                    },
                    {
                        'ParameterKey': 'VolumeSize',
                        'ParameterValue': args_info["ebs_size"]
                    },
                    {
                        'ParameterKey': 'HostZoneId',
                        'ParameterValue': args_info["host_zone_id"]
                    },
                    {
                        'ParameterKey': 'DomainName',
                        'ParameterValue': args_info["domain_name"]
                    },
                    {
                        'ParameterKey': 'AcmCertificateArn',
                        'ParameterValue':  args_info["acm_certificate_arn"]
                    },

                ],
                Capabilities=[
                    'CAPABILITY_NAMED_IAM',
                ],
                # EnableTerminationProtection=True
                EnableTerminationProtection=False
            )

            _logger.info(res)

            # スタック作成完了まで待機する。
            # 30秒毎に確認する。最大 24 回確認
            waiter = self.client.get_waiter('stack_create_complete')
            waiter.wait(
                StackName=args_info["stack_name"],
                WaiterConfig={
                    'Delay': 30,
                    'MaxAttempts': 24
                }
            )

            # 作成したEC2インスタントのIDをリターン
            desc = self.client.list_stack_resources(
                StackName=args_info["stack_name"])
            summaries = desc.get('StackResourceSummaries', {})

            for item in summaries:
                logical_resource_id = item.get("LogicalResourceId")
                physical_resource_id = item.get('PhysicalResourceId', None)
                if logical_resource_id == "EC2Instance":
                    return physical_resource_id
            _logger.info(f"{sys._getframe().f_code.co_name} End.")

            return None
        except Exception:
            _logger.error(f"Error: {sys._getframe().f_code.co_name} ")

        finally:
            _logger.info(f"{sys._getframe().f_code.co_name} End.")

    def _delete_cloudformation_stack(self, stack_name):
        _logger.info(f'begin to delete {stack_name}')
        self.client.delete_stack(StackName=stack_name)

        # スタック削除完了まで待機する。
        # 10秒毎に確認する。最大 24 回確認
        waiter = self.client.get_waiter('stack_delete_complete')
        waiter.wait(
            StackName=stack_name,
            WaiterConfig={
                'Delay': 10,
                'MaxAttempts': 24
            })
        _logger.info(f'finish to delete {stack_name}')

    @ staticmethod
    def _make_cfn_stack_parameter(args_info: dict, config: dict,
                                  host_zone_id, acm_certificate_arn,
                                  domain_name) -> dict:
        """CloudFormationのパラメータを作成

        Parameters
        ----------
        args_info : dict
            KUSANAGIの設定情報
        config : dict
            設定ファイル
        host_zone_id : str
            host_zoneのID
        domain_name : str
            ドメイン名
        acm_certificate_arn : str
            ACM証明書のarm

        Returns
        -------
        args_info : dict
            KUSANAGIの設定情報
        """
        _logger.info(f"{sys._getframe().f_code.co_name} Start.")

        az1 = args_info["availability_zone"]
        az2 = "C" if az1 == "A" else "A"

        args_info["subnet_id"] = config.get("vpc").get("subnets").get(az1)
        args_info["subnet_id2"] = config.get("vpc").get("subnets").get(az2)
        args_info["vpc_id"] = config["vpc"]["vpc_id"]

        args_info["host_zone_id"] = host_zone_id
        args_info["acm_certificate_arn"] = acm_certificate_arn
        args_info["domain_name"] = domain_name

        _logger.info(f"{sys._getframe().f_code.co_name} End.")
        return args_info
