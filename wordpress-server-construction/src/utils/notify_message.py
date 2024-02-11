import json
import sys

import requests
from requests.adapters import HTTPAdapter
from src.utils import log_handler
from urllib3.util import Retry

# ロガー初期化
_logger = log_handler.LoggerHander()


def get_direct_chat_room_id(api_token: str, account_id: str) -> str:
    """指定したアカウントIDとのダイレクトチャットの部屋番号を返す。

    Parameters
    ----------
    config : dict
        設定ファイル
    account_id : str
        指定したアカウントID

    Returns
    -------
    str
        ダイレクトチャットの部屋番号
    """

    if account_id == "" or not account_id:
        return None

    headers = {
        'X-ChatWorkToken': api_token,
        "Content-Type": "application/json;charset=utf-8"
    }
    response = requests.get(
        'https://api.chatwork.com/v2/contacts', headers=headers)

    chatwork_user_list = json.loads(response.text)

    for _item in chatwork_user_list:
        # print(item)
        _id = _item.get("account_id", "")
        if str(_id) == account_id:
            _room_id: str = _item.get("room_id", 0)
            return str(_room_id)

    return None


def send_message_with_file(api_token: str, room_id: str, files: str):
    """ファイル送信

    Parameters
    ----------
    api_token : str
        chatworkのAPI token
    room_id : str
        room id
    files : dict
        ファイル
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    try:
        headers = {'X-ChatWorkToken': api_token}

        url = f'https://api.chatwork.com/v2/rooms/{room_id}/files'
        #response = requests.post(url, headers=headers, files=files)

        session = requests.Session()
        retries = Retry(total=5,
                        backoff_factor=5,
                        status_forcelist=[500, 502, 503, 504, 429])
        session.mount("https://", HTTPAdapter(max_retries=retries))
        response = session.post(url, headers=headers, files=files)

        _logger.info(f"{room_id}: {response.text}")

    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def send_message(api_token: str, room_id: str, chat_text: str):
    """メッセージ送信

    Parameters
    ----------
    api_token : str
        chatworkのAPI token
    room_id : str
        room id
    chat_text : str
        送信メッセージ
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    try:
        print(chat_text)
        headers = {'X-ChatWorkToken': api_token}
        data = {'body': chat_text}
        _logger.info(chat_text)
        url = f'https://api.chatwork.com/v2/rooms/{room_id}/messages'

        response = requests.post(url, headers=headers, data=data)
        _logger.info(f"{room_id}: {response.text}")

    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def help_message() -> str:
    text = """
[info][title]ヘルプメッセージ[/title]
[info][title]構築用コマンド[/title]
build-up-wordpress $｛ホスト名｝ -stage $｛ステージ｝-kn $｛キーペア名｝ -account $｛アカウント｝[/info]

具体的な説明は
[info][title]設計書 [/title]
https://wiki.core-tech.jp/626a36ea8363bb003e472f67
[/info]
に参考してください
[/info]
    """
    return text


def stack_failed_message():
    return "Stack構築失敗しました。"


def key_not_specified():
    return "Key指定していない"


def ssm_run_commamd_failed_message() -> str:
    """ssm実行失敗のテキスト作成

    Returns
    -------
    str
        ssm実行失敗のテキスト
    """
    text = "Kusanagi サーバーを構築できませんでした！\n"
    text += "SSM Run Command によるサーバーの設定部分で失敗しました！！\n"
    return f"[info][title]Kusanagi WP サーバー自動立ち上げ[/title]{text}[/info]"


def stack_success_message(login_info: dict, host: str) -> str:
    """KUSANAGI構築成功メッセージ

    Parameters
    ----------
    login_info : dict
        ログイン情報
    host : str
        ホスト名

    Returns
    -------
    str
        _description_
    """
    text = f"[info][title]{host}[/title]"
    text += "[info][title]Web アクセス[/title]"
    text += f"Web ページ閲覧： {host}\n"
    text += f"WordPress ログイン： {host}/wp-login.php[/info]"
    text += f"[info][title]WordPress ログイン情報[/title]"
    text += f"ユーザー名： {login_info['wp_admin_name']}\n"
    text += f"パスワード： {login_info['wp_admin_password']}[/info]"
    text += f"[info][title]basic認証[/title]"
    text += f"ユーザー名： {login_info['basic_auth_user_name']}\n"
    text += f"パスワード： {login_info['basic_auth_user_password']}[/info]"
    text += f"[info][title]サーバー情報[/title]"
    text += f"インスタンスID： {login_info['instance_id']}\n"
    text += f"Name タグ：  {host}\n"
    text += f"IPアドレス： {login_info['public_ip']}[/info]"
    text += f"[info][title]DB接続情報[/title]"
    text += f"DB名：  {login_info['db_name']}\n"
    text += f"DBユーザー名： {login_info['db_user_name']}\n"
    text += f"DBルートパスワード： {login_info['db_root_password']}\n"
    text += f"DBパスワード： {login_info['db_user_password']}[/info]"
    text += f"[info][title]SFTP接続情報[/title]"
    text += f"IPアドレス： {login_info['public_ip']}\n"
    text += f"ユーザー名： {login_info['db_user_name']}\n"
    text += f"パスワード： {login_info['kusanagi_password']}[/info][/info]"

    return text


def new_domain_message(domain, name_servers):
    text = f'新規ドメイン{domain} を作成しました。\nCNAME レコードの登録しました\n'
    text += f"ドメインレジストラに以下のネームサーバーを設定してください\n"
    text += "ACMのステータスは発行済みとなったら、コマンド再実行してください\n"
    text += "[info]" + "\n".join(name_servers) + "[/info]"
    return text
