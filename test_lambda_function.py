import json
import os
import sys

import lambda_function
import pytest
from lambda_function import _HANDLER

current_directory = os.path.dirname(os.path.abspath(__file__))
_CONFIG_FILE_NAME = current_directory + "/env/core_orien_config.json"
_CONFIG_FILE_NAME = _CONFIG_FILE_NAME.replace("\\", "/")

_ACCOUNT_NAME = "orien"
os.environ["ENV_FILE"] = _CONFIG_FILE_NAME
os.environ["ACCOUNT"] = _ACCOUNT_NAME
os.environ["PROFILE_NAME"] = "core_orien"


def test_lambda_handler_Normal001():
    print(f"{sys._getframe().f_code.co_name} start")

    event = {"service": "ec2"}

    lambda_function.lambda_handler(event, "")
    print(f"{sys._getframe().f_code.co_name} end")


def test_lambda_handler_Normal002():
    print(f"{sys._getframe().f_code.co_name} start")

    event = {"service": "elasticache"}

    lambda_function.lambda_handler(event, "")
    print(f"{sys._getframe().f_code.co_name} end")


def test_lambda_handler_Normal003():
    print(f"{sys._getframe().f_code.co_name} start")

    event = {"service": "lambda"}

    lambda_function.lambda_handler(event, "")
    print(f"{sys._getframe().f_code.co_name} end")


def test_lambda_handler_Normal004():
    print(f"{sys._getframe().f_code.co_name} start")

    event = {"service": "rds"}

    lambda_function.lambda_handler(event, "")
    print(f"{sys._getframe().f_code.co_name} end")


def test_lambda_handler_Normal005():
    print(f"{sys._getframe().f_code.co_name} start")

    event = {"service": "targetgroup"}

    lambda_function.lambda_handler(event, "")
    print(f"{sys._getframe().f_code.co_name} end")
