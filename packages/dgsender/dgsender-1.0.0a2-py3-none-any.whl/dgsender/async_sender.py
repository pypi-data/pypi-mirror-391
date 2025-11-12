import asyncio
import time
from typing import Optional, Dict, Any, List
from .base import BaseSender
from .exceptions import TelegramSendError, SlackSendError, EmailSendError


class AsyncEmailSender(BaseSender):
    """Asynchronous email sender"""

    def __init__(self, host: str = "localhost", port: int = 0, use_tls: bool = False,
                 username: str = None, password: str = None, use_ssl: bool = False,
                 logger_instance=None, metrics_instance=None):
        super().__init__(logger_instance, metrics_instance)

        # Check if async mailer is available
        try:
            from .mailer import AsyncMailer, Message
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


class AsyncTelegramSender(BaseSender):
    """Asynchronous Telegram sender"""

    def __init__(self, token: str, base_url: str = 'https://api.telegram.org/bot',
                 proxy: Optional[str] = None,
                 logger_instance=None, metrics_instance=None):
        super().__init__(logger_instance, metrics_instance)

        # Check if aiohttp is available
        try:
            import aiohttp
        except ImportError:
            raise ImportError("AsyncTelegramSender requires aiohttp. Install with: pip install dgsender[async]")

        self.token = token
        self.base_url = base_url.rstrip('/')
        self.proxy = proxy

        self._record_metric_counter("async_telegram_sender.init")

    async def send(self, message: str, chat_id: int, parse_mode: str = None,
                   disable_web_page_preview: bool = None,
                   disable_notification: bool = None) -> Dict[str, Any]:
        """Send telegram message asynchronously"""
        import aiohttp

        start_time = time.time()
        success = False

        try:
            self._record_metric_counter("async_telegram_sender.send_attempt")

            url = f"{self.base_url}{self.token}/sendMessage"

            data = {
                'chat_id': chat_id,
                'text': message
            }

            if parse_mode:
                data['parse_mode'] = parse_mode
            if disable_web_page_preview is not None:
                data['disable_web_page_preview'] = disable_web_page_preview
            if disable_notification is not None:
                data['disable_notification'] = disable_notification

            # Record message metrics
            self._record_metric_gauge("async_telegram_sender.message_size", len(message))

            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, proxy=self.proxy) as response:
                    response.raise_for_status()
                    result = await response.json()

                    success = True
                    self._log_success('Async telegram message sent successfully')
                    return result

        except Exception as e:
            self._log_error('Async send telegram message error', e)
            raise TelegramSendError(f"Failed to send telegram message: {e}")
        finally:
            duration = time.time() - start_time
            self._record_send_metric("async_telegram", duration, success)
            self._record_metric_timer("async_telegram_sender.send_duration", duration)


class AsyncSlackSender(BaseSender):
    """Asynchronous Slack sender"""

    def __init__(self, webhook_url: str, default_channel: str = 'aims_integrations',
                 default_username: str = 'aims_notifier',
                 logger_instance=None, metrics_instance=None):
        super().__init__(logger_instance, metrics_instance)

        # Check if aiohttp is available
        try:
            import aiohttp
        except ImportError:
            raise ImportError("AsyncSlackSender requires aiohttp. Install with: pip install dgsender[async]")

        self.webhook_url = webhook_url
        self.default_channel = default_channel
        self.default_username = default_username

        self._record_metric_counter("async_slack_sender.init")

    async def send(self, message: str, channel: str = None,
                   username: str = None) -> None:
        """Send slack message asynchronously"""
        import aiohttp

        start_time = time.time()
        success = False

        try:
            self._record_metric_counter("async_slack_sender.send_attempt")

            data = {
                'text': message,
                'username': username or self.default_username,
                'channel': channel or self.default_channel,
            }

            # Record message metrics
            self._record_metric_gauge("async_slack_sender.message_size", len(message))

            async with aiohttp.ClientSession() as session:
                async with session.post(
                        self.webhook_url,
                        json=data,
                        headers={'content-type': 'application/json'}
                ) as response:
                    response.raise_for_status()

                    success = True
                    self._log_success('Async slack message sent successfully')

        except Exception as e:
            self._log_error('Async send slack message error', e)
            raise SlackSendError(f"Failed to send slack message: {e}")
        finally:
            duration = time.time() - start_time
            self._record_send_metric("async_slack", duration, success)
            self._record_metric_timer("async_slack_sender.send_duration", duration)
