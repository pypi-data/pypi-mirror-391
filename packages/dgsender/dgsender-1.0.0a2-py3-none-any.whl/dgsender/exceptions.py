class DGSenderError(Exception):
    """Base exception for dgsender package"""
    pass

class EmailSendError(DGSenderError):
    """Email sending related errors"""
    pass

class TelegramSendError(DGSenderError):
    """Telegram sending related errors"""
    pass

class SlackSendError(DGSenderError):
    """Slack sending related errors"""
    pass

class ZabbixSendError(DGSenderError):
    """Zabbix sending related errors"""
    pass