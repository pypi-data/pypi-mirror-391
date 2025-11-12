import asyncio
import time
from typing import List, Optional, Dict, Any
from .base import BaseSender
from .exceptions import EmailSendError


class AsyncEmailSender(BaseSender):
    """Asynchronous email sender"""

    def __init__(self, host: str = "localhost", port: int = 0, use_tls: bool = False,
                 username: str = None, password: str = None, use_ssl: bool = False,
                 logger_instance=None, metrics_instance=None):
        super().__init__(logger_instance, metrics_instance)

        # Check if async mailer is available
        try:
            from .mailer import AsyncMailer
        except ImportError:
            raise ImportError("AsyncEmailSender requires email dependencies. Install with: pip install dgsender[mail]")

        self.host = host
        self.port = port
        self.use_tls = use_tls
        self.username = username
        self.password = password
        self.use_ssl = use_ssl
        self.mailer = AsyncMailer(
            host=host, port=port, use_tls=use_tls,
            usr=username, pwd=password, use_ssl=use_ssl
        )

        self._record_metric_counter("async_email_sender.init", tags={"host": host})

    async def send(self, msg: str, subject: str, to: List[str], cc: List[str] = None,
                   bcc: List[str] = None, from_addr: str = '', charset: str = 'utf-8',
                   is_html: bool = True, attachments: List[str] = None,
                   mimetype: str = None, debug: bool = False) -> None:
        """
        Send email message asynchronously

        Args:
            msg: Message body
            subject: Email subject
            to: List of recipients
            cc: List of CC recipients
            bcc: List of BCC recipients
            from_addr: Sender email address
            charset: Character encoding
            is_html: Whether message is HTML
            attachments: File attachments
            mimetype: MIME type for attachments
            debug: Enable debug mode
        """
        from .mailer import Message

        start_time = time.time()
        success = False

        try:
            self._record_metric_counter("async_email_sender.send_attempt")

            message = Message(
                From=from_addr,
                To=to,
                Cc=cc,
                Bcc=bcc,
                charset=charset
            )
            message.Subject = subject

            if is_html:
                message.Html = msg
            else:
                message.Body = msg

            # Record message metrics
            self._record_metric_gauge("async_email_sender.message_size", len(msg))
            self._record_metric_gauge("async_email_sender.recipients_count", len(to))

            if attachments:
                for file in attachments:
                    try:
                        message.attach(file, mimetype=mimetype, charset=charset)
                        self._record_metric_counter("async_email_sender.attachment_added")
                    except Exception as e:
                        self._log_error(f'Could not attach file: {file}', e)
                        self._record_metric_counter("async_email_sender.attachment_failed")

            await self.mailer.send(message, debug=debug)
            success = True
            self._log_success('Async email sent successfully')

        except Exception as e:
            self._log_error('Error while sending async email', e)
            raise EmailSendError(f"Failed to send async email: {e}")
        finally:
            duration = time.time() - start_time
            self._record_send_metric("async_email", duration, success)
            self._record_metric_timer("async_email_sender.send_duration", duration)

    async def send_multiple(self, messages: List[Dict[str, Any]]) -> List[Any]:
        """
        Send multiple emails concurrently

        Args:
            messages: List of message dictionaries with send parameters

        Returns:
            List of results or exceptions
        """
        tasks = []
        for msg_data in messages:
            task = self.send(**msg_data)
            tasks.append(task)

        # Send all emails concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        return results
