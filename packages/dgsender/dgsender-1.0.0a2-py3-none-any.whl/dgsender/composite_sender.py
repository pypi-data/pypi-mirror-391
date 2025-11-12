from typing import List, Dict, Any, Optional
import logging
from .base import BaseSender
from .exceptions import DGSenderError


class CompositeSender(BaseSender):
    """
    Composite sender that can send messages through multiple channels
    """

    def __init__(self, senders: List[BaseSender],
                 logger_instance=None, metrics_instance=None):
        super().__init__(logger_instance, metrics_instance)
        self.senders = senders

        # Record initialization metric
        self._record_metric_counter("composite_sender.init", tags={"senders_count": len(senders)})

    def send_all(self, message: str, **kwargs) -> Dict[str, Any]:
        """
        Send message through all configured senders

        Returns:
            Dictionary with results from each sender
        """
        results = {}

        for sender in self.senders:
            sender_name = sender.__class__.__name__
            try:
                self._record_metric_counter("composite_sender.attempt", tags={"sender": sender_name})
                result = sender.send(message, **kwargs)
                results[sender_name] = {"success": True, "result": result}
                self._record_metric_counter("composite_sender.success", tags={"sender": sender_name})
            except Exception as e:
                results[sender_name] = {"success": False, "error": str(e)}
                self._record_metric_counter("composite_sender.failure", tags={"sender": sender_name})
                self._log_error(f"Sender {sender_name} failed", e)

        success_count = sum(1 for r in results.values() if r["success"])
        self._record_metric_gauge("composite_sender.success_count", success_count)
        self._record_metric_gauge("composite_sender.total_senders", len(self.senders))

        return results

    def add_sender(self, sender: BaseSender) -> None:
        """Add a new sender to the composite"""
        self.senders.append(sender)
        self._record_metric_counter("composite_sender.sender_added")

    def remove_sender(self, sender: BaseSender) -> None:
        """Remove a sender from the composite"""
        if sender in self.senders:
            self.senders.remove(sender)
            self._record_metric_counter("composite_sender.sender_removed")