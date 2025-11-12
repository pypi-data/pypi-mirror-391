import time
import ssl
from typing import Optional, Dict, Any, List
from .base import BaseSender
from .exceptions import SlackSendError


class AsyncSlackSender(BaseSender):
    """Asynchronous Slack/Mattermost webhook sender with SSL support"""

    def __init__(self, webhook_url: str, default_channel: str = 'aims_integrations',
                 default_username: str = 'aims_notifier',
                 default_icon_url: str = None,
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
            raise ImportError("AsyncSlackSender requires aiohttp. Install with: pip install dgsender[async]")

        self.webhook_url = webhook_url
        self.default_channel = default_channel
        self.default_username = default_username
        self.default_icon_url = default_icon_url
        self.verify_ssl = verify_ssl
        self.ssl_context = ssl_context
        self.client_cert = client_cert
        self.client_key = client_key

        self._record_metric_counter("async_slack_sender.init")

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

    async def send(self, message: str, channel: str = None,
                   username: str = None, icon_url: str = None,
                   attachments: List[Dict] = None) -> None:
        """
        Send slack message asynchronously
        """
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

            if icon_url or self.default_icon_url:
                data['icon_url'] = icon_url or self.default_icon_url

            if attachments:
                data['attachments'] = attachments
                self._record_metric_gauge("async_slack_sender.attachments_count", len(attachments))

            # Record message metrics
            self._record_metric_gauge("async_slack_sender.message_size", len(message))

            connector = self._create_connector()

            async with aiohttp.ClientSession(connector=connector) as session:
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

    async def send_blocks(self, blocks: List[Dict], text: str = None,
                          channel: str = None, username: str = None) -> None:
        """
        Send Slack message with blocks (rich formatting)
        """
        import aiohttp

        start_time = time.time()
        success = False

        try:
            self._record_metric_counter("async_slack_sender.send_blocks_attempt")

            data = {
                'blocks': blocks,
                'username': username or self.default_username,
                'channel': channel or self.default_channel,
            }

            if text:
                data['text'] = text

            # Record message metrics
            self._record_metric_gauge("async_slack_sender.blocks_count", len(blocks))

            connector = self._create_connector()

            async with aiohttp.ClientSession(connector=connector) as session:
                async with session.post(
                        self.webhook_url,
                        json=data,
                        headers={'content-type': 'application/json'}
                ) as response:
                    response.raise_for_status()

                    success = True
                    self._log_success('Async slack blocks sent successfully')

        except Exception as e:
            self._log_error('Async send slack blocks error', e)
            raise SlackSendError(f"Failed to send slack blocks: {e}")
        finally:
            duration = time.time() - start_time
            self._record_send_metric("async_slack_blocks", duration, success)
            self._record_metric_timer("async_slack_sender.send_blocks_duration", duration)
