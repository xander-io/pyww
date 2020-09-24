from os import path
from pathlib import Path
from notifypy import Notify as LocalNotify
from notify_run import Notify as RemoteNotify
from .logger import logger


class Notifier(object):
    def __init__(self, remote_notifications=False):
        self._local_notifier = LocalNotify()
        if remote_notifications:
            self._remote_notifier = RemoteNotify()
            logger.info("Registering a new remote push notification endpoint")
            remote_notify_info = self._remote_notifier.register()
            self._display_remote_notify_info(remote_notify_info)
        else:
            self._remote_notifier = None

    def _display_remote_notify_info(self, remote_notify_info):
        logger.info("\n****************** REMOTE PUSH NOTIFICATIONS ********************\n" +
                    str(remote_notify_info))

    def notify(self, title, message, link):
        self._send_local_notification(title, message)
        if self._remote_notifier:
            self._send_remote_notification(title, message, link)

    def _send_local_notification(self, title, message):
        self._local_notifier.title = title
        self._local_notifier.message = message
        self._local_notifier.send()

    def _send_remote_notification(self, title, message, link):
        self._remote_notifier.send(
            "{title} - {message}".format(title=title, message=message), link)
