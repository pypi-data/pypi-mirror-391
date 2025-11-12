import time
import ssl
from typing import Optional, Dict, Any, List
from .base import BaseSender
from .exceptions import TelegramSendError


class AsyncTelegramSender(BaseSender):
    """Asynchronous Telegram sender with proxy, SSL and custom API support"""

    def __init__(self, token: str, base_url: str = 'https://api.telegram.org/bot',
                 proxy: Optional[str] = None,
                 verify_ssl: bool = True,
                 ssl_context: Optional[ssl.SSLContext] = None,
                 client_cert: Optional[str] = None,
                 client_key: Optional[str] = None,
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
        self.verify_ssl = verify_ssl
        self.ssl_context = ssl_context
        self.client_cert = client_cert
        self.client_key = client_key

        self._record_metric_counter("async_telegram_sender.init")

    def _create_ssl_context(self) -> Optional[ssl.SSLContext]:
        """Create SSL context based on configuration"""
        if not self.verify_ssl:
            # Create context that doesn't verify certificates
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE
            return context
        elif self.ssl_context:
            # Use provided custom SSL context
            return self.ssl_context
        elif self.client_cert and self.client_key:
            # Create context with client certificate
            context = ssl.create_default_context()
            context.load_cert_chain(self.client_cert, self.client_key)
            return context
        return None

    def _create_connector(self) -> 'aiohttp.TCPConnector':
        """Create aiohttp connector with SSL configuration"""
        import aiohttp

        ssl_context = self._create_ssl_context()

        if ssl_context:
            connector = aiohttp.TCPConnector(ssl=ssl_context)
        else:
            connector = aiohttp.TCPConnector(verify_ssl=self.verify_ssl)

        return connector

    async def send(self, message: str, chat_id: int, parse_mode: str = None,
                   disable_web_page_preview: bool = None,
                   disable_notification: bool = None) -> Dict[str, Any]:
        """
        Send telegram message asynchronously
        """
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

            connector = self._create_connector()

            async with aiohttp.ClientSession(connector=connector) as session:
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

    async def send_to_multiple(self, message: str, chat_ids: List[int], **kwargs) -> Dict[int, Any]:
        """
        Send the same message to multiple chat IDs concurrently
        """
        import asyncio

        tasks = {}
        for chat_id in chat_ids:
            task = self.send(message, chat_id, **kwargs)
            tasks[chat_id] = task

        # Send to all chats concurrently
        results = {}
        for chat_id, task in tasks.items():
            try:
                result = await task
                results[chat_id] = {"success": True, "result": result}
            except Exception as e:
                results[chat_id] = {"success": False, "error": str(e)}

        return results

    async def get_me(self) -> Dict[str, Any]:
        """
        Get bot information asynchronously
        """
        import aiohttp

        start_time = time.time()

        try:
            url = f"{self.base_url}{self.token}/getMe"

            connector = self._create_connector()

            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.get(url, proxy=self.proxy) as response:
                    response.raise_for_status()
                    result = await response.json()

                    self._record_metric_counter("async_telegram_sender.get_me_success")
                    return result

        except Exception as e:
            self._record_metric_counter("async_telegram_sender.get_me_failed")
            self._log_error('Get bot info error', e)
            raise TelegramSendError(f"Failed to get bot info: {e}")
        finally:
            duration = time.time() - start_time
            self._record_metric_gauge("async_telegram_sender.get_me_duration", duration)
