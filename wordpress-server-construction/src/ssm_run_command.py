import os
import random
import secrets
import sys
import time
import string
import traceback
from src.utils import log_handler

# ロガー初期化
_LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
_logger = log_handler.LoggerHander(log_level=_LOG_LEVEL)


def setup_kusangi_server(ssm, config: dict,
                         host_name: str):
    """Kusanagi サーバーの設定を行う

    Parameters
    ----------
    ssm_client :
        SSMのクライアント
    config : dict
        設定ファイル
    host_hame : str
        対象サーバーのホスト名
    instance_id: str
        対象サーバーのインスタンス ID
    Returns
    -------
    bool
        実行が正常に完了したかどうかを返す。成功していれば True 。    
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")
    t = time.time()
    _commands, login_info = _make_commands(config, host_name)
    print(login_info)
    _document_name = "AWS-RunShellScript"
    _parameters: dict = {
        "commands": _commands,
        "workingDirectory": ["/tmp"],
        "executionTimeout": ["3600"]
    }

    # ---------------------
    # 1. コマンド実行開始
    # ---------------------
    _command_id: str = _send_ssm_command(ssm, _document_name, _parameters)
    if _command_id is False:
        _logger.info("SSM Run Command 実行に失敗")
        return False
    # _logger.info(_res)

    # ここで１５秒程度待たないと、次の待機が失敗する
    time.sleep(15)

    # ---------------------
    # 2. コマンド実行完了まで待機
    # ---------------------
    result: bool = ssm._wait_ssm_command_execution(_command_id)
    _logger.info(f"コマンド実行完了,{result}")
    _logger.info(
        f"{sys._getframe().f_code.co_name} End.Time Cost {time.time()-t}")
    return result, login_info


def _send_ssm_command(ssm, document_name: str,
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

        _command_id = ssm._send_ssm_command(document_name, parameters)

        # エラーにならなかった場合、コマンド ID を返す
        if _command_id is not None:
            return _command_id
        else:
            return False

    except Exception as e:
        _logger.error(f"Error: {sys._getframe().f_code.co_name} ")
        _logger.error(traceback.format_exc())
        return False
    finally:
        _logger.info(f"{sys._getframe().f_code.co_name} End.")


def _generate_password(length: int = 16) -> str:
    """指定した長さのパスワードを生成して返す。
    https://gammasoft.jp/blog/generate-password-by-python/
    https://qiita.com/trsqxyz/items/a5a74d73e5852b84c07c

    Parameters
    ----------
    length : int, optional
        パスワードの長さ, デフォルトでは 16

    Returns
    -------
    str
        パスワード
    """
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")

    # 記号
    _special_chars = '%-#_'

    _uppercase_num = random.randrange(1, 3)
    _digit_num = random.randrange(1, 3)
    _special_char_num = random.randrange(1, 3)
    _lowercase_num = length - (_uppercase_num + _digit_num + _special_char_num)

    passwd = ""

    for _ in range(_uppercase_num):
        passwd += secrets.choice(string.ascii_uppercase)

    for _ in range(_digit_num):
        passwd += secrets.choice(string.digits)

    for _ in range(_special_char_num):
        passwd += secrets.choice(_special_chars)

    for _ in range(_lowercase_num):
        passwd += secrets.choice(string.ascii_lowercase)

    # ランダムに並べ替え
    _random_str_list: list = random.sample(passwd, len(passwd))

    # list -> str
    _final_password = ''.join(_random_str_list)
    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return _final_password


def _make_commands(config: dict, host_name: str):
    """ssmのコマンドを作成

    Parameters
    ----------
    config : dict
        設定ファイル
    host_name : str
        ホスト名

    Returns
    -------
    _commands : list
        実行するコマンド
    login_info : dict
        ログイン情報など
    """
    #  シェルスクリプトの引数を用意
    _logger.info(f"{sys._getframe().f_code.co_name} Start.")

    login_info = {}
    _host_name_without_tld = host_name[0:host_name.rfind(".")]
    _host_name_without_dot = _host_name_without_tld.replace(".", "_")

    _kusanagi_password = _generate_password()

    _basic_auth_user_name = _host_name_without_dot
    _basic_auth_user_password = _generate_password()

    _wp_admin_name = _host_name_without_dot + "_admin"
    _wp_admin_password = _generate_password()

    # データベース名には、3～64文字の文字列を指定してください
    # DBユーザー名には、3～16文字の文字列を指定してください。
    _db_name = _host_name_without_dot + "_DB"
    _db_user_name = _make_db_user_name(_host_name_without_dot)
    _db_root_password = _generate_password()
    _db_user_password = _generate_password()

    _shell_script_url = config["ssm_run_command"]["shell_script"]
    _shell_script_name = _shell_script_url.split("/")[-1]

    # シェルスクリプト実行のコマンドを作成
    _command = "bash {} '{}' '{}' '{}' '{}' '{}' '{}' '{}' '{}' '{}' '{}'".format(
        _shell_script_name, host_name, _db_name, _db_user_name,
        _wp_admin_name, _basic_auth_user_name, _kusanagi_password,
        _db_user_password, _db_root_password,
        _wp_admin_password, _basic_auth_user_password)

    # 事前に実行するコマンドの配列を取得し、その末尾にシェルスクリプト実行コマンドを要素として追加
    _commands: list = config["ssm_run_command"]["pre_exec_commands"]
    _commands.append(_command)

    login_info["kusanagi_password"] = _kusanagi_password
    login_info["basic_auth_user_name"] = _basic_auth_user_name
    login_info["basic_auth_user_password"] = _basic_auth_user_password
    login_info["wp_admin_name"] = _wp_admin_name
    login_info["wp_admin_password"] = _wp_admin_password
    login_info["db_name"] = _db_name
    login_info["db_root_password"] = _db_root_password
    login_info["db_user_name"] = _db_user_name
    login_info["db_user_password"] = _db_user_password

    _logger.info(f"{sys._getframe().f_code.co_name} End.")
    return _commands, login_info


def _make_db_user_name(_host_name_without_dot):
    if len(f"{_host_name_without_dot}") > 16 and "_" in _host_name_without_dot:
        _host_name_without_dot = _host_name_without_dot.split("_")[0]

    if len(f"{_host_name_without_dot}") > 16:
        _host_name_without_dot = _host_name_without_dot[0:16]

    return _host_name_without_dot
