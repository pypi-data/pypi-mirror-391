import time
from typing import Optional, Dict, Any
from .base import BaseSender
from .exceptions import SlackSendError


class SlackSender(BaseSender):
    """Slack/Mattermost webhook sender with SSL support"""

    def __init__(self, webhook_url: str, default_channel: str = 'aims_integrations',
                 default_username: str = 'aims_notifier',
                 default_icon_url: str = None,
                 verify_ssl: bool = True,
                 ssl_cert: Optional[str] = None,
                 logger_instance=None, metrics_instance=None):
        super().__init__(logger_instance, metrics_instance)

        # Check if requests is available
        try:
            import requests
        except ImportError:
            raise ImportError("SlackSender requires requests. Install with: pip install dgsender[tg]")

        self.webhook_url = webhook_url
        self.default_channel = default_channel
        self.default_username = default_username
        self.default_icon_url = default_icon_url
        self.verify_ssl = verify_ssl
        self.ssl_cert = ssl_cert

        # Record initialization metric
        self._record_metric_counter("slack_sender.init")

    def send(self, message: str, channel: str = None, username: str = None,
             icon_url: str = None, attachments: list = None) -> None:
        """
        Send message to Slack/Mattermost
        """
        import requests

        start_time = time.time()
        success = False

        try:
            self._record_metric_counter("slack_sender.send_attempt")

            data = {
                'text': message,
                'username': username or self.default_username,
                'channel': channel or self.default_channel,
            }

            if icon_url or self.default_icon_url:
                data['icon_url'] = icon_url or self.default_icon_url

            if attachments:
                data['attachments'] = attachments
                self._record_metric_gauge("slack_sender.attachments_count", len(attachments))

            # Record message metrics
            self._record_metric_gauge("slack_sender.message_size", len(message))

            # Prepare SSL configuration
            ssl_config = {}
            if not self.verify_ssl:
                ssl_config['verify'] = False
            else:
                ssl_config['verify'] = True

            if self.ssl_cert:
                ssl_config['cert'] = self.ssl_cert

            response = requests.post(
                self.webhook_url,
                json=data,
                headers={'content-type': 'application/json'},
                **ssl_config
            )
            response.raise_for_status()

            success = True
            self._log_success('Slack message sent successfully')

        except requests.RequestException as e:
            self._log_error('Send slack message error', e)
            raise SlackSendError(f"Failed to send slack message: {e}")
        finally:
            duration = time.time() - start_time
            self._record_send_metric("slack", duration, success)
            self._record_metric_timer("slack_sender.send_duration", duration)