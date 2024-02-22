import os
import sys
import time
import traceback
import urllib.parse
import urllib.request
from logging import Formatter, StreamHandler, getLogger

import slackweb

# ロガー初期化 start ####################################################
_LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")

_logger = getLogger(__name__)
_logger.setLevel(_LOG_LEVEL)
formatter = Formatter(
    fmt="%(asctime)s:[%(filename)s](%(lineno)s)fn:%(funcName)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# stdout
s_handler = StreamHandler()
s_handler.setLevel(_LOG_LEVEL)
s_handler.setFormatter(formatter)
_logger.addHandler(s_handler)


def make_setting_fail_message_text(
    _ACCOUNT_NAME: str, service: str, setting_fail: dict
) -> str:
    """設定失敗時のメッセージテキストを生成

    パラメーター
    ----------
    _ACCOUNT_NAME : str
        アカウント名
    service : str
        サービス名
    setting_fail : dict
        設定失敗のアラーム

    戻り値
    ----------
    str
        メッセージテキスト
    """

    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    message = f"{_ACCOUNT_NAME} アカウント {service} アラームの作成・更新は失敗しました確認してください\n"

    for alarm_info, reason in setting_fail.items():
        message += f"   AlarmName: {alarm_info['AlarmName']}"
        message += f"       原因: {reason}"

    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return message


def make_setting_success_message_text(
    _ACCOUNT_NAME: str, service: str, setting_success: dict
) -> str:
    """設定成功のメッセージテキストを生成

    パラメーター
    ----------
    _ACCOUNT_NAME :str
        アカウント名
    service : str
        サービス名
    setting_success : dict
        設定成功のアラーム

    戻り値
    ----------
    str
        メッセージテキスト
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    message = f" {_ACCOUNT_NAME} アカウント {service} アラーム付与\n"

    for _, alarm_info in setting_success.items():
        action_str = "\n        ".join(alarm_info["AlarmActions"])

        message += f'   AlarmName: {alarm_info["AlarmName"]}\n'
        message += "   Actions: \n"
        message += f"        {action_str}\n"
        message += f'   Threshold: {alarm_info["Threshold"]}\n'
        message += f'   Period: {alarm_info["Period"]}\n'
        message += f'   EvaluationPeriods: {alarm_info["EvaluationPeriods"]}\n'
        message += f'   ComparisonOperator: {alarm_info["ComparisonOperator"]}\n'
        message += "\n"
    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return message


def make_message_for_alart_check(
    _ACCOUNT_NAME: str,
    service: str,
    alarms_with_wrong_destination: dict,
    alarms_with_wrong_setting: dict,
    instances_without_alarm: dict,
) -> str:
    """アラームチェック用のメッセージテキストを生成

    パラメーター
    ----------
    _ACCOUNT_NAME : str
        アカウント名
    service : str
        サービス名
    alarms_with_wrong_destination : dict
        間違った宛先のアラーム
    alarms_with_wrong_setting : dict
        間違った設定のアラーム
    instances_without_alarm : dict
        アラームのないインスタンス

    戻り値
    ----------
    str
        メッセージテキスト
    """
    title = f"【{_ACCOUNT_NAME}】{service} のCloudWatchアラーム確認\n"
    message_text = ""

    if len(alarms_with_wrong_destination) != 0:
        message_text += f"以下の{service}のアラーム宛先に有効なSNSトピックがない\n"
        for alarm_name, alarm_info in alarms_with_wrong_destination.items():
            message_text += f"  アラート名: {alarm_name} \n"
            message_text += "    AlarmActions:\n     "
            message_text += "\n     ".join(alarm_info.get("AlarmActions", []))
            message_text += "\n\n"

    if len(alarms_with_wrong_setting) != 0:
        message_text += f"以下の{service}のアラーム設定が正しくない\n"
        for alarm_name, alarm_info in alarms_with_wrong_setting.items():
            message_text += f"  アラート名: {alarm_name} \n"

            if service == "ec2":
                if (
                    alarm_info["MetricName"] == "StatusCheckFailed_System"
                    and "arn:aws:automate:ap-northeast-1:ec2:recover"
                    not in alarm_info["AlarmActions"]
                ):
                    message_text += "     recoverが含まれない\n"

            message_text += f"     Periodは {alarm_info.get('Period','設定なし')}\n"
            message_text += (
                f"     Thresholdは {alarm_info.get('Threshold','設定なし')}\n"
            )
            message_text += f"     EvaluationPeriodsは {alarm_info.get('EvaluationPeriods','設定なし')}\n"
            message_text += f"     ComparisonOperatorは {alarm_info.get('ComparisonOperator','設定なし')}\n"
            message_text += "\n"

    if len(instances_without_alarm) != 0:
        alarms_list = list(instances_without_alarm.keys())
        message_text += f"以下の{service}にアラームがついていなかったよ！\n   "
        message_text += "\n   ".join(alarms_list)
        message_text += "\n"

    if message_text == "":
        message_text += (
            f"アラームチェックをしたよ!\nアラームをつけてない{service}はなかったよ！"
        )

    message_text = f"{title}{message_text}"
    return message_text


def _send_chatwork(room_id_list: list, api_token: str, message: str):
    """チャットワークにメッセージを送信

    パラメーター
    ----------
    room_id_list : list
        ルームIDのリスト
    api_token : str
        チャットワークAPIトークン
    message : str
        メッセージテキスト

    戻り値
    ----------
    なし
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    try:
        for room_id in room_id_list:
            post_message_url = f"https://api.chatwork.com/v2/rooms/{room_id}/messages"
            headers = {"X-ChatWorkToken": api_token}
            data = urllib.parse.urlencode({"body": message})
            data = data.encode("utf-8")

            # リクエストの生成と送信
            request = urllib.request.Request(
                post_message_url, data=data, method="POST", headers=headers
            )
            with urllib.request.urlopen(request) as response:
                response_body = response.read().decode("utf-8")
                _logger.info(response_body)
        time.sleep(0.1)
    except Exception as e:
        _logger.error(f"Error: {sys._getframe().f_code.co_name} ")
        _logger.error(traceback.format_exc())
        raise e
    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def _send_slack(slack_url: str, title: str, text: str):
    """Send message to Slack.

    パラメーター
    ----------
    slack_url : str
        Slack webhook URL
    title : str
        メッセージのタイトル
    text : str
        メッセージテキスト

    戻り値
    ----------
    なし
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")

    attachments = []
    attachment = {"title": title, "text": text, "mrkdwn_in": ["text"]}

    slack = slackweb.Slack(url=slack_url)
    attachments.append(attachment)
    slack.notify(attachments=attachments)

    _logger.info(f"{sys._getframe().f_code.co_name} End.")


def send_message(config: dict, message_text: str):
    """設定に基づいてメッセージを Chatwork または Slack に送信

    パラメーター
    ----------
    config : dict
        設定変数
    message_text : str
        メッセージテキスト

    戻り値
    ----------
    なし
    """
    message_list = message_text.split("\n")

    title = message_list[0]
    text = "\n".join(message_list[1:])

    if config["send_to_chatwork"]:
        message_text = f"[info][title]{title}[/title]\n{text}[/info]"
        _send_chatwork(
            config["chatwork"]["room_id_list"],
            config["chatwork"]["api_token"],
            message_text,
        )
    else:
        _send_slack(config["slack"]["slack_url"], title, text)
    time.sleep(0.3)
