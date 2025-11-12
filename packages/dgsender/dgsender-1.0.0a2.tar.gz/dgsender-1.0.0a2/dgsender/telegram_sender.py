import time
import ssl
from typing import Optional, Dict, Any, Union
from .base import BaseSender
from .exceptions import TelegramSendError


class TelegramSender(BaseSender):
    """Telegram sender with proxy, SSL and custom API support"""

    def __init__(self, token: str, base_url: str = 'https://api.telegram.org/bot',
                 proxy: Optional[Dict[str, str]] = None,
                 verify_ssl: bool = True,
                 ssl_cert: Optional[Union[str, tuple]] = None,
                 logger_instance=None, metrics_instance=None):
        super().__init__(logger_instance, metrics_instance)

        # Check if requests is available
        try:
            import requests
        except ImportError:
            raise ImportError("TelegramSender requires requests. Install with: pip install dgsender[tg]")

        self.token = token
        self.base_url = base_url.rstrip('/')
        self.proxy = proxy
        self.verify_ssl = verify_ssl
        self.ssl_cert = ssl_cert

        # Record initialization metric
        self._record_metric_counter("telegram_sender.init")

    def send(self, message: str, chat_id: int, parse_mode: str = None,
             disable_web_page_preview: bool = None, disable_notification: bool = None,
             reply_to_message_id: int = None) -> Dict[str, Any]:
        """
        Send telegram message
        """
        import requests

        start_time = time.time()
        success = False

        try:
            self._record_metric_counter("telegram_sender.send_attempt")

            url = f"{self.base_url}{self.token}/sendMessage"

            data = {
                'chat_id': chat_id,
                'text': message
            }

            # Optional parameters
            if parse_mode:
                data['parse_mode'] = parse_mode
            if disable_web_page_preview is not None:
                data['disable_web_page_preview'] = disable_web_page_preview
            if disable_notification is not None:
                data['disable_notification'] = disable_notification
            if reply_to_message_id:
                data['reply_to_message_id'] = reply_to_message_id

            # Record message metrics
            self._record_metric_gauge("telegram_sender.message_size", len(message))
            self._record_metric_gauge("telegram_sender.chat_id", chat_id)

            # Prepare SSL configuration
            ssl_config = {}
            if not self.verify_ssl:
                ssl_config['verify'] = False
            else:
                ssl_config['verify'] = True

            if self.ssl_cert:
                ssl_config['cert'] = self.ssl_cert

            response = requests.post(
                url,
                data=data,
                proxies=self.proxy,
                **ssl_config
            )
            response.raise_for_status()

            result = response.json()
            success = True
            self._log_success('Telegram message sent successfully')

            return result

        except requests.RequestException as e:
            self._log_error('Send telegram message error', e)
            raise TelegramSendError(f"Failed to send telegram message: {e}")
        finally:
            duration = time.time() - start_time
            self._record_send_metric("telegram", duration, success)
            self._record_metric_timer("telegram_sender.send_duration", duration)

    def get_me(self) -> Dict[str, Any]:
        """Get bot information"""
        import requests

        start_time = time.time()

        try:
            url = f"{self.base_url}{self.token}/getMe"

            # Prepare SSL configuration
            ssl_config = {}
            if not self.verify_ssl:
                ssl_config['verify'] = False
            else:
                ssl_config['verify'] = True

            if self.ssl_cert:
                ssl_config['cert'] = self.ssl_cert

            response = requests.get(
                url,
                proxies=self.proxy,
                **ssl_config
            )
            response.raise_for_status()

            self._record_metric_counter("telegram_sender.get_me_success")
            return response.json()

        except requests.RequestException as e:
            self._record_metric_counter("telegram_sender.get_me_failed")
            self._log_error('Get bot info error', e)
            raise TelegramSendError(f"Failed to get bot info: {e}")
        finally:
            duration = time.time() - start_time
            self._record_metric_gauge("telegram_sender.get_me_duration", duration)