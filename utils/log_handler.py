import logging

LOGGER_FORMAT = "%(asctime)s:[%(filename)s](%(lineno)s)fn:%(funcName)s %(message)s"
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


class LoggerHander(logging.Logger):
    """カスタマーログ設定"""

    def __init__(
        self,
        name="root",
        log_level="DEBUG",
        file=None,
        logger_format=LOGGER_FORMAT,
        datefmt=DATE_FORMAT,
    ):
        """
        ロガーハンドラーを初期化
        パラメーター
        -------
        name : str
            ロガーの名前
        log_level : str
            ロガーのログレベル
        file : str
            ログファイルへのパス None の場合、ログはファイルに書き込まれない
        logger_format : str
            ログメッセージの形式
        datefmt : str
            ログの日付の形式
        """

        super().__init__(name)
        self.setLevel(log_level)
        formatter = logging.Formatter(fmt=logger_format, datefmt=datefmt)

        if file:
            file_handler = logging.FileHandler(file)
            file_handler.setLevel(log_level)
            file_handler.setFormatter(formatter)
            self.addHandler(file_handler)

        # stdout
        s_handler = logging.StreamHandler()
        s_handler.setLevel(log_level)
        s_handler.setFormatter(formatter)
        self.addHandler(s_handler)
