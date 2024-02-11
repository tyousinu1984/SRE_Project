import sys
sys.path.insert(1, 'wordpress-server-construction-with-kusanagi/coretech_lambda/launching-resources-with-cloudformation')  # NOQA: E402
import boto3
import pytest
from src.utils import notify_message


def test_help_message_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    text = notify_message.help_message()
    print(text)
    print(f"{sys._getframe().f_code.co_name} end")


def test_stack_success_message_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    host = "dev.isdsblog.com"
    login_info = {'kusanagi_password': 'Rpp_iR2M#jZmvyhT', 'basic_auth_user_name': 'dev_isdsblog', 'basic_auth_user_password': 'Mq_efSLBVbrEH7iG', 'wp_admin_name': 'dev_isdsblog_admin',
                  'wp_admin_password': 'np3wXawS7BNGBhYK', 'db_name': 'dev_isdsblog_DB', 'db_root_password': 'eVzHWnx6ek%9AS!m', 'db_user_name': 'dev_isdsblog', 'db_user_password': 'rW2uq%rLfUb#7RhY',
                  "instance_id": "i-066591174f18ae025", "public_ip": "35.78.48.46s"}
    text = notify_message.stack_success_message(login_info, host)
    print(text)
    print(f"{sys._getframe().f_code.co_name} end")


def test_get_direct_chat_room_id_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")
    api_token = "bac2678223bf79f13f41c3a4e250b1be"
    account_id = "5757341"
    id = notify_message.get_direct_chat_room_id(api_token, account_id)
    print(id)

    print(f"{sys._getframe().f_code.co_name} end")
