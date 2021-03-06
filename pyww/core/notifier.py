import os

from notify_run import Notify as RemoteNotify
from notifypy import Notify as LocalNotify
from pyww.core.logger import logger


class Notifier(object):
    def __init__(self, remote_notifications=False):
        self._local_notifier = LocalNotify()
        if remote_notifications:
            self._remote_notifier = RemoteNotify()
            logger.info(
                "Registering a new Remote Push Notification (RPN) endpoint")
            remote_notify_info = self._remote_notifier.register()
            self._display_remote_notify_info(str(remote_notify_info))
        else:
            self._remote_notifier = None

    @classmethod
    def _display_remote_notify_info(cls, remote_notify_info):
        if os.name == 'nt':
            # Windows cmd/powershell does not display QR code properly - stripping it off
            remote_notify_info = remote_notify_info[:remote_notify_info.index(
                "Or scan this QR code")]

        logger.info(
            """\n\n****************** REMOTE PUSH NOTIFICATIONS ********************\n
            %s
            \nNOTE: iOS and Safari NOT supported
            \n*****************************************************************\n""",
            remote_notify_info
        )

    def notify(self, title, message, link):
        if self._remote_notifier:
            self._send_remote_notification(title, message, link)
        else:
            self._send_local_notification(title, message)

    def _send_local_notification(self, title, message):
        self._local_notifier.title = title
        self._local_notifier.message = message
        self._local_notifier.send()

    def _send_remote_notification(self, title, message, link):
        self._remote_notifier.send(
            "{title} - {message}".format(title=title, message=message), link)
