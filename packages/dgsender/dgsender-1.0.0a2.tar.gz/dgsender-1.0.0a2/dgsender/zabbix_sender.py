import time
from typing import Optional, Dict, Any
from .base import BaseSender
from .exceptions import ZabbixSendError


class ZabbixSender(BaseSender):
    """Zabbix sender for monitoring data"""

    def __init__(self, server: str, port: int = 10051,
                 logger_instance=None, metrics_instance=None):
        super().__init__(logger_instance, metrics_instance)

        # Check if divinegift is available
        try:
            import divinegift
        except ImportError:
            raise ImportError("ZabbixSender requires divinegift. Install with: pip install dgsender[zabbix]")

        self.server = server
        self.port = port
        self.zabbix_agent = None

        # Record initialization metric
        self._record_metric_counter("zabbix_sender.init", tags={"server": server})

    def _init_agent(self, **server_conf):
        """Initialize Zabbix agent"""
        if self.zabbix_agent is None:
            from divinegift import zabbix_agent
            config = server_conf or {'server': self.server, 'port': self.port}
            self.zabbix_agent = zabbix_agent.ZabbixAgent(**config)
            self._record_metric_counter("zabbix_sender.agent_initialized")

    def send(self, host: str, key: str, value: Any, **server_conf) -> None:
        """
        Send data to Zabbix
        """
        start_time = time.time()
        success = False

        try:
            self._record_metric_counter("zabbix_sender.send_attempt")

            self._init_agent(**server_conf)
            self.zabbix_agent.send(host, key, value)

            success = True
            self._log_success('Zabbix data sent successfully')

            # Record data metrics
            self._record_metric_gauge("zabbix_sender.value_sent",
                                      float(value) if isinstance(value, (int, float)) else 1)
            self._record_metric_counter("zabbix_sender.send_success", tags={"host": host, "key": key})

        except Exception as e:
            self._record_metric_counter("zabbix_sender.send_failed", tags={"host": host, "key": key})
            self._log_error('Error sending data to Zabbix', e)
            raise ZabbixSendError(f"Failed to send data to Zabbix: {e}")
        finally:
            duration = time.time() - start_time
            self._record_send_metric("zabbix", duration, success)
            self._record_metric_timer("zabbix_sender.send_duration", duration)
