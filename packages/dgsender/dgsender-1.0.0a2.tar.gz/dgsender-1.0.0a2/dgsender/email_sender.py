import socket
import time
from typing import List, Optional, Union
from email.header import Header

from .base import BaseSender
from .exceptions import EmailSendError

try:
    from .mailer import Mailer, Message
except ImportError:
    pass


class MailerContinius(Mailer):
    def __init__(self, host="localhost", port=0, use_tls=False, usr=None, pwd=None,
                 use_ssl=False, use_plain_auth=False, timeout=socket._GLOBAL_DEFAULT_TIMEOUT):
        super().__init__(host, port, use_tls, usr, pwd, use_ssl, use_plain_auth, timeout)
        self.server = None

    def send(self, msg, debug=False):
        if not self.server:
            if self.use_ssl:
                self.server = smtplib.SMTP_SSL(self.host, self.port, timeout=self.timeout)
            else:
                self.server = smtplib.SMTP(self.host, self.port, timeout=self.timeout)

            if debug:
                self.server.set_debuglevel(1)

            if self._usr and self._pwd:
                if self.use_tls is True:
                    self.server.ehlo()
                    self.server.starttls()
                    self.server.ehlo()

                if self.use_plain_auth is True:
                    self.server.esmtp_features["auth"] = "LOGIN PLAIN"

                self.server.login(self._usr, self._pwd)

        if isinstance(msg, Message):
            msg = [msg]

        for m in msg:
            self._send(self.server, m)

    def quit(self):
        if self.server:
            self.server.quit()
            self.server = None


class EmailSender(BaseSender):
    """Email sender with persistent connection support"""

    def __init__(self, host: str = "localhost", port: int = 0, use_tls: bool = False,
                 username: str = None, password: str = None, use_ssl: bool = False,
                 reopen_mail_session: bool = True,
                 logger_instance=None, metrics_instance=None):
        super().__init__(logger_instance, metrics_instance)
        self.host = host
        self.port = port
        self.use_tls = use_tls
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.reopen_mail_session = reopen_mail_session
        self.email_connector = None

        # Record initialization metric
        self._record_metric_counter("email_sender.init", tags={"host": host})

    def send(self, msg: str, subject: str, to: List[str], cc: List[str] = None,
             bcc: List[str] = None, from_addr: str = '', charset: str = 'utf-8',
             is_html: bool = True, attachments: Union[List[str], str] = None,
             mimetype: str = None, debug: bool = False) -> None:
        """
        Send email message
        """
        start_time = time.time()
        success = False

        try:
            self._record_metric_counter("email_sender.send_attempt")

            message = Message(
                From=from_addr,
                To=to,
                Cc=cc,
                Bcc=bcc,
                charset=charset
            )
            message.Subject = Header(subject.encode('utf-8'), 'UTF-8').encode()

            if is_html:
                message.Html = msg
            else:
                message.Body = msg

            # Record message metrics
            self._record_metric_gauge("email_sender.message_size", len(msg))
            self._record_metric_gauge("email_sender.recipients_count", len(to))

            if attachments:
                self._attach_files(message, attachments, mimetype, charset)

            if self.email_connector is None:
                if self.reopen_mail_session:
                    self.email_connector = Mailer(
                        self.host, self.port, self.use_tls,
                        usr=self.username, pwd=self.password
                    )
                else:
                    self.email_connector = MailerContinius(
                        self.host, self.port, self.use_tls,
                        usr=self.username, pwd=self.password
                    )

            self.email_connector.send(message)
            success = True
            self._log_success('Email sent successfully')

        except Exception as e:
            self._log_error('Error while sending email', e)
            self.email_connector = None
            raise EmailSendError(f"Failed to send email: {e}")
        finally:
            duration = time.time() - start_time
            self._record_send_metric("email", duration, success)
            self._record_metric_timer("email_sender.send_duration", duration)

    def _attach_files(self, message: Message, attachments: Union[List[str], str],
                      mimetype: str, charset: str) -> None:
        """Attach files to email message"""
        if isinstance(attachments, list):
            for file in attachments:
                try:
                    message.attach(file, mimetype=mimetype, charset=charset)
                    self._record_metric_counter("email_sender.attachment_added")
                except Exception as e:
                    self._log_error(f'Could not attach file: {file}', e)
                    self._record_metric_counter("email_sender.attachment_failed")
        elif isinstance(attachments, str):
            try:
                message.attach(attachments, mimetype=mimetype, charset=charset)
                self._record_metric_counter("email_sender.attachment_added")
            except Exception as e:
                self._log_error(f'Could not attach file: {attachments}', e)
                self._record_metric_counter("email_sender.attachment_failed")
        else:
            self.logger.warn('Incorrect type of variable attachments')
            self._record_metric_counter("email_sender.attachment_invalid_type")

    def close(self):
        """Close email connection"""
        if self.email_connector and hasattr(self.email_connector, 'quit'):
            self.email_connector.quit()
        self.email_connector = None
        self._record_metric_counter("email_sender.connection_closed")
